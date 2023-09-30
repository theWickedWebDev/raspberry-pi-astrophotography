def declination(value, cur):
    # TODO:
    if value:
        return dict(statusCode=200, value=value)
    else:
        return dict(statusCode=400, value=cur)


def ra_step_multiplier(value, cur):
    # TODO:
    if not value.lstrip('-+').isdigit():
        return dict(statusCode=400, value=cur)
    if int(value) == 0:
        return dict(statusCode=400, value=cur)
    else:
        return dict(statusCode=200, value=int(value))


def dec_step_multiplier(value, cur):
    # TODO:
    if not value.lstrip('-+').isdigit():
        return dict(statusCode=400, value=cur)
    if int(value) == 0:
        return dict(statusCode=400, value=cur)
    else:
        return dict(statusCode=200, value=int(value))


def ra_time_scale(value, cur):
    # TODO:
    if not value.lstrip('-+').isnumeric():
        return dict(statusCode=400, value=cur)
    if int(value) == 0:
        return dict(statusCode=400, value=cur)
    else:
        return dict(statusCode=200, value=int(value))


def dec_time_scale(value, cur):
    # TODO:
    if not value.lstrip('-+').isdigit():
        return dict(statusCode=400, value=cur)
    if int(value) == 0:
        return dict(statusCode=400, value=cur)
    else:
        return dict(statusCode=200, value=int(value))


def ra_current_position(value, cur):
    # TODO:
    if value:
        return dict(statusCode=200, value=value)
    else:
        return dict(statusCode=400, value=cur)


def dec_current_position(value, cur):
    # TODO:
    if value:
        return dict(statusCode=200, value=value)
    else:
        return dict(statusCode=400, value=cur)


setting = dict(
    declination=declination,
    ra_step_multiplier=ra_step_multiplier,
    ra_time_scale=ra_time_scale,
    ra_current_position=ra_current_position,
    dec_step_multiplier=dec_step_multiplier,
    dec_time_scale=dec_time_scale,
    dec_current_position=dec_current_position
)
