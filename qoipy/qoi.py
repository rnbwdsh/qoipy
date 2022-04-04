from itertools import islice, chain
from struct import pack, unpack
from typing import Union, Iterable, Iterator, Optional, Tuple

from PIL import Image

from helper import *


def encode(it: Union[Image.Image, Iterator, Iterable], whc: Optional[Tuple[int, int, int]] = None) -> bytearray:
    colorspace = 0  # srgb = 0, lin = 1

    if isinstance(it, Image.Image):
        w, h, channels = it.width, it.height, len(it.getbands())
        it = chain(*it.getdata())
    else:
        assert type(whc) == tuple
        assert len(whc) == 3
        w, h, channels = whc
    if type(it) != iter:
        it = iter(it)
    sanity_check(None, w, h, channels, colorspace)

    # initialize helpers
    cache = [[0, 0, 0, 0] for _ in range(64)]
    prev = [0, 0, 0, 255]
    px_len = w * h * channels
    body = bytearray(pack(">IIIBB", START, w, h, channels, colorspace))
    run = 0

    for px_pos in range(0, px_len, channels):
        px = list(islice(it, channels))
        if channels == 3:
            px.append(255)
        c_hash = color_hash(*px)
        if px == prev:
            run += 1
            if run == MAX_RUN:
                body.append(OP.RUN | (run - 1))
                run = 0
        else:
            if run > 0:
                body.append(OP.RUN | (run - 1))
                run = 0
            if cache[c_hash] == px:
                body.append(OP.INDEX | c_hash)
            else:
                cache[c_hash] = px
                if px[3] == prev[3]:
                    vr = signed_int(px[0] - prev[0])
                    vg = signed_int(px[1] - prev[1])
                    vb = signed_int(px[2] - prev[2])
                    vg_r = signed_int(vr - vg)
                    vg_b = signed_int(vb - vg)
                    if in_range(2, vr, vg, vb):
                        body.append(OP.DIFF | (vr + 2) << 4 | (vg + 2) << 2 | (vb + 2))
                    elif in_range(8, vg_r, vg_b) and in_range(32, vg):
                        body.append(OP.LUMA | (vg + 32))
                        body.append((vg_r + 8) << 4 | (vg_b + 8))
                    else:
                        body.extend([OP.RGB] + px[:3])
                else:
                    body.extend([OP.RGBA] + px[:4])
        prev = px
    # close last running
    if run > 0:
        body.append(OP.RUN | (run - 1))
    body.extend(END)
    return body


def decode(it: Union[Iterable, Iterator]) -> bytearray:
    # Change iterable to iterator
    if type(it) != iter:
        it = iter(it)

    # sanity checks
    header = bytes(islice(it, 14))
    start, w, h, channels, colorspace = sanity = unpack(">IIIBB", header)
    sanity_check(*sanity)
    assert start == START

    # initialize help variables
    cache = [[0, 0, 0, 0] for _ in range(64)]
    px = [0, 0, 0, 255]
    px_len = w * h * channels
    pixels = bytearray()
    run = 0

    for px_pos in range(0, px_len, channels):
        if run:
            run -= 1
        else:
            match b1 := next(it):
                case OP.RGB:
                    px[:3] = list(islice(it, 3))
                case OP.RGBA:
                    px[:4] = list(islice(it, 4))
                case _:
                    b1r = b1 & 0x3f
                    match b1 & OP.MASK:
                        case OP.INDEX:
                            px = list(cache[b1])
                        case OP.DIFF:
                            add3(px, [(b1 >> (4 - i * 2) & 3) - 2 for i in range(3)])
                        case OP.LUMA:
                            b2 = next(it)
                            vg = b1r - 32
                            add3(px, [vg - 8 + ((b2 >> 4) & 0x0f),
                                      vg,
                                      vg - 8 + ((b2) & 0x0f)])
                        case OP.RUN:
                            run = b1r
            cache[color_hash(*px)] = list(px)  # set copy, as reference will be overwritten
        pixels.extend(px[:channels])
    return pixels
