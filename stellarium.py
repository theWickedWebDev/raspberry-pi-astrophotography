import datetime
import math
import socket
import struct
import requests
import convert
import json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
port = 10001
s.bind(("0.0.0.0", port))
s.listen(5)

client, _ = s.accept()

while True:
    # Read msg length and type
    header = client.recv(4)
    if not header:
        break

    msglen, msgtype, = struct.unpack('<hh', header)
    # The protocol only defines one message type: 0
    assert msgtype == 0
    # Read the rest of the message (don't include the header count)
    body = client.recv(msglen - 4)

    # Unpack raw data
    t_raw, ra_raw, dec_raw = struct.unpack('<QLl', body)

    # Convert ra_raw to fractional seconds
    ra = (ra_raw % 0x100000000) / 0x100000000 * 86400
    # Convert dec_raw to radians
    dec = dec_raw / 0x40000000 * math.pi / 2

    # Formatting/display from here on
    h = int(ra // 3600)
    m = int((ra - h * 3600) // 60)
    s = int(ra % 60)
    us = int((ra % 1) * 1_000_000)
    ra_dt = datetime.time(h, m, s, us)

    # print(f"RA:  {ra_dt.strftime('%Hh%Mm%S.%f')}")
    # print(convert.HMS2deg(ra_dt))
    # print(ra_dt.strftime('%H %M %S.%f'))
    raDecimalDeg = convert.HMS2deg(ra_dt.strftime('%H %M %S.%f'))
    raRadians = raDecimalDeg * math.pi / 180

    print(f"Degrees => RA:  {raDecimalDeg}    DEC: {math.degrees(dec)}")
    print(f"")
    print(f"Radians => RA:  {ra}    DEC: {dec}")
    # RA:  08h13m42.429227
    # 08:13:42.429227
    # DEC: -5.747297080233693

    # headers = {'Content-type': 'application/json'}
    r = requests.patch(
        f"http://10.0.0.200:8765/api/goto/{ra}/{dec}")
    print(r)
    print(r.content)
    # print(json.dumps(r.content, indent=2))

# Protocol definition is here.  Stellarium is the "client", telescope is the "server".
# http://svn.code.sf.net/p/stellarium/code/trunk/telescope_server/stellarium_telescope_protocol.txt

# client->server:
# MessageGoto (type =0)
# LENGTH (2 bytes,integer): length of the message
# TYPE   (2 bytes,integer): 0
# TIME   (8 bytes,integer): current time on the client computer in microseconds
#                   since 1970.01.01 UT. Currently unused.
# RA     (4 bytes,unsigned integer): right ascension of the telescope (J2000)
#            a value of 0x100000000 = 0x0 means 24h=0h,
#            a value of 0x80000000 means 12h
# DEC    (4 bytes,signed integer): declination of the telescope (J2000)
#            a value of -0x40000000 means -90degrees,
#            a value of 0x0 means 0degrees,
#            a value of 0x40000000 means 90degrees
