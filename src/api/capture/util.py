def set_config(**kwargs):
    return [
        word
        for k, v in kwargs.items()
        for word in
        ("--set-config", f"{k}={str(v)}")
    ]

def set_bulb_capture(exposure):
    return [
        '--set-config', 'eosremoterelease=5',
        '--wait-event=' + exposure,
        '--set-config', 'eosremoterelease=11',
        '--wait-event-and-download=6s'
    ]

def set_filename(frame, dir='./captures'):
    filename = dir + "/%m-%d_%H:%M:%S__frame_" + str(frame)
    return [
        '--filename', filename + '.%C'
    ]