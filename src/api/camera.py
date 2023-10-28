from ._blueprint import api
from quart import request
from gphoto2.gphoto import GPhoto

from api.response import returnResponse

Cam = GPhoto()


@api.route("/camera/config/<_config>/", methods=["GET"])
async def camera_config_get(_config):
    try:
        value = Cam.getSetting(_config)
        return await returnResponse({
            _config: value
        }, 200)
    except Exception as e:
        return await returnResponse({
            "error": e.args
        }, 400)


@api.route("/camera/config/<_config>/<_value>/", methods=["POST"])
async def camera_config_set(_config, _value):
    try:
        settings = Cam.setSetting(_config, _value)
        return await returnResponse({
            "camera_settings_updated": True,
            _config: settings
        }, 200)
    except Exception as e:
        return await returnResponse({
            "error": e.args[0]
        }, 400)


@api.route("/camera/config/", methods=["GET"])
async def camera_config_get_all():
    try:
        result = Cam.getSettings()
        return await returnResponse(result, 200)
    except Exception as e:
        return await returnResponse({
            "error": e.args[0]
        }, 400)


@api.route("/camera/config/", methods=["POST"])
async def camera_config_set_all():
    try:
        content = await request.json
        result = Cam.setSettings(content)
        return await returnResponse(result, 200)
    except Exception as e:
        return await returnResponse({
            "error": e.args[0]
        }, 400)


@api.route("/lens/<_focalLength>/", methods=["POST"])
async def camera_attach_lens(_focalLength):
    try:
        result = Cam.initLens(_focalLength)
        return await returnResponse(result, 200)
    except Exception as e:
        return await returnResponse({
            "error": e.args[0]
        }, 400)
