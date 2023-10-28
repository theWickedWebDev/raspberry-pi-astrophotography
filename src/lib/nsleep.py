import ctypes
import time

_libc = ctypes.CDLL("libc.so.6")


class _Timespec(ctypes.Structure):
    _fields_ = [
        ("tv_sec", ctypes.c_long),
        ("tv_nsec", ctypes.c_long),
    ]


_libc.nanosleep.argtypes = [
    ctypes.POINTER(_Timespec),
    ctypes.POINTER(_Timespec),
]


def nsleep(ns: int):
    req = _Timespec()
    rem = _Timespec()

    req.tv_sec = ns // 1_000_000_000
    req.tv_nsec = ns % 1_000_000_000

    while _libc.nanosleep(req, rem) == -1:
        req, rem = rem, req
