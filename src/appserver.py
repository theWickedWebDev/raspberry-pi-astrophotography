from quart_trio import QuartTrio
from api import api
from api.telescope import KEY_TELESCOPE
from telescope_control import TelescopeControl


def create_app(telescope: TelescopeControl):
    app = QuartTrio(__name__)
    # I tried hard to use the app context to store the telescope object, but
    # according to the documentation, app contexts are created and destroyed on
    # demand.  They don't seem to be meant to store long-lived (same lifetime as
    # the app) Python objects.  So, instead I'm sticking it in app.config, which
    # seems wrong, but works.
    app.config[KEY_TELESCOPE] = telescope
    app.register_blueprint(api, url_prefix="/api")
    return app
