from ._blueprint import api
import trio
from gphoto2.gphoto import GPhoto
from api.response import returnResponse


async def capture():
    print("  child1: started! sleeping now...")
    await trio.sleep(1)
    print("  child1: exiting!")


@api.route("/camera/capture/stack/", methods=["POST"])
async def capture_stack():
    api.nursery.start_soon(capture)
    return await returnResponse({"capturing_stack": True}, 200)
