from quart import request
from .._blueprint import api
import trio
from gphoto2.gphoto import GPhoto
from api.response import returnResponse
from api.capture.util import set_config, set_bulb_capture, set_filename

scope: trio.CancelScope | None = None

async def capture(scope: trio.CancelScope, settings):
    print(settings)

    imageformat = "7"
    if ("jpeg" in settings) and (settings['jpeg'] == True):
        imageformat = "6"
    if ("jpegonly" in settings) and (settings['jpegonly'] == True):
        imageformat = "0"
   
    exposure = str(settings['exposure']) + 's'

    with scope:
        for i in range(settings['frames']):

            res = await trio.run_process([
                'gphoto2',
                *set_filename(i),
                *set_config(
                    aperture=settings['aperture'],
                    iso=settings['iso'],
                    imageformat=imageformat,
                ),
                *set_bulb_capture(exposure),
            ], capture_stdout=True, capture_stderr=True)

            lines = res.stdout.splitlines()
            if (res.stderr):
                # print("ERROR!")
                for line in res.stderr.splitlines():
                    print(line.decode())
                # if ("An error occurred in the io-library" in res.stderr):
                # if ('Could not claim the USB device' in res.stderr):
                # reset_usb()
                # toggle camera relay via gpio

            for line in lines:
                if "Saving file" in line.decode():
                    print(line.decode())
        # TODO: Call a "post stack capture" function here to begin pre-processing


@api.route("/camera/capture/stack/start/", methods=["POST"])
async def capture_stack_start():
    try:
        global scope
        settings = await request.json

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
        api.nursery.start_soon(capture, scope, _default_settings)
        return await returnResponse({"capturing_stack": True}, 200)
    except Exception as e:
        return await returnResponse({"capturing_stack": False, "error": e}, 400)


@api.route("/camera/capture/stack/stop/", methods=["POST"])
async def capture_stack_stop():
    global scope
    if scope:
        scope.cancel()
        scope = None
    return await returnResponse({"capturing_stack": False}, 200)
