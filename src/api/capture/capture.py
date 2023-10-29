from quart import request
from .._blueprint import api
import trio
from gphoto2.gphoto import GPhoto
from api.response import returnResponse
from api.capture.util import set_config, set_bulb_capture, set_filename
from api.telescope import get_telescope
from api.camera import Cam

scope: trio.CancelScope | None = None

REQUIRED_CAPTURE_STACK_FIELDS = { "name": "String", "focal_length": "Number"}

@api.route("/camera/capture/stack/start/", methods=["POST"])
async def capture_stack_start():
    try:
        global scope
        settings = await request.json
        
        if ('name' not in  settings):
                raise Exception("'name' not provided.", REQUIRED_CAPTURE_STACK_FIELDS)
        
        print(Cam)
        # if ('focal_length' not in  settings):
        #         raise Exception("'focal_length' not provided.", REQUIRED_CAPTURE_STACK_FIELDS)

        # TODO: Add target object (use from telescope goto?)
        if scope:
            print('scope exists already')
            scope.cancel()
            scope = None
        scope = trio.CancelScope()

        _default_settings = {
            "frames": 1,
            "iso": "800",
            "aperture": "4",
            "exposure": "1",
        }

        _default_settings.update(settings)
        api.nursery.start_soon(Cam.captureStack, scope, _default_settings)
        return await returnResponse({"capturing_stack": True}, 200)
    except Exception as e:
        return await returnResponse({"capturing_stack": False, "error": e.args}, 400)


# @api.route("/camera/capture/stack/status/", methods=["POST"])
# async def capture_stack_status():
     
     
@api.route("/camera/capture/stack/stop/", methods=["POST"])
async def capture_stack_stop():
    global scope
    tel = get_telescope()

    # ha, dec = telescope.orientation
    # telescope.target = tc.FixedTarget(SkyCoord(ha + ha_change, dec + dec_change, frame=HADec(obstime=Time.now(), location=telescope.config.location))
    print('TELESCOPE')
    print(tel.orientation)
    print(tel.target)
    print(tel.config)
    if scope:
        scope.cancel()
        scope = None
    return await returnResponse({"capturing_stack": False}, 200)
