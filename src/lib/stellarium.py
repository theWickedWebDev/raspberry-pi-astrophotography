from __future__ import annotations
import math
from socket import socket
import socketserver
import struct
from threading import Thread
import time

from astropy.coordinates import ICRS, SkyCoord
import astropy.units as u

import telescope_control as tc


def decode_ra(x: int):
    """Convert Stellarium wire RA value to fractional seconds"""
    return (x % 0xFFFFFFFF) / 0xFFFFFFFF * 86_400


def decode_dec(x: int):
    """Convert Stellarium wire DEC value to radians"""
    return x / 0x40000000 * math.pi / 2


def encode_ra(x: float):
    """Convert RA (fractional seconds) to Stellarium wire format"""
    return round((float(x) % 86_400) / 86_400 * 0xFFFFFFFF)


def encode_dec(x: float):
    """Convert DEC (radians) to Stellarium wire format"""
    return int(x * 2 / math.pi * 0x40000000)


class StellariumTCPHandler(socketserver.BaseRequestHandler):
    server: StellariumTCPServer

    def handle(self):
        client = self.request
        Thread(
            target=_report_position_loop,
            args=[client, self.server.telescope],
            daemon=True,
        ).start()
        while True:
            if not _read_target(client, self.server.telescope):
                time.sleep(0.1)


class StellariumTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

    telescope: tc.TelescopeControl

    def __init__(
        self,
        server_address: socketserver._AfInetAddress,
        telescope: tc.TelescopeControl,
        RequestHandlerClass=StellariumTCPHandler,
        bind_and_activate=True,
    ):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.telescope = telescope


def _report_position_loop(client: socket, telescope: tc.TelescopeControl):
    while True:
        pos = telescope.current_skycoord()
        _report_position(client, pos)
        time.sleep(0.5)


def _report_position(client: socket, pos: SkyCoord):
    # FIXME: Send a real time value
    t_raw = 0

    ra: float = pos.ra.to(u.hourangle) / (24 * u.hourangle) * 86_400  # pyright: ignore
    dec: float = pos.dec.to(u.rad).value  # pyright: ignore

    client.send(
        struct.pack(
            "<hhQLll",
            24,
            0,
            t_raw,
            encode_ra(ra),
            encode_dec(dec),
            0,
        )
    )


def _read_target(client: socket, telescope: tc.TelescopeControl):
    # Read msg length and type
    header = client.recv(4)
    if not header:
        return False

    msglen, msgtype = struct.unpack("<hh", header)

    # The protocol only defines one message type: 0
    assert msgtype == 0
    # Read the rest of the message (don't include the header count)
    body = client.recv(msglen - 4)

    # Unpack raw data
    _, ra_raw, dec_raw = struct.unpack("<QLl", body)
    # TODO: Use the time given by Stellarium for something?

    coord = SkyCoord(
        (decode_ra(ra_raw) / 3600) * u.hourangle,  # pyright: ignore
        decode_dec(dec_raw) * u.rad,
        frame=ICRS,
    )

    telescope.set_target(tc.FixedTarget(coord))

    return True
