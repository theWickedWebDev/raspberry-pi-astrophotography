from quart import request
from quart_trio import QuartTrio
from astropy.coordinates import HADec, ICRS, SkyCoord
from astropy.time import Time
import telescope_control as tc
from api.camera import camera_config_get, camera_config_set, camera_config_get_all, camera_config_set_all, camera_attach_lens
from api.response import returnResponse
from api import api


def create_app(telescope: tc.TelescopeControl):
    app = QuartTrio(__name__)

    app.register_blueprint(api, url_prefix="/api")

    # TODO: Update the API to get things from telescope.config (and rebuild the
    # config, stop the telescope, restart the telescope as needed).

    def calib(target: tc.Target, track: bool = True):
        coord = target.coordinate(Time.now(), telescope.config.location)
        tcoord = coord.transform_to(
            HADec(obstime=Time.now(), location=telescope.config.location)
        )

        o: tc.TelescopeOrientation = (tcoord.ha, tcoord.dec)  # pyright: ignore
        telescope.orientation = o
        if track:
            telescope.target = target

    @app.route("/api/calibrate/", methods=["POST"])
    def calibrate():
        try:
            _ra = request.args.get('ra')
            _dec = request.args.get('dec')
            calib(tc.FixedTarget(SkyCoord(ra=_ra, dec=_dec, frame=ICRS)))

            return returnResponse({
                "calibrated": True,
                "ra": _ra,
                "dec": _dec
            })

        except:
            return returnResponse({
                "calibrated": False,
                "ra": _ra,
                "dec": _dec
            }, 400)

    @app.route("/api/calibrate/by_name/", methods=["POST"])
    def calibrate_by_name():
        try:
            _name = request.args.get('name')

            calib(tc.FixedTarget(SkyCoord.from_name(_name)))

            return returnResponse({
                "calibrated": True,
                "name": _name
            })
        except:
            return returnResponse({
                "calibrated": False,
                "name": _name
            }, 400)

    @app.route("/api/calibrate/solar_system_object/", methods=["POST"])
    def calibrate_solar_system_object():
        try:
            _name = request.args.get('name')

            calib(tc.SolarSystemTarget(_name))

            return returnResponse({
                "calibrated": True,
                "object": _name,
            })
        except:
            return returnResponse({
                "calibrated": False,
                "object": _name,
            }, 400)

    @app.route("/api/goto/", methods=["POST"])
    def goto():
        try:
            _ra = request.args.get('ra')
            _dec = request.args.get('dec')

            telescope.target = tc.FixedTarget(SkyCoord(ra=_ra, dec=_dec, frame=ICRS))

            return returnResponse({
                "goto": True,
                "ra": _ra,
                "dec": _dec
            })

        except:
            return returnResponse({
                "goto": False,
                "ra": _ra,
                "dec": _dec
            }, 400)

    @app.route("/api/goto/by_name/", methods=["POST"])
    def goto_by_name():
        try:
            _name = request.args.get("name")
            telescope.target = tc.FixedTarget(SkyCoord.from_name(_name))

            return returnResponse({
                "goto": True,
                "name": _name
            })
        except:
            return returnResponse({
                "goto": False,
                "name": _name
            }, 400)

    @app.route("/api/goto/solar_system_object/", methods=["POST"])
    def goto_solar_system_object():
        try:
            _name = request.args.get("name")
            telescope.target = tc.SolarSystemTarget(_name)
            return returnResponse(
                {
                    "goto": True,
                    "object": _name,
                }
            )
        except:
            return returnResponse({
                "goto": False,
                "object": _name,
            }, 400)

    return app
