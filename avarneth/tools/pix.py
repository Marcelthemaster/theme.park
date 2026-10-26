"""AVARNETH pixel-art toolkit.

Everything is authored on an integer pixel grid (1 art pixel = 1 array cell)
without anti-aliasing. Shapes are sampled at pixel centres, shading is
quantised onto fixed palette ramps, upscaling is integer nearest-neighbour only.
"""
from __future__ import annotations

import math
import numpy as np
from PIL import Image
from scipy import ndimage

# --------------------------------------------------------------------------
# Master palette (sRGB). Ramps are ordered dark -> light.
# --------------------------------------------------------------------------
def _hex(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

RAMPS = {
    # dark iron / steel (cool)
    'iron':  ['#07070b', '#111219', '#1b1c25', '#262833', '#353845', '#4a4e5d', '#666b7b', '#8d92a1', '#b9bdc8', '#e3e5ea'],
    # aged gold / warm metal
    'gold':  ['#1d0f05', '#3a1f0a', '#5e3512', '#87511c', '#ad7128', '#cd9437', '#e6b552', '#f4d27e', '#fdebb0', '#fffbe6'],
    # dark natural stone (slightly warm grey)
    'stone': ['#0e0d0b', '#1a1815', '#25221e', '#322e29', '#423d36', '#554f46', '#6c655a', '#878073'],
    # ember / glow
    'ember': ['#2a0903', '#561406', '#8a230a', '#c1390e', '#e85d17', '#ff8b2b', '#ffb457', '#ffd892', '#fff1d0'],
    # arcane blue (sparing contrast accent)
    'arcane': ['#06111f', '#0c2440', '#153b66', '#215c92', '#3584be', '#5eb2e0', '#9fdcf6', '#e0f7ff'],
}
RAMPS = {k: [_hex(c) for c in v] for k, v in RAMPS.items()}

def col(ramp, i, a=255):
    r = RAMPS[ramp]
    i = int(max(0, min(len(r) - 1, i)))
    return (*r[i], a)

def all_palette():
    out = []
    for k, v in RAMPS.items():
        for i, c in enumerate(v):
            out.append((f'{k}{i}', c))
    return out

# --------------------------------------------------------------------------
# Canvas
# --------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), np.uint8)

    def put(self, mask, rgba):
        self.a[mask] = rgba

    def put_index(self, mask, ramp, idx, alpha=255):
        """mask: bool array; idx: int array (same shape) of ramp indices."""
        r = np.array(RAMPS[ramp], np.uint8)
        idx = np.clip(idx, 0, len(r) - 1)
        self.a[mask, :3] = r[idx[mask]]
        if np.isscalar(alpha):
            self.a[mask, 3] = alpha
        else:
            self.a[mask, 3] = alpha[mask]

    def px(self, x, y, rgba):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = rgba

    def over(self, other: 'Canvas', ox=0, oy=0):
        alpha_over(self.a, other.a, ox, oy)

    def image(self):
        return Image.fromarray(self.a, 'RGBA')

    def save(self, path, scale=1):
        im = self.image()
        if scale != 1:
            im = im.resize((self.w * scale, self.h * scale), Image.NEAREST)
        im.save(path, optimize=True)

    def alpha_mask(self):
        return self.a[..., 3] > 0

    def copy(self):
        c = Canvas(self.w, self.h)
        c.a = self.a.copy()
        return c


def alpha_over(dst, src, ox=0, oy=0, opacity=1.0):
    """Straight-alpha 'over' composite of src onto dst (both HxWx4 uint8), in place."""
    sh, sw = src.shape[:2]
    dh, dw = dst.shape[:2]
    x0, y0 = max(0, ox), max(0, oy)
    x1, y1 = min(dw, ox + sw), min(dh, oy + sh)
    if x0 >= x1 or y0 >= y1:
        return
    s = src[y0 - oy:y1 - oy, x0 - ox:x1 - ox].astype(np.float32) / 255.0
    d = dst[y0:y1, x0:x1].astype(np.float32) / 255.0
    sa = s[..., 3:4] * opacity
    da = d[..., 3:4]
    oa = sa + da * (1 - sa)
    oc = np.where(oa > 0, (s[..., :3] * sa + d[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6), 0)
    out = np.concatenate([oc, oa], axis=-1)
    dst[y0:y1, x0:x1] = np.clip(out * 255.0 + 0.5, 0, 255).astype(np.uint8)

# --------------------------------------------------------------------------
# Shape rasterisation (pixel-centre sampling, no AA)
# --------------------------------------------------------------------------
def grid(w, h):
    ys, xs = np.mgrid[0:h, 0:w]
    return xs + 0.5, ys + 0.5


def poly_mask(w, h, pts):
    """Even-odd polygon fill sampled at pixel centres. pts in pixel-edge coords."""
    X, Y = grid(w, h)
    inside = np.zeros((h, w), bool)
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if y1 == y2:
            continue
        cond = ((y1 > Y) != (y2 > Y))
        xint = (x2 - x1) * (Y - y1) / (y2 - y1) + x1
        inside ^= cond & (X < xint)
    return inside


def ellipse_mask(w, h, cx, cy, rx, ry):
    X, Y = grid(w, h)
    return ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 <= 1.0


def rect_mask(w, h, x0, y0, x1, y1):
    m = np.zeros((h, w), bool)
    m[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True
    return m


def bezier(p0, p1, p2, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        out.append((x, y))
    return out


def mirror_x(mask):
    """Force left/right symmetry: copy left half (incl. centre column) to the right."""
    w = mask.shape[1]
    out = mask.copy()
    half = (w + 1) // 2
    out[:, w - half:] = mask[:, :half][:, ::-1]
    return out


def shift(m, dx, dy, fill=False):
    h, w = m.shape
    out = np.full_like(m, fill)
    xs0, xs1 = max(0, -dx), min(w, w - dx)
    ys0, ys1 = max(0, -dy), min(h, h - dy)
    out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = m[ys0:ys1, xs0:xs1]
    return out


def outline(mask, diagonal=False):
    """Pixels outside `mask` that touch it (4-neighbour, optionally 8)."""
    st = np.ones((3, 3), bool) if diagonal else ndimage.generate_binary_structure(2, 1)
    return ndimage.binary_dilation(mask, st) & ~mask


def inner_edge(mask, diagonal=False):
    st = np.ones((3, 3), bool) if diagonal else ndimage.generate_binary_structure(2, 1)
    return mask & ~ndimage.binary_erosion(mask, st)


def erode(mask, r):
    if r <= 0:
        return mask.copy()
    d = ndimage.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
    return d > r


def dilate(mask, r):
    if r <= 0:
        return mask.copy()
    d = ndimage.distance_transform_edt(~np.pad(mask, 1, constant_values=False))[1:-1, 1:-1]
    return mask | (d <= r)


def edt_inside(mask):
    return ndimage.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]


def remove_orphans(mask, min_neighbours=1):
    """Remove isolated single pixels (no 4-neighbours inside the mask)."""
    st = ndimage.generate_binary_structure(2, 1)
    n = ndimage.convolve(mask.astype(int), st.astype(int), mode='constant') - mask
    return mask & (n >= min_neighbours)

# --------------------------------------------------------------------------
# Shading helpers
# --------------------------------------------------------------------------
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 + 1 / 32.0


def dither_levels(value, levels_lo, levels_hi=None, strength=1.0):
    """Quantise float `value` (in ramp-index units) with ordered dithering.

    strength 0 => plain rounding; 1 => full Bayer between neighbouring indices.
    """
    h, w = value.shape
    ys, xs = np.mgrid[0:h, 0:w]
    th = BAYER4[ys % 4, xs % 4]
    base = np.floor(value)
    frac = value - base
    frac = 0.5 + (frac - 0.5) * (1.0 / max(1e-6, strength)) if strength < 1 else frac
    return (base + (np.clip(frac, 0, 1) > th)).astype(int)


def bevel_light(mask, width=2.0, light=(-0.55, -0.83), smooth=0.9):
    """Return (d, ndotl) for a plate mask: d = distance from edge, ndotl in [-1,1]
    for the outward normal of the nearest edge vs. the light direction."""
    d = edt_inside(mask)
    ds = ndimage.gaussian_filter(d, smooth)
    gy, gx = np.gradient(ds)
    nrm = np.hypot(gx, gy) + 1e-6
    # outward normal = -gradient (gradient points inward)
    nx, ny = -gx / nrm, -gy / nrm
    lx, ly = light
    ln = math.hypot(lx, ly)
    ndl = (nx * lx + ny * ly) / ln
    return d, ndl


def upscale(arr, s):
    return np.repeat(np.repeat(arr, s, axis=0), s, axis=1)


def save_rgba(arr, path, scale=1):
    im = Image.fromarray(arr, 'RGBA')
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path, optimize=True)


def trim_box(arr):
    a = arr[..., 3] > 0
    ys, xs = np.where(a)
    if len(xs) == 0:
        return (0, 0, arr.shape[1], arr.shape[0])
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def checker_bg(w, h, s=8, c1=(48, 48, 56), c2=(64, 64, 72)):
    ys, xs = np.mgrid[0:h, 0:w]
    m = ((xs // s + ys // s) % 2) == 0
    out = np.zeros((h, w, 4), np.uint8)
    out[m] = (*c1, 255)
    out[~m] = (*c2, 255)
    return out
