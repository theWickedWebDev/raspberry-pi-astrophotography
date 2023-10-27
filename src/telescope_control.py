from __future__ import annotations
import astropy.units as u
from astropy.coordinates import (
    EarthLocation,
    SkyCoord,
    HADec,
    ICRS,
    get_body,
    solar_system_ephemeris,
)
from astropy.time import Time
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
import numpy as np
from queue import Queue, Empty, Full
from threading import Event, RLock, Thread
import time
from typing import Any, Protocol, TypeAlias

from lib.nsleep import nsleep


_log = logging.getLogger(__name__)

TelescopeOrientation: TypeAlias = tuple[u.Quantity["angle"],
                                        u.Quantity["angle"]]


class StepperController(Protocol):
    def __call__(
        self,
        telescope: TelescopeControl,
        axes: list[StepperAxis],
        actions: list[int],
        /,
    ):
        ...


@dataclass(frozen=True)
class StepperAxis:
    motor_steps: int
    gear_ratio: float
    max_speed: u.Quantity["angle / time"]


@dataclass(frozen=True)
class Config:
    bearing_axis: StepperAxis
    declination_axis: StepperAxis
    motor_controller: StepperController

    location: EarthLocation

    max_plan_length: int = field(default=2)
    # FIXME: Rename this.
    noncritical_sleep_time: u.Quantity["time"] = field(
        default=0.1 * u.second,  # pyright: ignore
    )


def _angle_per_step(axis: StepperAxis) -> u.Quantity[u.rad]:
    return 2 * np.pi / (axis.motor_steps * axis.gear_ratio) * u.rad


def _cancel_on_error(f, cancel: Event):
    def wrapper(*args):
        try:
            f(*args)
        except:
            cancel.set()
            raise

    return wrapper


class Busy(Exception):
    pass


class Target(Protocol):
    def coordinate(self, time: Time, location: EarthLocation) -> SkyCoord:
        ...


@dataclass
class FixedTarget(Target):
    coord: SkyCoord

    def coordinate(self, time: Time, location: EarthLocation):
        return self.coord


@dataclass
class SolarSystemTarget(Target):
    name: str

    def coordinate(self, time: Time, location: EarthLocation):
        with solar_system_ephemeris.set("builtin"):
            return get_body(self.name, time, location)


@dataclass
class _RunControl:
    stop: Event = field(default_factory=Event)
    reset: Event = field(default_factory=Event)
    done: Event = field(default_factory=Event)


@dataclass(frozen=True)
class Segment:
    start: TelescopeOrientation
    end: TelescopeOrientation
    # [deadline (ns), bearing_move (1/0/-1), dec_move (1/0/-1)]
    moves: np.ndarray[Any, np.dtype[np.int64]]


class TelescopeControl:
    _config: Config
    _lock: RLock

    _run_control: _RunControl | None

    _orientation: TelescopeOrientation
    _target: Target | None

    def __init__(
        self,
        config: Config,
        orientation: TelescopeOrientation,
        target: Target | None = None,
    ):
        self._config = config
        self._lock = RLock()

        self._run_control = None

        self._orientation = orientation
        self._target = target

    @property
    def config(self):
        return self._config

    def set_config(self, config: Config):
        """Set the configuration for this telescope"""
        if self.is_running:
            raise Busy("cannot change configuration while running")
        self._config = config

    @property
    def is_running(self):
        return self._run_control is not None

    def get_orientation(self):
        with self._lock:
            return self._orientation

    def set_orientation(self, position: TelescopeOrientation):
        if self.is_running:
            raise Busy("cannot update position while running")

        self._orientation = position

    def get_target(self):
        with self._lock:
            return self._target

    def set_target(self, target: Target):
        with self._lock:
            self._target = target
        self._reset_if_running()

    def start(self):
        if self.is_running:
            raise Busy("already running")

        self._run_control = _RunControl()
        Thread(
            target=_cancel_on_error(self._run, self._run_control.reset),
            args=[self._run_control],
        ).start()

    def stop(self):
        # TODO: Could add a block=True parameter to allow stopping without
        # waiting.  But, then all access to _run_control would need to be made
        # thread-safe so that _run_control could be cleared by.

        if not self._run_control:
            # TODO: Raise an error?
            return

        self._run_control.stop.set()
        self._run_control.done.wait()

    def _run(self, control: _RunControl):
        _log.debug("telescope: starting")
        while not control.stop.is_set():
            with self._lock:
                if not self._target:
                    _log.debug("telescope: no target: waiting")
                    time.sleep(1)
                    continue

            control.reset = Event()
            _log.debug("telescope: running")
            q: Queue[Segment] = Queue(self._config.max_plan_length)

            threads = [
                Thread(
                    target=_cancel_on_error(f, control.reset), args=args, daemon=True
                )
                for f, args in [
                    (self._planner, [q, control.reset]),
                    (self._executor, [q, control.reset]),
                ]
            ]

            for t in threads:
                t.start()

            while any(t.is_alive() for t in threads):
                if control.stop.wait(1):
                    control.reset.set()
                    for t in threads:
                        t.join()
                    break

            time.sleep(0.5)

        _log.debug("telescope: stopping")
        self._run_control = None
        control.done.set()

    def _reset_if_running(self):
        if self._run_control:
            self._run_control.reset.set()

    # TODO: Decide if we want to keep this.  It's convenient for callers (to
    # report positions to Stellarium, for example), but it's not used otherwise.
    def current_skycoord(self):
        with self._lock:
            bearing, dec = self._orientation

        return SkyCoord(
            bearing,
            dec,
            frame=HADec(obstime=Time.now(), location=self._config.location),
        ).transform_to(ICRS)

    def _planner(self, q: Queue[Segment], cancel: Event):
        _log.debug("planner: start")

        axis_speeds = np.array(
            # TODO: Convert from list comprehension to generator
            [
                axis.max_speed.to(u.rad / u.s).value
                for axis in [
                    self._config.bearing_axis,
                    self._config.declination_axis,
                ]
            ]
        )

        planned_to_time = time.time_ns()
        xtrem = 0
        ytrem = 0

        with self._lock:
            planned_to_pos = self._orientation
            target = self._target

        if target is None:
            cancel.set()
            return

        while not cancel.is_set():
            _log.debug("planner: create segment")
            start_ha, start_dec = planned_to_pos

            # FIXME: predict_time_ns doesn't work well with larger values, because
            # we can overshoot.  The offset calculation below needs to adaptively
            # reduce the segment time.  For now, 1 second works well enough.
            predict_time_ns = 1_000_000_000
            predict_dt = predict_time_ns * u.nanosecond  # pyright: ignore
            end_time_ns = planned_to_time + predict_time_ns

            start_time = Time(
                datetime.fromtimestamp(
                    planned_to_time / 1_000_000_000, timezone.utc)
            )
            present = HADec(obstime=start_time, location=self._config.location)
            future = HADec(
                obstime=start_time + predict_dt, location=self._config.location
            )

            pos = SkyCoord(start_ha, start_dec, frame=present)
            fut_tgt = target.coordinate(
                start_time + predict_dt, self._config.location
            ).transform_to(future)

            delta = np.array(_raw_orientation_radians(fut_tgt)) - np.array(
                _raw_orientation_radians(pos)
            )

            start = _raw_orientation_radians(pos)

            times_to_fut_tgt = np.abs(delta) / axis_speeds
            mag = np.linalg.norm(delta)
            dir = delta / mag
            offset = (
                dir
                * mag
                * predict_dt.to(u.second).value
                / np.max(np.append(times_to_fut_tgt, 1))
            )
            end = (start[0] + offset[0], start[1] + offset[1])

            xsteps, x_true_end, xtrem = calc_axis_steps(
                start[0],
                planned_to_time,
                end[0],
                end_time_ns,
                _angle_per_step(self.config.bearing_axis).value,
                xtrem,
            )

            ysteps, y_true_end, ytrem = calc_axis_steps(
                start[1],
                planned_to_time,
                end[1],
                end_time_ns,
                _angle_per_step(self.config.declination_axis).value,
                ytrem,
            )

            end_pos: TelescopeOrientation = x_true_end * u.rad, y_true_end * u.rad
            start_pos = planned_to_pos
            planned_to_pos = end_pos
            planned_to_time = end_time_ns

            moves = combine_moves(xsteps, ysteps)
            if moves.size == 0:
                continue

            segment = Segment(start_pos, end_pos, moves)

            while True:
                if cancel.is_set():
                    break
                try:
                    q.put(segment, timeout=0.5)
                    break
                except Full:
                    pass

        _log.debug("planner: stop")

    def _executor(self, q: Queue[Segment], cancel: Event):
        _log.debug("executor: start")

        while not cancel.is_set():
            segment = None
            while segment is None:
                if cancel.is_set():
                    return
                try:
                    segment = q.get(block=True, timeout=0.1)
                except Empty:
                    # TODO: Notify about starvation.  The planner should stay ahead
                    # of the executor.
                    pass

            try:
                # FIXME: Handle exceptions in `execute`.
                self._execute_segment(segment, cancel)
            finally:
                q.task_done()

        _log.debug("executor: stop")

    # TODO: Give `execute` a more descriptive name.
    def _execute_segment(self, segment: Segment, cancel: Event):
        _log.debug("execute_segment: start")

        # FIXME: Assert position == segment.start

        bearing_axis = self.config.bearing_axis
        dec_axis = self.config.declination_axis

        with self._lock:
            cur_ha, cur_dec = self._orientation

        deadline: int
        bearing_move: int
        dec_move: int
        for deadline, bearing_move, dec_move in segment.moves:
            if cancel.is_set():
                break

            sleep_ns = deadline - time.time_ns()
            if sleep_ns > 0:
                nsleep(sleep_ns)
            else:
                # TODO: Warn that we're running behind.
                pass

            if cancel.is_set():
                break

            self.config.motor_controller(
                self, [bearing_axis, dec_axis], [bearing_move, dec_move]
            )

            cur_ha += bearing_move * _angle_per_step(bearing_axis)
            cur_dec += dec_move * _angle_per_step(dec_axis)

            with self._lock:
                self._orientation = cur_ha, cur_dec  # pyright: ignore

        _log.debug("execute_segment: stop")


def calc_axis_steps(
    start: float,
    start_time: int,
    end: float,
    end_time: int,
    step_size: float,
    time_remainder: int,
) -> tuple[np.ndarray, float, int]:
    """
    Make an array of [deadline, -1/1] for axis movement, and return the last
    calculated value and time (to be used as start, start_time on subsequent
    invocations).
    """

    d = end - start
    dt = end_time - start_time

    adj_start_time = start_time - time_remainder
    adj_dt = end_time - adj_start_time

    steps = abs(d / step_size)
    step_time = adj_dt / steps

    xs = (
        np.arange(adj_start_time + step_time, end_time, step_time)
        .round()
        .astype(np.int64)[:, np.newaxis]
    )
    xs = np.append(xs, np.full_like(xs, int(np.sign(d))), axis=1)

    if xs.size == 0:
        true_end = start
        time_remainder += dt
    else:
        true_end = start + xs.shape[0] * np.sign(d) * step_size
        time_remainder = end_time - xs[-1, 0]

    return xs, true_end, time_remainder


def combine_moves(xsteps: np.ndarray, ysteps: np.ndarray):
    moves = np.concatenate(
        (
            np.insert(xsteps, 2, np.zeros(xsteps.shape[0]), axis=1),
            np.insert(ysteps, 1, np.zeros(ysteps.shape[0]), axis=1),
        ),
        axis=0,
    )
    return moves[moves[:, 0].argsort()]


def _raw_orientation_radians(c: SkyCoord) -> tuple[float, float]:
    ha: u.Quantity["angle"] = c.ha  # pyright: ignore
    dec: u.Quantity["angle"] = c.dec  # pyright: ignore

    return ha.to(u.rad).value, dec.to(u.rad).value
