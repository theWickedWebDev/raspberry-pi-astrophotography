from flask import Flask, request, make_response
from astropy.coordinates import ICRS, SkyCoord
from rich import print_json

#
import log
import validate
import steps
import telescope_control as tc


settings = dict()


def create_app(telescope: tc.TelescopeControl):
    app = Flask(__name__)

    # TODO: Update the API to get things from telescope.config (and rebuild the
    # config, stop the telescope, restart the telescope as needed).

    @app.route("/api/settings", methods=["GET"])
    def get_settings():
        return settings

    @app.route("/api/settings/<setting>/<new_value>", methods=["PATCH"])
    def update_setting(setting, new_value):
        statusCode = 200

        validationResponse = validate.setting[setting](new_value, settings[setting])
        if validationResponse["statusCode"] == 200:
            settings[setting] = validationResponse["value"]
            log.settings(settings)
        else:
            statusCode = validationResponse["statusCode"]
            log.error(
                "/api/settings/" + setting + "/" + new_value + "/", statusCode, "PATCH"
            )

        response = make_response(settings)
        response.status_code = statusCode
        return response

    @app.route("/api/goto/<_ra>/<_dec>", methods=["POST"])
    def goto(_ra, _dec):
        statusCode = 200

        telescope.set_target(tc.FixedTarget(SkyCoord(ra=_ra, dec=_dec, frame=ICRS)))

        response = make_response(settings)
        response.status_code = statusCode
        print_json(data=settings)
        return settings

    @app.route("/api/goto/by_name/<_name>", methods=["POST"])
    def goto_by_name(_name):
        statusCode = 200

        telescope.set_target(tc.FixedTarget(SkyCoord.from_name(_name)))

        response = make_response(settings)
        response.status_code = statusCode
        print_json(data=settings)
        return settings

    @app.route("/api/goto/solar_system_object/<_name>", methods=["POST"])
    def goto_solar_system_object(_name):
        statusCode = 200

        telescope.set_target(tc.SolarSystemTarget(_name))

        response = make_response(settings)
        response.status_code = statusCode
        print_json(data=settings)
        return settings

    @app.route("/api/settings", methods=["PATCH"])
    def put_settings():
        new_settings = request.get_json()
        statusCode = 200

        for key in new_settings:
            validationResponse = validate.setting[key](new_settings[key], settings[key])
            if validationResponse["statusCode"] == 200:
                settings[key] = validationResponse["value"]
            else:
                statusCode = validationResponse["statusCode"]

        log.settings(settings)
        response = make_response(settings)
        response.status_code = statusCode
        return response

    @app.route("/api/settings/slew/dec/<steps>", methods=["POST"])
    def slew_dec(steps):
        statusCode = 200

        newDecTarget = (
            float(steps) * DEC_RAD_PER_STEP + settings["dec_current_position"]
        )
        settings["dec_target_position"] = newDecTarget
        log.settings(settings)
        response = make_response(settings)
        response.status_code = statusCode
        return response

    return app
