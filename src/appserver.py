from flask import Flask, request
from astropy.coordinates import HADec, ICRS, SkyCoord
from astropy.time import Time
import telescope_control as tc
from handlers.camera import camera_config_get, camera_config_set, camera_config_get_all, camera_config_set_all, camera_attach_lens
from handlers.response import returnResponse


def create_app(telescope: tc.TelescopeControl):
    app = Flask(__name__)

    # TODO: Update the API to get things from telescope.config (and rebuild the
    # config, stop the telescope, restart the telescope as needed).

    def calib(target: tc.Target, track: bool = True):
        coord = target.coordinate(Time.now(), telescope.config.location)
        tcoord = coord.transform_to(
            HADec(obstime=Time.now(), location=telescope.config.location)
        )

        running = telescope.is_running
        if running:
            telescope.stop()

        o: tc.TelescopeOrientation = (tcoord.ha, tcoord.dec)  # pyright: ignore
        telescope.set_orientation(o)
        if track:
            telescope.set_target(target)

        if running:
            telescope.start()

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

            telescope.set_target(tc.FixedTarget(
                SkyCoord(ra=_ra, dec=_dec, frame=ICRS)))

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
            _name = request.args.get('name')
            telescope.set_target(tc.FixedTarget(SkyCoord.from_name(_name)))

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
            _name = request.args.get('name')
            telescope.set_target(tc.SolarSystemTarget(_name))
            return returnResponse({
                "goto": True,
                "object": _name,
            })
        except:
            return returnResponse({
                "goto": False,
                "object": _name,
            }, 400)

    app.add_url_rule(
        "/api/camera/config/", methods=["GET"], view_func=camera_config_get_all)

    app.add_url_rule(
        "/api/camera/config/", methods=["POST"], view_func=camera_config_set_all)

    app.add_url_rule(
        "/api/camera/config/<_config>/", methods=["GET"], view_func=camera_config_get)

    app.add_url_rule(
        "/api/camera/config/<_config>/<_value>/", methods=["POST"], view_func=camera_config_set)

    app.add_url_rule(
        "/api/lens/<_focalLength>/", methods=["POST"], view_func=camera_attach_lens)

    return app
