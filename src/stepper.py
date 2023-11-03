from __future__ import annotations

from dataclasses import dataclass
import logging
from enum import Enum, IntEnum, auto
import math
from queue import Queue
from threading import Condition, Lock, Thread
import time
from typing import Callable, Protocol, TypeAlias, TypeVar
from typing_extensions import assert_never

import numpy as np

from .lib.nsleep import nsleep
from .motion import pulse_times_trapz, travel_linaccel, trapz_intercept_info

_log = logging.Logger(__name__)


@dataclass(frozen=True)
class StepperConfig:
    min_sleep_ns: int
    max_speed: float  # steps/s
    max_accel: float  # steps/s/s
    max_decel: float  # steps/s/s


class _Direction(IntEnum):
    FWD = 1
    NOP = 0
    REV = -1


class ActivityStatus(Enum):
    PENDING = auto()

    ACTIVE = auto()
    COMPLETE = auto()

    ABORTING = auto()
    ABORTED = auto()

    def running(self):
        return self in [ActivityStatus.ACTIVE, ActivityStatus.ABORTING]

    def done(self):
        return self in [ActivityStatus.COMPLETE, ActivityStatus.ABORTED]


@dataclass
class _Intercept:
    target: int
    target_velocity: float
    final_velocity: float


@dataclass
class _RunConstant:
    velocity: float
    deadline_ns: int


# TODO: Rename to _Noop?  Maybe it could be eliminated?
@dataclass
class _Idle:
    pass


@dataclass
class _Stop:
    pass


_Goal: TypeAlias = _Intercept | _RunConstant | _Idle | _Stop


_T = TypeVar("_T")


class Activity:
    _goal: _Goal
    _status: ActivityStatus
    _cond: Condition
    _canceled: bool

    def __init__(self, goal: _Goal, cond: Condition):
        self._goal = goal
        self._status = ActivityStatus.PENDING
        self._cond = cond
        self._canceled = False

    def wait_for(
        self, pred: Callable[[ActivityStatus], _T], timeout: float | None = None
    ) -> _T:
        with self._cond:
            return self._cond.wait_for(lambda: pred(self._status), timeout)

    def cancel(self):
        with self._cond:
            self._canceled = True
            self._cond.notify_all()

    def __repr__(self):
        return f"Activity({self._goal!r}, {self._status.name})"


_MotionQueue: TypeAlias = Queue[tuple[int, _Direction] | Activity]


@dataclass
class _RunState:
    plan_thread: Thread
    run_thread: Thread


@dataclass
class _PlanContext:
    commit_pos: int
    commit_vel: float
    commit_deadline: int


class StateFn(Protocol):
    def __call__(
        self, stepper: Stepper, motion: _MotionQueue, ctx: _PlanContext
    ) -> StateFn | None:
        ...


class Stepper:
    _config: StepperConfig
    _position: int
    _velocity: float

    _lock: Lock
    _run_state: _RunState | None
    _activities: Queue[Activity]
    _activity_fallback_cond: Condition

    def __init__(
        self,
        config: StepperConfig,
        position: int = 0,
        velocity: float = 0,
    ):
        self._config = config
        self._position = position
        self._velocity = velocity

        self._lock = Lock()
        self._run_state = None
        self._activities = Queue()
        self._activity_fallback_cond = Condition()

    @property
    def position(self):
        with self._lock:
            return self._position

    def goto(
        self,
        target: int,
        final_velocity: float = 0,
        cond: Condition | None = None,
    ):
        return self._put_activity(_Intercept(target, 0, final_velocity), cond)

    def idle(self, cond: Condition | None = None):
        return self._put_activity(_Idle(), cond)

    def intercept(
        self,
        target: int,
        target_velocity: float,
        final_velocity: float | None = None,
        cond: Condition | None = None,
    ):
        if final_velocity is None:
            final_velocity = target_velocity
        return self._put_activity(
            _Intercept(target, target_velocity, final_velocity), cond
        )

    def run_constant(
        self,
        velocity: float,
        deadline_ns: int,
        cond: Condition | None = None,
    ):
        return self._put_activity(_RunConstant(velocity, deadline_ns), cond)

    def _put_activity(self, goal: _Goal, cond: Condition | None) -> Activity:
        activity = Activity(goal, cond or self._activity_fallback_cond)
        self._activities.put(activity)
        return activity

    def start(self):
        with self._lock:
            if self._run_state is not None:
                return

            # TODO: Make plan ahead steps configurable
            motion: _MotionQueue = Queue(maxsize=10)

            run_state = _RunState(
                plan_thread=Thread(target=self._plan, args=[motion]),
                run_thread=Thread(target=self._move, args=[motion]),
            )
            self._run_state = run_state

            for t in [run_state.plan_thread, run_state.run_thread]:
                t.start()

    # TODO: Should start/stop take a Condition and return an Activity?
    def stop(self, timeout: float | None = None):
        deadline = None
        if timeout is not None:
            deadline = time.time() + timeout

        with self._lock:
            run_state = self._run_state
            if run_state is None:
                return

        self._put_activity(_Stop(), None).wait_for(ActivityStatus.done)

        for t in [run_state.plan_thread, run_state.run_thread]:
            t.join(deadline - time.time() if deadline is not None else None)

        with self._lock:
            self._run_state = None

    def _plan(self, motion: _MotionQueue):
        with self._lock:
            ctx = _PlanContext(
                self._position,
                self._velocity,
                time.time_ns(),
            )

        statefn = _plan_dispatch
        while statefn is not None:
            statefn = statefn(self, motion, ctx)

    def _move(self, motion: _MotionQueue):
        while True:
            item = motion.get()
            if isinstance(item, Activity):
                with item._cond:
                    match item._status:
                        case ActivityStatus.ABORTING:
                            item._status = ActivityStatus.ABORTED
                        case ActivityStatus.ACTIVE:
                            item._status = ActivityStatus.COMPLETE
                        case _:
                            assert (
                                False
                            ), f"unexpected Activity status: {item._status} on {item._goal}"

                    item._cond.notify_all()

                motion.task_done()
                if isinstance(item._goal, _Stop):
                    return
                continue

            try:
                deadline, d = item
                now = time.time_ns()

                sleep_ns = deadline - now
                if sleep_ns < self._config.min_sleep_ns:
                    # FIXME: Better telemetry
                    _log.warn(f"running behind: {sleep_ns}")
                    deadline = now + self._config.min_sleep_ns

                nsleep(sleep_ns)

                with self._lock:
                    if d != _Direction.NOP:
                        # FIXME: Actually pulse the motor.
                        pass
                    self._position += d
                    # FIXME: Calculate velocity
                    self._velocity = 0
            finally:
                motion.task_done()


def _plan_dispatch(stepper: Stepper, motion: _MotionQueue, ctx: _PlanContext):
    activity = stepper._activities.get()
    with activity._cond:
        assert activity._status == ActivityStatus.PENDING

    match activity._goal:
        case _Idle() | _Stop() as g:
            with activity._cond:
                activity._status = ActivityStatus.ACTIVE
                activity._cond.notify_all()
            motion.put(activity)
            if isinstance(g, _Stop):
                return None
            return _plan_dispatch
        case _Intercept(_):
            return _plan_intercept(activity)
        case _RunConstant(_):
            return _plan_run_constant(activity)
        case _:
            assert_never(activity._goal)


def _plan_intercept(activity: Activity) -> StateFn:
    assert isinstance(activity._goal, _Intercept)
    goal = activity._goal

    def plan_intercept(stepper: Stepper, motion: _MotionQueue, ctx: _PlanContext):
        with activity._cond:
            assert activity._status == ActivityStatus.PENDING

            activity._status = ActivityStatus.ACTIVE
            activity._cond.notify_all()

        cfg = stepper._config

        now = time.time_ns()
        # TODO: Need to incorporate Config.min_sleep_ns?
        start_ns = max(ctx.commit_deadline, now)
        t0 = (start_ns - now) / 1_000_000_000
        target_t0 = goal.target + t0 * goal.target_velocity

        scratch_delta = target_t0 - ctx.commit_pos

        a_in = math.copysign(cfg.max_accel, scratch_delta)
        a_out = -math.copysign(cfg.max_decel, scratch_delta)

        info = trapz_intercept_info(
            cfg.max_speed,
            a_in,
            a_out,
            ctx.commit_pos,
            ctx.commit_vel,
            goal.final_velocity,
            target_t0,
            goal.target_velocity,
        )

        delta = round(info["p_f"]) - ctx.commit_pos
        if delta == 0:
            motion.put(activity)
            return _plan_dispatch

        dir = _Direction.FWD if delta > 0 else _Direction.REV
        deadlines = (
            start_ns
            + pulse_times_trapz(
                ctx.commit_vel,
                goal.final_velocity,
                info["v_c"],
                a_in,
                a_out,
                delta,
            )
            * 1_000_000_000
        ).astype(np.int64)

        velocities = np.empty_like(deadlines, dtype=np.float64)
        velocities[0] = ctx.commit_vel
        velocities[1:] = int(dir) * 1_000_000_000 / (deadlines[1:] - deadlines[:-1])

        for deadline, velocity in zip(deadlines, velocities):
            with activity._cond:
                if activity._canceled:
                    return _plan_abort(activity)

            ctx.commit_deadline = deadline
            ctx.commit_pos += dir
            ctx.commit_vel = velocity
            motion.put((deadline, dir))
        else:
            motion.put(activity)
            return _plan_dispatch

    return plan_intercept


def _plan_run_constant(activity: Activity) -> StateFn:
    assert isinstance(activity._goal, _RunConstant)
    goal = activity._goal

    def plan_run_constant(stepper: Stepper, motion: _MotionQueue, ctx: _PlanContext):
        with activity._cond:
            assert activity._status == ActivityStatus.PENDING
            activity._status = ActivityStatus.ACTIVE
            activity._cond.notify_all()

        if goal.velocity == 0:
            if ctx.commit_deadline < goal.deadline_ns:
                motion.put((goal.deadline_ns, _Direction.NOP))
            motion.put(activity)
            return _plan_dispatch

        # TODO: Deal with quantization errors (should be pretty small)
        interval = abs(1_000_000_000 / goal.velocity)
        dir = _Direction.FWD if goal.velocity > 0 else _Direction.REV

        while True:
            with activity._cond:
                if activity._canceled:
                    return _plan_abort(activity)

            deadline = round(ctx.commit_deadline + interval)
            if deadline > goal.deadline_ns:
                if ctx.commit_deadline < goal.deadline_ns:
                    motion.put((goal.deadline_ns, _Direction.NOP))
                motion.put(activity)
                return _plan_dispatch

            ctx.commit_deadline = deadline
            ctx.commit_pos += dir
            ctx.commit_vel = goal.velocity
            motion.put((deadline, dir))

    return plan_run_constant


def _plan_abort(activity: Activity) -> StateFn:
    def plan_abort(stepper: Stepper, motion: _MotionQueue, ctx: _PlanContext):
        with activity._cond:
            activity._status = ActivityStatus.ABORTING
            activity._cond.notify_all()

        if ctx.commit_vel == 0 or ctx.commit_deadline is None:
            return _plan_dispatch

        dir = _Direction.FWD if ctx.commit_vel > 0 else _Direction.REV
        steps = np.ceil(travel_linaccel(ctx.commit_vel, 0, -stepper._config.max_decel))
        cfg = stepper._config
        deadlines = (
            ctx.commit_deadline
            + pulse_times_trapz(
                ctx.commit_vel,
                0,
                cfg.max_speed,
                cfg.max_accel,
                -cfg.max_decel,
                steps,
            )
            * 1_000_000_000
        ).astype(np.int64)

        velocities = np.empty_like(deadlines, dtype=np.float64)
        velocities[0] = ctx.commit_vel
        velocities[1:] = (
            (1 if dir == _Direction.FWD else -1)
            * 1_000_000_000
            / (deadlines[1:] - deadlines[:-1])
        )

        for deadline, velocity in zip(deadlines, velocities):
            ctx.commit_deadline = deadline
            ctx.commit_pos += dir
            ctx.commit_vel = velocity
            motion.put((deadline, dir))
        else:
            motion.put(activity)
            return _plan_dispatch

    return plan_abort
