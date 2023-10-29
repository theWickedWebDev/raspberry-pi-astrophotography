from __future__ import annotations
import argparse
import logging
import logging.config
import os

from astropy.coordinates import EarthLocation, HADec, SkyCoord
from astropy.time import Time
import astropy.units as u
import trio

import appserver
import lib.stellarium as stellarium
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

TELESCOPE_MOUNT_GEAR_RATIO = 4 * 4 * 4 * 4
CAMERA_MOUNT_GEAR_RATIO = 4 * 4

RA_MOTOR_STEPS = 200 * 8
DEC_MOTOR_STEPS = 200 * 8
RA_GEAR_RATIO = 4 * 4 * 4 * 4
DEC_GEAR_RATIO = TELESCOPE_MOUNT_GEAR_RATIO


def orientation_from_skycoord(coord: SkyCoord) -> tc.TelescopeOrientation:
    tcoord = coord.transform_to(HADec(obstime=Time.now(), location=STEPHEN_HOUSE))
    return tcoord.ha, tcoord.dec


async def main():
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
                motor_steps=RA_MOTOR_STEPS,
                gear_ratio=RA_GEAR_RATIO,
                max_speed=1.5 * u.deg / u.second,  # pyright: ignore
            ),
            declination_axis=tc.StepperAxis(
                motor_steps=DEC_MOTOR_STEPS,
                gear_ratio=DEC_GEAR_RATIO,
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

    app = appserver.create_app(telescope)

    try:
        async with trio.open_nursery() as n:
            n.start_soon(telescope.run)
            n.start_soon(stellarium.serve, "0.0.0.0", 10001, telescope)
            n.start_soon(app.run_task, "0.0.0.0", 8765)
    except KeyboardInterrupt:
        pass


def noop_motor_controller(
    config: tc.Config,
    axes: list[tc.StepperAxis],
    actions: list[int],
):
    for axis, action in zip(axes, actions):
        name = "unknown"
        if axis is config.bearing_axis:
            name = "bearing"
        elif axis is config.declination_axis:
            name = "dec"

        if action != 0:
            _log.debug(f"pulse {name}: {action}")


def rpi_motor_controller(
    config: tc.Config,
    axes: list[tc.StepperAxis],
    actions: list[int],
):
    import lib.pi.motor as motor

    def find_pins(axis: tc.StepperAxis):
        if axis is config.bearing_axis:
            return motor.RA_PINS, 0, 1
        elif axis is config.declination_axis:
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
    trio.run(main)
