import astropy.units as u
from astropy.coordinates import EarthLocation, SkyCoord, HADec, ICRS
from astropy.time import Time
import numpy as np
from socket import socket
import socketserver
import struct
import threading
import time

from nsleep import nsleep
import stellarium_wire as wire

stephen_house = EarthLocation(
    lat=42.8164989*u.deg,
    lon=-71.0638871*u.deg,
    height=52.32*u.m,
)

position_lock = threading.Lock()

position = 0*u.hourangle, 0*u.deg, stephen_house

def current_skycoord():
    return SkyCoord(
        position[0],
        position[1],
        frame=HADec(obstime=Time.now(), location=position[2]),
    ).transform_to(ICRS)

# By default, autoguide (maybe change this)
target = current_skycoord()
print(target)

HA_MOTOR_STEPS = 200
HA_GEAR_RATIO = 4 * 4 * 4 * 4
HA_ANGLE_PER_STEP = (2 * np.pi / (HA_MOTOR_STEPS * HA_GEAR_RATIO)) * u.rad
HA_MAX_SPEED = 60 * u.deg / u.second

print(HA_ANGLE_PER_STEP.to(u.deg) / (5.4 * u.deg) * 6000)

DEC_MOTOR_STEPS = 800
DEC_GEAR_RATIO = 4 * 4
DEC_ANGLE_PER_STEP = (2 * np.pi / (DEC_MOTOR_STEPS * DEC_GEAR_RATIO)) * u.rad
DEC_MAX_SPEED = 10 * u.deg / u.second

def report_position_loop(client: socket):
    while True:
        with position_lock:
            pos = current_skycoord()
        
        report_position(client, pos)
        time.sleep(0.5)

def report_position(client: socket, pos: SkyCoord):
    # FIXME: Send a real time value
    t_raw = 0
    client.send(struct.pack(
        '<hhQLll', 24, 0,
        t_raw,
        wire.encode_ra(pos.ra.to(u.hourangle) / (24*u.hourangle) * 86_400),
        wire.encode_dec(pos.dec.to(u.rad).value),
        0))

def read_target(client):
    # Read msg length and type
    header = client.recv(4)
    if not header:
        return False

    msglen, msgtype, = struct.unpack('<hh', header)
    # The protocol only defines one message type: 0
    assert msgtype == 0
    # Read the rest of the message (don't include the header count)
    body = client.recv(msglen - 4)

    # Unpack raw data
    _, ra_raw, dec_raw = struct.unpack('<QLl', body)
    # TODO: Use the time given by Stellarium for something?

    new_target = SkyCoord(
        wire.decode_ra(ra_raw) / 3600 * u.hourangle,
        wire.decode_dec(dec_raw) * u.rad,
        frame=ICRS,
    )

    with position_lock:
        global target
        target = new_target

    return True

class StellariumTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        client = self.request
        threading.Thread(target=report_position_loop, args=[client]).start()
        while True:
            read_target(client)
            time.sleep(0.1)


def guide_loop():
    global position

    # FIXME: Add exit condition.
    while True:
        with position_lock:
            tgt = target
            cur_ha, cur_dec, cur_loc = position

        start = time.time_ns()
        present = HADec(obstime=Time.now(), location=cur_loc)
        predict_dt = 1 * u.second
        future = HADec(obstime=Time.now() + predict_dt, location=cur_loc)
        
        pos = SkyCoord(cur_ha, cur_dec, frame=present)
        now_tgt = tgt.transform_to(present)

        # Update HA/DEC, if needed.
        dha = now_tgt.ha - pos.ha
        ddec = now_tgt.dec - pos.dec

        next_ha = cur_ha
        if np.abs(dha) > HA_ANGLE_PER_STEP:
            next_ha = cur_ha + np.copysign(HA_ANGLE_PER_STEP, dha)

        next_dec = cur_dec
        if np.abs(ddec) > DEC_ANGLE_PER_STEP:
            next_dec = cur_dec + np.copysign(DEC_ANGLE_PER_STEP, ddec)

        # Maybe someday we'll be on a boat.
        next_loc = cur_loc

        with position_lock:
            position = next_ha, next_dec, next_loc

        # Figure out how long to sleep.
        fut_tgt = tgt.transform_to(future)
        # print(fut_tgt.ha, fut_tgt.dec)

        newpos = SkyCoord(next_ha, next_dec, frame=present)

        # ha "velocity" in radians/sec
        ha_vel = (fut_tgt.ha - newpos.ha).to(u.rad) / predict_dt
        ha_vel_clamped = np.copysign(
            min(HA_MAX_SPEED, np.abs(ha_vel)),
            ha_vel,
        )
        ha_sps = np.abs(ha_vel_clamped / HA_ANGLE_PER_STEP)
        ha_tts = 1 / ha_sps

        dec_vel = (fut_tgt.dec - newpos.dec).to(u.rad) / predict_dt
        dec_vel_clamped = np.copysign(
            min(DEC_MAX_SPEED, np.abs(dec_vel)),
            dec_vel,
        )
        dec_sps = np.abs(dec_vel_clamped / DEC_ANGLE_PER_STEP)
        dec_tts = 1 / dec_sps

        tts = min(ha_tts, dec_tts)
        #print("ha_vel_clamped: ", ha_vel_clamped)
        deadline = start + tts.to(u.nanosecond).value
        nsleep(int(deadline) - time.time_ns())


if __name__ == "__main__":
    threading.Thread(target=guide_loop, daemon=True).start()

    addr = "0.0.0.0", 10001
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(addr, StellariumTCPHandler) as server:
        server.serve_forever()
