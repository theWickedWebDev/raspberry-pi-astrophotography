from __future__ import annotations
import argparse
import logging
import logging.config
import os
import threading

from astropy.coordinates import EarthLocation, HADec, ICRS, SkyCoord
from astropy.time import Time
import astropy.units as u

import appserver
from stellarium import StellariumTCPServer
import telescope_control as tc
from nsleep import nsleep

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
        import gpio

        gpio.setup()

    telescope = tc.TelescopeControl(
        config=tc.Config(
            bearing_axis=tc.StepperAxis(
                motor_steps=800,
                gear_ratio=4 * 4 * 4 * 4,
                max_speed=1 * u.deg / u.second,  # pyright: ignore
            ),
            declination_axis=tc.StepperAxis(
                motor_steps=800,
                gear_ratio=4 * 4,
                max_speed=2 * u.deg / u.second,  # pyright: ignore
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
        # target=tc.FixedTarget(
        #     SkyCoord(
        #         0 * u.hourangle,  # pyright: ignore
        #         0 * u.deg,  # pyright: ignore
        #         frame=HADec(obstime=Time.now(), location=STEPHEN_HOUSE),
        #     ).transform_to(ICRS)
        # ),
        target=tc.FixedTarget(SkyCoord.from_name("Vega")),
        # target=tc.SolarSystemTarget("jupiter"),
    )

    telescope.start()

    app = appserver.create_app(telescope)
    threading.Thread(target=app.run, args=["0.0.0.0", 8765], daemon=True).start()

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
    import motor

    def find_pins(axis: tc.StepperAxis):
        if axis is telescope.config.bearing_axis:
            return motor.RA_PINS
        elif axis is telescope.config.declination_axis:
            return motor.DEC_PINS
        else:
            _log.error(f"unknown axis: {axis}")
            return None

    resolved_actions = [
        (find_pins(axis), action) for axis, action in zip(axes, actions)
    ]
    for pins, action in resolved_actions:
        if pins is None:
            continue

        if action == 1:
            motor.leading(pins, 0)  # forward
        elif action == -1:
            motor.leading(pins, 1)  # backward

    nsleep(motor.PULSE_NS)

    for pins, _ in resolved_actions:
        if pins is None:
            continue

        motor.trailing(pins)


if __name__ == "__main__":
    main()
