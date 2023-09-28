def declination(value, cur):
    # TODO:
    if value:
        return value
    else:
        return cur


def step_multiplier(value, cur):
    # TODO:
    if value:
        return int(value)
    else:
        return cur


def time_scale(value, cur):
    # TODO:
    if int(value) == 0:
        return cur
    else:
        return int(value)


def ra_current_position(value, cur):
    # TODO:
    if value:
        return value
    else:
        return cur


def dec_current_position(value, cur):
    # TODO:
    if value:
        return value
    else:
        return cur


setting = dict(
    declination=declination,
    step_multiplier=step_multiplier,
    time_scale=time_scale,
    ra_current_position=ra_current_position,
    dec_current_position=dec_current_position
)
