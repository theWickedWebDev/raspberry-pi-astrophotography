
import ctypes
libc = ctypes.CDLL("libc.so.6")


class Timespec(ctypes.Structure):
    _fields_ = [
        ('tv_sec', ctypes.c_long),
        ('tv_nsec', ctypes.c_long),
    ]


libc.nanosleep.argtypes = [
    ctypes.POINTER(Timespec),
    ctypes.POINTER(Timespec)
]


def nsleep(ns):
    req = Timespec()
    rem = Timespec()

    req.tv_sec = ns // 1_000_000_000
    req.tv_nsec = ns % 1_000_000_000

    while libc.nanosleep(req, rem) == -1:
        req, rem = rem, req
