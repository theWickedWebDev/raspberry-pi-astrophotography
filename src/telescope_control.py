from __future__ import annotations
import functools
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
import multiprocessing as mp
import multiprocessing.connection as mpc
import multiprocessing.synchronize as mps
import numpy as np
from queue import Queue, Empty, Full
from threading import Event, Lock, Thread
import time
import trio
from typing import Any, Protocol, TypeAlias

from lib.nsleep import nsleep

_log = logging.getLogger(__name__)

TelescopeOrientation: TypeAlias = tuple[u.Quantity["angle"], u.Quantity["angle"]]


class StepperController(Protocol):
    def __call__(
        self,
        config: Config,
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


@dataclass(frozen=True)
class Segment:
    start: TelescopeOrientation
    end: TelescopeOrientation
    # [deadline (ns), bearing_move (1/0/-1), dec_move (1/0/-1)]
    moves: np.ndarray[Any, np.dtype[np.int64]]


class TelescopeControl:
    def __init__(
        self,
        config: Config,
        orientation: TelescopeOrientation,
        target: Target | None = None,
    ):
        self._config = config

        self._conn = None

        self._orientation = orientation
        self._target = target

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config: Config):
        self._config = config
        if self._conn:
            self._conn.send(SetConfig(config))

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, orientation: TelescopeOrientation):
        self._orientation = orientation
        if self._conn:
            self._conn.send(SetOrientation(orientation))

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target: Target):
        self._target = target
        if self._conn:
            self._conn.send(SetTarget(target))

    def current_skycoord(self):
        bearing, dec = self._orientation

        return SkyCoord(
            bearing,
            dec,
            frame=HADec(obstime=Time.now(), location=self._config.location),
        ).transform_to(ICRS)

    def calibrate(self, target: Target, track: bool = True):
        coord = target.coordinate(Time.now(), self.config.location)
        tcoord = coord.transform_to(
            HADec(obstime=Time.now(), location=self.config.location)
        )

        o: TelescopeOrientation = (tcoord.ha, tcoord.dec)  # pyright: ignore
        self.orientation = o
        if track:
            self.target = target

    async def run(self):
        conn, child_conn = mp.Pipe()
        self._conn = conn
        stop = mp.Event()

        async with trio.open_nursery() as n:
            n.start_soon(
                functools.partial(
                    trio.to_thread.run_sync,
                    self._run_multiprocess,
                    conn,
                    child_conn,
                    stop,
                )
            )

            try:
                await trio.sleep_forever()
            except:
                stop.set()

    def _run_multiprocess(
        self,
        conn: mpc.PipeConnection,
        child_conn: mpc.PipeConnection,
        stop: mps.Event,
    ):
        state = State(self.config, self.orientation, self.target)
        proc = mp.Process(
            target=_control_supervisor, args=[state, child_conn], daemon=True
        )
        proc.start()

        while not stop.is_set():
            if conn.poll(1):
                msg: OutputMessage = conn.recv()
                match msg:
                    case PublishOrientation(orientation):

                        def update():
                            self._orientation = orientation

                        trio.from_thread.run_sync(update)
                    case PublishTarget(target):

                        def update():
                            self._target = target

                        trio.from_thread.run_sync(update)
                    case _:
                        print(f"unhandled message: {msg}")

        _log.debug("stopping")
        conn.send(Stop())
        try:
            proc.join(5)
        except:
            _log.error("timed out waiting for telescope control to stop")
            proc.kill()


@dataclass
class SetTarget:
    target: Target


@dataclass
class SetOrientation:
    orientation: TelescopeOrientation


@dataclass
class SetConfig:
    config: Config


@dataclass
class PublishTarget:
    target: Target


@dataclass
class PublishOrientation:
    orientation: TelescopeOrientation


@dataclass
class Stop:
    pass


InputMessage: TypeAlias = SetTarget | SetOrientation | SetConfig | Stop
OutputMessage: TypeAlias = PublishTarget | PublishOrientation


@dataclass
class State:
    config: Config
    orientation: TelescopeOrientation
    target: Target | None
    lock: Lock = field(default_factory=Lock)


def _control_supervisor(state: State, conn: mpc.PipeConnection):
    stop = Event()

    _log.debug("telescope: starting")
    while not stop.is_set():
        reset = Event()
        idle = Event()

        _log.debug("telescope: running")
        q: Queue[Segment] = Queue(state.config.max_plan_length)

        # TODO: It seems awkward that _state_reader is created separately, but
        # it needs to wait for idle to be set to update some properties on
        # `state`.  So for now, this is the best we can do.
        state_thread = Thread(
            target=_state_reader, args=[state, conn, reset, idle, stop]
        )
        state_thread.start()

        threads = [
            Thread(target=_cancel_on_error(f, reset), args=args, daemon=True)
            for f, args in [
                (_state_publisher, [state, conn, reset]),
                (_planner, [state, q, reset]),
                (_executor, [state, q, reset]),
            ]
        ]

        for t in threads:
            t.start()

        while any(t.is_alive() for t in threads):
            if stop.wait(1):
                reset.set()
                for t in threads:
                    t.join()
                break

        idle.set()
        state_thread.join()

    _log.debug("telescope: stopping")


def _state_reader(
    state: State, conn: mpc.PipeConnection, reset: Event, idle: Event, stop: Event
):
    def reset_and_wait():
        reset.set()
        idle.wait()

    while not reset.is_set() and not stop.is_set():
        if conn.poll(1):
            msg: InputMessage = conn.recv()
            match msg:
                case Stop():
                    stop.set()
                case SetTarget(target):
                    reset_and_wait()
                    state.target = target
                case SetOrientation(orientation):
                    reset_and_wait()
                    state.orientation = orientation
                case SetConfig(config):
                    reset_and_wait()
                    state.config = config
                case _:
                    print(f"unhandled msg: {msg}")


def _state_publisher(state: State, conn: mpc.PipeConnection, cancel: Event):
    prev_orientation = None

    # TODO: Configurable interval
    while True:
        try:
            if cancel.wait(0.5):
                break
        except Exception as e:
            print(type(e), e)

        with state.lock:
            orientation = state.orientation
        if orientation is not prev_orientation:
            prev_orientation = orientation
            conn.send(PublishOrientation(orientation))


def _planner(state: State, q: Queue[Segment], cancel: Event):
    if state.target is None:
        return

    _log.debug("planner: start")

    axis_speeds = np.array(
        [
            axis.max_speed.to(u.rad / u.s).value
            for axis in [
                state.config.bearing_axis,
                state.config.declination_axis,
            ]
        ]
    )

    planned_to_time = time.time_ns()
    xtrem = 0
    ytrem = 0

    with state.lock:
        planned_to_pos = state.orientation
        target = state.target

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
            datetime.fromtimestamp(planned_to_time / 1_000_000_000, timezone.utc)
        )
        present = HADec(obstime=start_time, location=state.config.location)
        future = HADec(obstime=start_time + predict_dt, location=state.config.location)

        pos = SkyCoord(start_ha, start_dec, frame=present)
        fut_tgt = target.coordinate(
            start_time + predict_dt, state.config.location
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
            _angle_per_step(state.config.bearing_axis).value,
            xtrem,
        )

        ysteps, y_true_end, ytrem = calc_axis_steps(
            start[1],
            planned_to_time,
            end[1],
            end_time_ns,
            _angle_per_step(state.config.declination_axis).value,
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


def _executor(state: State, q: Queue[Segment], cancel: Event):
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
            _execute_segment(state, segment, cancel)
        finally:
            q.task_done()

    _log.debug("executor: stop")


def _execute_segment(state: State, segment: Segment, cancel: Event):
    _log.debug("execute_segment: start")

    bearing_axis = state.config.bearing_axis
    dec_axis = state.config.declination_axis

    with state.lock:
        cur_ha, cur_dec = state.orientation

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

        state.config.motor_controller(
            state.config, [bearing_axis, dec_axis], [bearing_move, dec_move]
        )

        cur_ha += bearing_move * _angle_per_step(bearing_axis)
        cur_dec += dec_move * _angle_per_step(dec_axis)

        with state.lock:
            state.orientation = cur_ha, cur_dec  # pyright: ignore

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
