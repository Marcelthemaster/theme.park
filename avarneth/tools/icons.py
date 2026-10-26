"""Windows icon set (revision 2).

* 16/20/24/30/32/36/40 px: reduced emblem drawn per size on the pixel grid (icons_small).
* 48/64 px: the emblem master in its 'icon' variant (brighter plate and right side).
* Every other size is an exact integer nearest-neighbour multiple of one of those:
  60 = 20x3, 72 = 24x3, 80 = 40x2, 96 = 48x2, 128 = 64x2, 256 = 64x4, 512 = 64x8, 1024 = 64x16.
  So Windows never has to resample (125 %/150 % display scaling asks for 20/30/36/40/60/72 px).
* The .ico is written by our own writer (16-128 as 32-bit DIB + AND mask, 256 as PNG),
  so no resampling ever touches the pixels.
"""
from __future__ import annotations

import io
import struct

import numpy as np
from PIL import Image

import emblem
import icons_small
from pix import Canvas, alpha_over

ICO_SIZES = (16, 20, 24, 30, 32, 36, 40, 48, 60, 64, 72, 80, 96, 128, 256)
DERIVED = {60: (20, 3), 72: (24, 3), 80: (40, 2), 96: (48, 2), 128: (64, 2), 256: (64, 4), 512: (64, 8), 1024: (64, 16)}


def _center(c: Canvas, size):
    out = Canvas(size, size)
    alpha_over(out.a, c.a, (size - c.w) // 2, (size - c.h) // 2)
    return out


def build_all():
    icons = {}
    for s in icons_small.SIZES:
        icons[s] = icons_small.build(s)
    icons[48] = _center(emblem.build(0.667, 'icon'), 48)
    icons[64] = _center(emblem.build(0.889, 'icon'), 64)
    for s, (src, k) in DERIVED.items():
        c = Canvas(s, s)
        c.a = np.repeat(np.repeat(icons[src].a, k, 0), k, 1)
        icons[s] = c
    return icons


def _dib(arr):
    h, w = arr.shape[:2]
    bgra = arr[::-1, :, [2, 1, 0, 3]].tobytes()   # bottom-up BGRA
    row_bytes = ((w + 31) // 32) * 4
    mask = bytearray()
    for y in range(h - 1, -1, -1):
        row = bytearray(row_bytes)
        for x in range(w):
            if arr[y, x, 3] == 0:
                row[x // 8] |= 0x80 >> (x % 8)
        mask += row
    header = struct.pack('<IiiHHIIiiII', 40, w, h * 2, 1, 32, 0, len(bgra) + len(mask), 0, 0, 0, 0)
    return header + bgra + bytes(mask)


def write_ico(path, icons, sizes=ICO_SIZES):
    blobs = []
    for s in sizes:
        arr = icons[s].a
        if s >= 256:
            b = io.BytesIO()
            Image.fromarray(arr, 'RGBA').save(b, 'PNG', optimize=True)
            blobs.append((s, b.getvalue()))
        else:
            blobs.append((s, _dib(arr)))
    out = bytearray(struct.pack('<HHH', 0, 1, len(blobs)))
    offset = 6 + 16 * len(blobs)
    for s, data in blobs:
        wh = 0 if s >= 256 else s
        out += struct.pack('<BBBBHHII', wh, wh, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    for s, data in blobs:
        out += data
    with open(path, 'wb') as f:
        f.write(out)
    return sizes
