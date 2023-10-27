from __future__ import annotations
import argparse
import logging
import logging.config
import os
import threading

from astropy.coordinates import EarthLocation, HADec, SkyCoord
from astropy.time import Time
import astropy.units as u

import appserver
from lib.stellarium import StellariumTCPServer
from lib.nsleep import nsleep
import telescope_control as tc

_log = logging.getLogger(__name__)

try:
    with open(os.path.join(os.path.dirname(__file__), "logging.json"), "r") as f:
        import json
        import logging.config

        logging.config.dictConfig(json.load(f))
except FileNotFoundError:
    pass


STEPHEN_HOUSE = EarthLocation(
    lat=42.8164989 * u.deg,  # pyright: ignore
    lon=-71.0638871 * u.deg,  # pyright: ignore
    height=52.32 * u.m,  # pyright: ignore
)


def orientation_from_skycoord(coord: SkyCoord) -> tc.TelescopeOrientation:
    tcoord = coord.transform_to(
        HADec(obstime=Time.now(), location=STEPHEN_HOUSE))
    return tcoord.ha, tcoord.dec


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--virtual",
        action="store_true",
        default=False,
        help="When set, run in virtual mode (only serving to Stellarium, no motor control)",
    )

    args = parser.parse_args()

    if not args.virtual:
        import lib.pi.gpio as gpio

        gpio.setup()

    telescope = tc.TelescopeControl(
        config=tc.Config(
            bearing_axis=tc.StepperAxis(
                motor_steps=800,
                gear_ratio=4 * 4 * 4 * 4,
                max_speed=1.5 * u.deg / u.second,  # pyright: ignore
            ),
            declination_axis=tc.StepperAxis(
                motor_steps=400,
                gear_ratio=4 * 4,
                max_speed=4 * u.deg / u.second,  # pyright: ignore
            ),
            motor_controller=(
                noop_motor_controller if args.virtual else rpi_motor_controller
            ),
            location=STEPHEN_HOUSE,
        ),
        orientation=(
            0 * u.hourangle,  # pyright: ignore
            0 * u.deg,  # pyright: ignore
        ),
        # orientation=orientation_from_skycoord(SkyCoord.from_name("Polaris")),
        # orientation=orientation_from_skycoord(SkyCoord.from_name("Mebsuta")),
        # target=tc.FixedTarget(
        #     SkyCoord(
        #         0 * u.hourangle,  # pyright: ignore
        #         0 * u.deg,  # pyright: ignore
        #         frame=HADec(obstime=Time.now(), location=STEPHEN_HOUSE),
        #     ).transform_to(ICRS)
        # ),
        # target=tc.FixedTarget(SkyCoord.from_name("Mebsuta")),
        # target=tc.FixedTarget(SkyCoord.from_name("Polaris")),
        # target=tc.FixedTarget(SkyCoord.from_name("Vega")),
        # target=tc.SolarSystemTarget("jupiter"),
    )

    telescope.start()

    app = appserver.create_app(telescope)
    threading.Thread(target=app.run, args=[
                     "0.0.0.0", 8765], daemon=True).start()

    stellarium_addr = "0.0.0.0", 10001
    with StellariumTCPServer(stellarium_addr, telescope) as server:
        server.serve_forever()


def noop_motor_controller(
    telescope: tc.TelescopeControl,
    axes: list[tc.StepperAxis],
    actions: list[int],
):
    for axis, action in zip(axes, actions):
        name = "unknown"
        if axis is telescope.config.bearing_axis:
            name = "bearing"
        elif axis is telescope.config.declination_axis:
            name = "dec"

        if action != 0:
            _log.debug(f"pulse {name}: {action}")


def rpi_motor_controller(
    telescope: tc.TelescopeControl,
    axes: list[tc.StepperAxis],
    actions: list[int],
):
    import lib.pi.motor as motor

    def find_pins(axis: tc.StepperAxis):
        if axis is telescope.config.bearing_axis:
            return motor.RA_PINS, 1, 0
        elif axis is telescope.config.declination_axis:
            return motor.DEC_PINS, 0, 1
        else:
            _log.error(f"unknown axis: {axis}")
            return None

    resolved_actions = [
        (find_pins(axis), action) for axis, action in zip(axes, actions)
    ]
    for [pins, fwd, rev], action in resolved_actions:
        if pins is None:
            continue

        if action == 1:
            motor.leading(pins, fwd)  # forward
        elif action == -1:
            motor.leading(pins, rev)  # backward

    nsleep(motor.PULSE_NS)

    for [pins, _, _], _ in resolved_actions:
        if pins is None:
            continue

        motor.trailing(pins)


if __name__ == "__main__":
    main()
