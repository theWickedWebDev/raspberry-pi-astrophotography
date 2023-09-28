import RPi.GPIO as GPIO
#
import gpio
import sleep


def ra_step():
    GPIO.output(gpio.RA_ENABLE_PIN, 0)
    GPIO.output(gpio.RA_PULSE_PIN, 1)
    sleep.nsleep(50_000)
    GPIO.output(gpio.RA_PULSE_PIN, 0)
    GPIO.output(gpio.RA_ENABLE_PIN, 1)


def dec_step():
    GPIO.output(gpio.DEC_ENABLE_PIN, 0)
    GPIO.output(gpio.DEC_PULSE_PIN, 1)
    sleep.nsleep(50_000)
    GPIO.output(gpio.DEC_PULSE_PIN, 0)
    GPIO.output(gpio.DEC_ENABLE_PIN, 1)


def validateSpeed():
    # TODO: Write this
    return True
