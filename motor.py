import RPi.GPIO as GPIO

import gpio
from nsleep import nsleep

RA_PINS = dict(
    dir=gpio.RA_DIRECTION_PIN,
    en=gpio.RA_ENABLE_PIN,
    pul=gpio.RA_PULSE_PIN,
)

DEC_PINS = dict(
    dir=gpio.DEC_DIRECTION_PIN,
    en=gpio.DEC_ENABLE_PIN,
    pul=gpio.DEC_PULSE_PIN,
)

PULSE_NS = 50_000


def step(pins, dir):
    leading(pins, dir)
    # Propagation
    nsleep(PULSE_NS)
    trailing(pins)


def leading(pins: dict, dir):
    # Set direction; forward=0 backward=1
    GPIO.output(pins["dir"], dir)
    # Enable Motor
    GPIO.output(pins["en"], 0)
    # Rising Edge
    GPIO.output(pins["pul"], 1)


def trailing(pins: dict):
    # Falling Edge
    GPIO.output(pins["pul"], 0)
    # Disable Motor
    GPIO.output(pins["en"], 1)


def ra_step(dir):
    step(RA_PINS, dir)


def dec_step(dir):
    step(DEC_PINS, dir)


def ra_setMicrosteps(val):
    print(f"Set RA microstepping to {val}")


def dec_setMicrosteps(val):
    print(f"Set DEC microstepping to {val}")
