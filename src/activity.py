from __future__ import annotations

from enum import Enum, auto
from types import TracebackType
from typing import Callable, Protocol, TypeVar


_T = TypeVar("_T")


class Activity:
    _status: ActivityStatus
    _cond: _Condition
    _canceled: bool

    def __init__(self, cond: _Condition):
        self._status = ActivityStatus.PENDING
        self._cond = cond
        self._canceled = False

    def wait_for(
        self,
        pred: Callable[[ActivityStatus], _T],
        timeout: float | None = None,
    ) -> _T:
        with self._cond:
            return self._cond.wait_for(lambda: pred(self._status), timeout)

    def cancel(self):
        with self._cond:
            self._canceled = True
            self._cond.notify_all()

    def __repr__(self):
        return f"Activity({self._status.name})"


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


class _Condition(Protocol):
    def __enter__(self) -> bool:
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
        /,
    ) -> None:
        ...

    def wait_for(self, predicate: Callable[[], _T], timeout: float | None = ...) -> _T:
        ...

    def notify_all(self) -> None:
        ...
