"""Windows icon set: 16/24/32 hand-specified, 48/64 procedural (reduced detail),
128/256/512/1024 as exact integer nearest-neighbour upscales of the 64 master.
Writes a multi-resolution .ico (16-128 as 32-bit BMP/DIB with AND mask, 256 as
PNG) with a self-contained writer so no resampling ever touches the pixels.
"""
from __future__ import annotations

import io
import struct

import numpy as np
from PIL import Image

import emblem
import icons_small
from pix import Canvas, alpha_over


def _center(c: Canvas, size):
    out = Canvas(size, size)
    alpha_over(out.a, c.a, (size - c.w) // 2, (size - c.h) // 2)
    return out


def build_all():
    icons = {}
    for s in (16, 24, 32):
        icons[s] = icons_small.build(s)
    icons[48] = _center(emblem.build(0.667, 'medium'), 48)
    icons[64] = _center(emblem.build(0.889, 'medium'), 64)
    for s, k in ((128, 2), (256, 4), (512, 8), (1024, 16)):
        c = Canvas(s, s)
        c.a = np.repeat(np.repeat(icons[64].a, k, 0), k, 1)
        icons[s] = c
    return icons


def _dib(arr):
    h, w = arr.shape[:2]
    bgra = arr[::-1, :, [2, 1, 0, 3]].tobytes()   # bottom-up BGRA
    row_bytes = ((w + 31) // 32) * 4
    mask = bytearray()
    for y in range(h - 1, -1, -1):
        bits = 0
        row = bytearray(row_bytes)
        for x in range(w):
            if arr[y, x, 3] == 0:
                row[x // 8] |= 0x80 >> (x % 8)
        mask += row
    header = struct.pack('<IiiHHIIiiII', 40, w, h * 2, 1, 32, 0, len(bgra) + len(mask), 0, 0, 0, 0)
    return header + bgra + bytes(mask)


def write_ico(path, icons, sizes=(16, 24, 32, 48, 64, 128, 256)):
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
