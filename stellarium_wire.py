import math

def decode_ra(x):
    """Convert Stellarium wire RA value to fractional seconds"""
    return round((x % 0xffffffff) / 0xffffffff * 86_400)

#86_164.0905

def decode_dec(x):
    """Convert Stellarium wire DEC value to radians"""
    return x / 0x40000000 * math.pi / 2

def encode_ra(x):
    """Convert RA (fractional seconds) to Stellarium wire format"""
    return round((float(x) % 86_400) / 86_400 * 0xffffffff)

def encode_dec(x):
    """Convert DEC (radians) to Stellarium wire format"""
    return int(x * 2 / math.pi * 0x40000000)
