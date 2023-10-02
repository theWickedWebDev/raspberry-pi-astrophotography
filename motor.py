import RPi.GPIO as GPIO
#
import gpio
import sleep

RA_PINS = dict(
    dir=gpio.RA_DIRECTION_PIN,
    en=gpio.RA_ENABLE_PIN,
    pul=gpio.RA_PULSE_PIN
)

DEC_PINS = dict(
    dir=gpio.DEC_DIRECTION_PIN,
    en=gpio.DEC_ENABLE_PIN,
    pul=gpio.DEC_PULSE_PIN
)


def step(pins, dir):
    # Set direction; forward=0 backward=1
    GPIO.output(pins['dir'], dir)
    # Enable Motor
    GPIO.output(pins['en'], 0)
    # Rising Edge
    GPIO.output(pins['pul'], 1)
    # Propagation
    sleep.nsleep(50_000)
    # Falling Edge
    GPIO.output(pins['pul'], 0)
    # Disable Motor
    GPIO.output(pins['en'], 1)


def ra_step(dir):
    step(RA_PINS, dir)


def dec_step(dir):
    step(DEC_PINS, dir)


def ra_setMicrosteps(val):
    print(f"Set RA microstepping to {val}")


def dec_setMicrosteps(val):
    print(f"Set DEC microstepping to {val}")
