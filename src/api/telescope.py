from quart import current_app, request

from astropy.coordinates import ICRS, SkyCoord
from astropy.time import Time

from .. import telescope_control as tc
from ._blueprint import api
from .response import returnResponse

# TODO: Update the API to get things from telescope.config (and rebuild the
# config, stop the telescope, restart the telescope as needed).

KEY_TELESCOPE = "telescope"


def get_telescope() -> tc.TelescopeControl:
    telescope = current_app.config[KEY_TELESCOPE]
    assert isinstance(telescope, tc.TelescopeControl)
    return telescope


@api.route("/calibrate/", methods=["POST"])
async def calibrate():
    try:
        _ra = request.args.get("ra")
        _dec = request.args.get("dec")
        get_telescope().calibrate(
            tc.FixedTarget(SkyCoord(ra=_ra, dec=_dec, frame=ICRS))
        )

        return await returnResponse({"calibrated": True, "ra": _ra, "dec": _dec}, 200)

    except:
        return await returnResponse({"calibrated": False, "ra": _ra, "dec": _dec}, 400)


@api.route("/calibrate/by_name/", methods=["POST"])
async def calibrate_by_name():
    try:
        _name = request.args.get("name")
        get_telescope().calibrate(tc.FixedTarget(SkyCoord.from_name(_name)))

        return await returnResponse({"calibrated": True, "name": _name}, 200)
    except:
        return await returnResponse({"calibrated": False, "name": _name}, 400)


@api.route("/calibrate/solar_system_object/", methods=["POST"])
async def calibrate_solar_system_object():
    try:
        _name = request.args.get("name")

        get_telescope().calibrate(tc.SolarSystemTarget(_name))

        return await returnResponse(
            {
                "calibrated": True,
                "object": _name,
            },
            200,
        )
    except:
        return await returnResponse(
            {
                "calibrated": False,
                "object": _name,
            },
            400,
        )


@api.route("/goto/", methods=["POST"])
async def goto():
    try:
        _ra = request.args.get("ra")
        _dec = request.args.get("dec")

        get_telescope().target = tc.FixedTarget(SkyCoord(ra=_ra, dec=_dec, frame=ICRS))

        return await returnResponse({"goto": True, "ra": _ra, "dec": _dec}, 200)

    except:
        return await returnResponse({"goto": False, "ra": _ra, "dec": _dec}, 400)


@api.route("/goto/by_name/", methods=["POST"])
async def goto_by_name():
    try:
        _name = request.args.get("name")
        get_telescope().target = tc.FixedTarget(SkyCoord.from_name(_name))

        return await returnResponse({"goto": True, "name": _name}, 200)
    except:
        return await returnResponse({"goto": False, "name": _name}, 400)


@api.route("/goto/solar_system_object/", methods=["POST"])
async def goto_solar_system_object():
    try:
        _name = request.args.get("name")
        get_telescope().target = tc.SolarSystemTarget(_name)
        return await returnResponse(
            {
                "goto": True,
                "object": _name,
            },
            200,
        )
    except:
        return await returnResponse(
            {
                "goto": False,
                "object": _name,
            },
            400,
        )
