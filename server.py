from flask import Flask, request
import math
import threading
from dms2dec.dms_convert import dms2dec
from numpy import deg2rad
import json
#
import gpio
import motor
import ra

HOST = '10.0.0.200'
PORT = 8765

gpio.setup()


app = Flask(__name__)

settings = dict(
    declination=deg2rad(dms2dec('''0°0'00.000"N''')),
    time_scale=1,
    step_multiplier=4,
    current_position=0,
    tracking=True
)

RA = threading.Thread(target=ra.track)
RA.start()


def updateSettings(data):
    with open('settings.log', 'w') as convert_file:
        convert_file.write(json.dumps(settings))
    settings.update(data)


@app.route('/settings', methods=['GET'])
def get_settings():
    return settings


@app.route('/settings', methods=['PUT'])
def put_settings():
    new_settings = request.get_json()
    #
    # FIXME: validate new_settings
    #

    if 'declination' in new_settings:
        settings['declination'] = deg2rad(dms2dec(new_settings['declination']))

    if 'step_multiplier' in new_settings:
        # TODO: Check max motor speed
        settings['step_multiplier'] = int(new_settings['step_multiplier'])

    if 'time_scale' in new_settings:
        # TODO: Check max motor speed
        if motor.validateSpeed(int(new_settings['time_scale'])) == True:
            settings['time_scale'] = int(new_settings['time_scale'])

    if 'current_position' in new_settings:
        # TODO: To reset to 0? vs goto position
        settings['current_position'] = int(new_settings['current_position'])

    if 'tracking' in new_settings:
        settings['tracking'] = bool(new_settings['tracking'] == 'True') or bool(
            new_settings['tracking'] == 'true') or bool(new_settings['tracking'] == '1')

    updateSettings(settings)
    return settings


app.run(host=HOST, port=PORT)
