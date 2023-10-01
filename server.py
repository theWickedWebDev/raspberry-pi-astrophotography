from flask import Flask, request, make_response
import math
import threading
from dms2dec.dms_convert import dms2dec
from numpy import deg2rad
import time
from rich import print_json
#
import log
import gpio
import sleep
import motor
import validate
import steps

HOST = '10.0.0.200'
PORT = 8765

gpio.setup()

POLARIS_RA = 38.31919259166666
POLARIS_DEC = 1.5579117591980816

app = Flask(__name__)

settings = dict(
    # is mount actively tracking an object
    tracking=True,
    # Current position of Right Ascention Axis
    ra_current_steps=0,
    # Current position of Declination Axis (deg)
    dec_current_steps=0,
    # Right ascension speed adjustment (positive=forward / negative=backwards)
    ra_time_scale=1,
    # Declination speed adjustment (positive=forward / negative=backwards)
    dec_time_scale=1,
    # Microstepping value for Right Ascention motor
    ra_step_multiplier=4,
    # Microstepping value for Declination motor
    dec_step_multiplier=4,
    #
    #
    # Current position of Right Ascention Axis (deg)
    ra_current_position=POLARIS_RA,
    # Current position of Declination Axis (deg)
    dec_current_position=POLARIS_DEC,
    # Final Coordinates
    goto_en=False,
    goto_ra=0,
    goto_dec=0,
    # Remaining Steps for GOTO
    goto_remaining_ra_steps=0,
    goto_remaining_dec_steps=0,
    goto_remaining_ra_degrees=0,
    goto_remaining_dec_degrees=0
)


# you should start rearranging code to make it so there is a
# distance-remaining variable for both motors (which might be zero)

# we know our current position
# we give a target position
# from that, we calculate ra-dist-remaining, dec-dist-remaining
# the motor loops try to move thos *-dist-remaining values down to zero by moving

def ra():
    deadline = time.time_ns()
    while True:
        if bool(settings['tracking'] == True):
            forward = settings['ra_time_scale'] > 0
            scale = abs(settings['ra_time_scale'])
            NANOSECONDS_PER_STEP = round(
                1_682_892_392 / math.cos(settings["dec_current_position"]) / scale)
            STEP_DELAY = NANOSECONDS_PER_STEP // settings["ra_step_multiplier"]
            # STEP_DELAY = 1_250_000
            motor.ra_step(forward)
            settings["ra_current_steps"] += 1
            deadline += STEP_DELAY
            sleep.nsleep(deadline - time.time_ns())


threading.Thread(target=ra).start()


@app.route('/api/settings', methods=['GET'])
def get_settings():
    return settings


@app.route('/api/settings/<setting>/<new_value>', methods=['PATCH'])
def update_setting(setting, new_value):
    statusCode = 200

    validationResponse = validate.setting[setting](
        new_value, settings[setting])
    if validationResponse['statusCode'] == 200:
        settings[setting] = validationResponse['value']
        log.settings(settings)
    else:
        statusCode = validationResponse['statusCode']
        log.error('/api/settings/' + setting +
                  '/' + new_value + '/', statusCode, 'PATCH')

    response = make_response(settings)
    response.status_code = statusCode
    return response


@app.route('/api/goto/<_ra>/<_dec>', methods=['PATCH'])
def goto(_ra, _dec):
    statusCode = 200

    print(f"RA: {_ra}")
    print(f"DEC: {_dec}")

    _goto = dict(
        ra=float(_ra),
        dec=float(_dec)
    )

    b = dict(
        ra=settings["ra_current_position"],
        dec=settings["dec_current_position"]
    )

    settings['goto_ra'] = _goto["ra"]
    settings['goto_dec'] = _goto["dec"]

    settings["goto_remaining_ra_degrees"] = _goto["ra"] - b["ra"]
    settings["goto_remaining_dec_degrees"] = _goto["dec"] - b["dec"]

    settings['goto_remaining_steps'] = steps.compare(_goto, b)

    settings['goto_remaining_ra_steps'] = steps.compare(_goto, b)
    settings['goto_remaining_dec_steps'] = steps.compare(_goto, b)

    response = make_response(settings)
    response.status_code = statusCode
    print_json(data=settings)
    return settings


@app.route('/api/settings', methods=['PATCH'])
def put_settings():
    new_settings = request.get_json()
    statusCode = 200

    for key in new_settings:
        validationResponse = validate.setting[key](
            new_settings[key], settings[key])
        if validationResponse['statusCode'] == 200:
            settings[key] = validationResponse['value']
        else:
            statusCode = validationResponse['statusCode']

    log.settings(settings)
    response = make_response(settings)
    response.status_code = statusCode
    return response


app.run(host=HOST, port=PORT)
