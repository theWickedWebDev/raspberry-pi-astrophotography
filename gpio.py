import RPi.GPIO as GPIO

RA_ENABLE_PIN = 12
RA_PULSE_PIN = 19
RA_DIRECTION_PIN = 13

DEC_ENABLE_PIN = 24
DEC_PULSE_PIN = 18
DEC_DIRECTION_PIN = 4


def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # GPIO Setup
    GPIO.setup(RA_ENABLE_PIN, GPIO.OUT)
    GPIO.setup(RA_PULSE_PIN, GPIO.OUT)
    GPIO.setup(RA_DIRECTION_PIN, GPIO.OUT)
    GPIO.setup(DEC_ENABLE_PIN, GPIO.OUT)
    GPIO.setup(DEC_PULSE_PIN, GPIO.OUT)
    GPIO.setup(DEC_DIRECTION_PIN, GPIO.OUT)

    # GPIO Initial Values
    GPIO.output(RA_DIRECTION_PIN, 0)
    GPIO.output(RA_ENABLE_PIN, 0)
    GPIO.output(DEC_DIRECTION_PIN, 0)
    GPIO.output(DEC_ENABLE_PIN, 0)
