from quart import request
from quart_trio import QuartTrio
from astropy.coordinates import HADec, ICRS, SkyCoord
from astropy.time import Time
import telescope_control as tc
from api.camera import (
    camera_config_get,
    camera_config_set,
    camera_config_get_all,
    camera_config_set_all,
    camera_attach_lens,
)
from api.response import returnResponse
from api import api


def create_app(telescope: tc.TelescopeControl):
    app = QuartTrio(__name__)

    app.register_blueprint(api, url_prefix="/api")

    # TODO: Update the API to get things from telescope.config (and rebuild the
    # config, stop the telescope, restart the telescope as needed).

    @app.route("/api/calibrate/", methods=["POST"])
    async def calibrate():
        try:
            _ra = request.args.get("ra")
            _dec = request.args.get("dec")
            telescope.calibrate(tc.FixedTarget(SkyCoord(ra=_ra, dec=_dec, frame=ICRS)))

            return await returnResponse(
                {"calibrated": True, "ra": _ra, "dec": _dec}, 200
            )

        except:
            return await returnResponse(
                {"calibrated": False, "ra": _ra, "dec": _dec}, 400
            )

    @app.route("/api/calibrate/by_name/", methods=["POST"])
    async def calibrate_by_name():
        try:
            _name = request.args.get("name")

            telescope.calibrate(tc.FixedTarget(SkyCoord.from_name(_name)))

            return await returnResponse({"calibrated": True, "name": _name}, 200)
        except:
            return await returnResponse({"calibrated": False, "name": _name}, 400)

    @app.route("/api/calibrate/solar_system_object/", methods=["POST"])
    async def calibrate_solar_system_object():
        try:
            _name = request.args.get("name")

            telescope.calibrate(tc.SolarSystemTarget(_name))

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

    @app.route("/api/goto/", methods=["POST"])
    async def goto():
        try:
            _ra = request.args.get("ra")
            _dec = request.args.get("dec")

            telescope.target = tc.FixedTarget(SkyCoord(ra=_ra, dec=_dec, frame=ICRS))

            return await returnResponse({"goto": True, "ra": _ra, "dec": _dec}, 200)

        except:
            return await returnResponse({"goto": False, "ra": _ra, "dec": _dec}, 400)

    @app.route("/api/goto/by_name/", methods=["POST"])
    async def goto_by_name():
        try:
            _name = request.args.get("name")
            telescope.target = tc.FixedTarget(SkyCoord.from_name(_name))

            return await returnResponse({"goto": True, "name": _name}, 200)
        except:
            return await returnResponse({"goto": False, "name": _name}, 400)

    @app.route("/api/goto/solar_system_object/", methods=["POST"])
    async def goto_solar_system_object():
        try:
            _name = request.args.get("name")
            telescope.target = tc.SolarSystemTarget(_name)
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

    return app
