from flask import Flask, request
import math
import threading
from dms2dec.dms_convert import dms2dec
from numpy import deg2rad
import json
import time
#
import gpio
import sleep
import motor
import validate

HOST = '10.0.0.200'
PORT = 8765

gpio.setup()


app = Flask(__name__)

settings = dict(
    declination=deg2rad(dms2dec('''0°0'00.000"N''')),
    time_scale=1,
    step_multiplier=4,
    ra_current_position=0,
    dec_current_position=0,
    tracking=True
)


def track():
    deadline = time.time_ns()
    while True:
        if bool(settings['tracking'] == True):

            forward = settings['time_scale'] > 0

            # TODO Check max/min value for time_scale
            scale = abs(settings['time_scale'])

            NANOSECONDS_PER_STEP = round(
                1_682_892_392 / math.cos(settings["declination"]) / scale)
            STEP_DELAY = NANOSECONDS_PER_STEP // settings["step_multiplier"]
            motor.ra_step(forward)
            settings["ra_current_position"] += 1
            deadline += STEP_DELAY
            sleep.nsleep(deadline - time.time_ns())


threading.Thread(target=track).start()


def logSettings(data):
    with open('./settings.log', 'a') as convert_file:
        convert_file.write(json.dumps(settings) + '\n')
        convert_file.close()
    settings.update(data)


@app.route('/api/settings', methods=['GET'])
def get_settings():
    return settings


@app.route('/api/settings/<setting>/<new_value>', methods=['PATCH'])
def update_setting(setting, new_value):
    settings[setting] = validate.setting[setting](new_value, settings[setting])
    logSettings(settings)
    return settings


@app.route('/api/settings', methods=['PATCH'])
def put_settings():
    new_settings = request.get_json()
    for key in new_settings:
        settings[key] = validate.setting[key](new_settings[key], settings[key])
    logSettings(settings)
    return settings


app.run(host=HOST, port=PORT)
