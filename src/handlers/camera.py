from flask import request
from gphoto2.gphoto import GPhoto
from handlers.response import returnResponse

Cam = GPhoto()


def camera_config_get(_config):
    try:
        value = Cam.getSetting(_config)
        return returnResponse({
            _config: value
        })
    except Exception as e:
        return returnResponse({
            "error": e.args
        }, 400)


def camera_config_set(_config, _value):
    try:
        settings = Cam.setSetting(_config, _value)
        return returnResponse({
            "camera_settings_updated": True,
            _config: settings
        })
    except Exception as e:
        return returnResponse({
            "error": e.args[0]
        }, 400)


def camera_config_get_all():
    try:
        result = Cam.getSettings()
        return returnResponse(result)
    except Exception as e:
        return returnResponse({
            "error": e.args[0]
        }, 400)


def camera_config_set_all():
    try:
        content = request.json
        result = Cam.setSettings(content)
        return returnResponse(result)
    except Exception as e:
        return returnResponse({
            "error": e.args[0]
        }, 400)


def camera_attach_lens(_focalLength):
    try:
        result = Cam.initLens(_focalLength)
        return returnResponse(result)
    except Exception as e:
        return returnResponse({
            "error": e.args[0]
        }, 400)
