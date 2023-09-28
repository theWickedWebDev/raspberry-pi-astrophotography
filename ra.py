import time
import math
#
import sleep
import server
import motor


def track():
    deadline = time.time_ns()
    while True:
        if bool(server.settings['tracking'] == True):
            NANOSECONDS_PER_STEP = round(
                1_682_892_392 / math.cos(server.settings["declination"]))
            STEP_DELAY = NANOSECONDS_PER_STEP // server.settings["step_multiplier"]
            motor.ra_step()
            server.settings["current_position"] += 1
            deadline += STEP_DELAY
            sleep.nsleep(deadline - time.time_ns())
