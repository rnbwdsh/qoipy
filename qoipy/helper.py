from functools import lru_cache

START = int.from_bytes(b"qoif", "big")
END = b"\0" * 7 + b"\1"
MAX_RUN = 62  # 64 - 2


class OP:  # constants wouldn't work in match-case statements
    INDEX = 0x00
    DIFF = 0x40
    LUMA = 0x80
    MASK = RUN = 0xc0
    I_MASK = 0x3f
    RGB = 0xfe
    RGBA = 0xff


@lru_cache
def color_hash(r, g, b, a=0):
    return (r * 3 + g * 5 + b * 7 + a * 11) % 64


def add3(px, other):
    for i in range(3):
        px[i] = (px[i] + other[i] + 256) % 256


@lru_cache
def in_range(ran, *args):
    for a in args:
        if not -ran <= a < ran:
            return False
    return True


def sanity_check(start, w, h, channels, colorspace):
    if start is not None:
        assert start == START
    assert w > 0
    assert h > 0
    assert channels in (3, 4)
    assert colorspace in (0, 1)


@lru_cache()
def signed_int(a: int) -> int:
    a = (a + 256) % 256
    return a if a < 128 else a - 256
