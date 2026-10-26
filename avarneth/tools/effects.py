"""Effect layers for the AVARNETH startup: emblem trace, flashes, glows, shine
sweep, glint, ember/gold particle sprites and the backdrop veil.

All effects are pixel art on the native grid: hard pixels with a small set of
stepped alpha levels (no blur), using the master palette only.
"""
from __future__ import annotations

import math
from collections import deque

import numpy as np
from pix import Canvas, col, RAMPS, inner_edge, outline, dilate, edt_inside, BAYER4

ALPHA_STEPS = (255, 200, 150, 100, 60, 32)


def _rgba(ramp, i, a=255):
    r = RAMPS[ramp][i]
    return (r[0], r[1], r[2], int(a))


# ---------------------------------------------------------------------------
# Emblem trace: golden light runs along the silhouette from the apex down both
# sides and meets at the shield tip.
# ---------------------------------------------------------------------------
def contour_order(mask):
    """Geodesic distance (8-connected) along the boundary ring from its top pixel."""
    ring = inner_edge(mask, diagonal=False)
    ys, xs = np.where(ring)
    top = np.argmin(ys * 10000 + np.abs(xs - mask.shape[1] // 2))
    start = (ys[top], xs[top])
    dist = np.full(mask.shape, -1, int)
    dist[start] = 0
    q = deque([start])
    while q:
        y, x = q.popleft()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny, nx = y + dy, x + dx
                if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and ring[ny, nx] and dist[ny, nx] < 0:
                    dist[ny, nx] = dist[y, x] + 1
                    q.append((ny, nx))
    return ring, dist


def emblem_trace_frames(emblem: Canvas, n=14, margin=2, tail=0.35):
    mask = emblem.alpha_mask()
    ring, dist = contour_order(mask)
    dmax = dist.max()
    s = np.where(ring, dist / max(1, dmax), -1.0)
    W, H = emblem.w + 2 * margin, emblem.h + 2 * margin
    frames = []
    for f in range(n):
        p = (f + 1) / n
        c = Canvas(W, H)
        lit = ring & (s <= p) & (s >= 0)
        age = np.where(lit, (p - s) / tail, 9)  # 0 at the head
        ys, xs = np.where(lit)
        for y, x in zip(ys, xs):
            a = age[y, x]
            if a < 0.12:
                rgba = _rgba('gold', 9)
            elif a < 0.35:
                rgba = _rgba('gold', 8)
            elif a < 0.7:
                rgba = _rgba('gold', 7, 220)
            elif a < 1.0:
                rgba = _rgba('gold', 6, 160)
            else:
                rgba = _rgba('gold', 5, 110)
            c.px(x + margin, y + margin, rgba)
        # glowing heads (both sides) with a small halo just outside the silhouette
        head = lit & (age < 0.12)
        hy, hx = np.where(head)
        for y, x in zip(hy, hx):
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    yy, xx = y + dy + margin, x + dx + margin
                    if c.a[yy, xx, 3] == 0:
                        c.a[yy, xx] = _rgba('ember', 7, 120 if (dx == 0 or dy == 0) else 60)
        frames.append(c)
    return frames


def emblem_outline_glow(emblem: Canvas, margin=2):
    """Full lit outline (held after the trace and faded out by the timeline)."""
    mask = emblem.alpha_mask()
    ring = inner_edge(mask, diagonal=False)
    c = Canvas(emblem.w + 2 * margin, emblem.h + 2 * margin)
    ys, xs = np.where(ring)
    for y, x in zip(ys, xs):
        c.px(x + margin, y + margin, _rgba('gold', 8))
    big = np.zeros((c.h, c.w), bool)
    big[margin:margin + emblem.h, margin:margin + emblem.w] = mask
    halo = outline(big)
    c.a[halo] = _rgba('ember', 6, 90)
    return c


def silhouette_flash(layer: Canvas, ramp='gold', idx=8, alpha=255, mask=None):
    m = layer.alpha_mask() if mask is None else mask
    c = Canvas(layer.w, layer.h)
    c.put(m, _rgba(ramp, idx, alpha))
    return c


# ---------------------------------------------------------------------------
# Stepped radial glow (pixel-art light: concentric alpha bands, dithered seams)
# ---------------------------------------------------------------------------
def radial_glow(w, h, rx, ry, cx=None, cy=None, ramp='ember', idx=(6, 5, 4, 3), alphas=(120, 80, 48, 24),
                dither=True):
    c = Canvas(w, h)
    cx = (w - 1) / 2.0 if cx is None else cx
    cy = (h - 1) / 2.0 if cy is None else cy
    Y, X = np.mgrid[0:h, 0:w]
    r = np.hypot((X - cx) / rx, (Y - cy) / ry)
    nb = len(alphas)
    band = np.floor(r * nb).astype(int)
    if dither:
        frac = r * nb - band
        th = BAYER4[Y % 4, X % 4]
        band = band + ((frac > 0.75) & (th < (frac - 0.75) * 4)).astype(int)
    for b in range(nb):
        m = band == b
        c.a[m] = _rgba(ramp, idx[min(b, len(idx) - 1)], alphas[b])
    return c


def veil(w=480, h=270, cx=240, cy=135, rx=300, ry=170, max_alpha=150, min_alpha=70):
    """Backdrop dim behind the logo: dark iron, stronger in the centre, stepped bands."""
    c = Canvas(w, h)
    Y, X = np.mgrid[0:h, 0:w]
    r = np.clip(np.hypot((X - cx) / rx, (Y - cy) / ry), 0, 1)
    levels = 10
    t = 1 - r
    q = np.floor(t * levels) / levels          # flat stepped bands (pixel-art light falloff)
    a = (min_alpha + (max_alpha - min_alpha) * np.clip(q + 1 / levels, 0, 1)).astype(int)
    rgb = RAMPS['iron'][0]
    c.a[..., 0], c.a[..., 1], c.a[..., 2] = rgb
    c.a[..., 3] = np.clip(a, 0, 255)
    return c


# ---------------------------------------------------------------------------
# Wordmark shine: a slanted band of light sweeping left -> right, clipped to the
# gold face.
# ---------------------------------------------------------------------------
def shine_frames(face_mask, n=16, band=7, slope=0.5, start=-24, end=None):
    H, W = face_mask.shape
    end = W + 24 if end is None else end
    Y, X = np.mgrid[0:H, 0:W]
    frames = []
    for f in range(n):
        p = f / (n - 1)
        x0 = start + (end - start) * p
        # slanted coordinate: x + slope*y (top leans right)
        u = (X - (H - Y) * slope) - x0
        c = Canvas(W, H)
        core = (np.abs(u) <= 1.0) & face_mask
        mid = (np.abs(u) <= band / 2.0) & face_mask & ~core
        edge = (np.abs(u) <= band / 2.0 + 2) & face_mask & ~core & ~mid
        c.a[edge] = _rgba('gold', 8, 90)
        c.a[mid] = _rgba('gold', 9, 170)
        c.a[core] = _rgba('gold', 9, 255)
        frames.append(c)
    return frames


# ---------------------------------------------------------------------------
# Glint: 4-point star that pops at the emblem apex (final accent)
# ---------------------------------------------------------------------------
def glint_frames(n=10, size=17):
    c0 = size // 2
    sizes = [1, 3, 5, 7, 8, 7, 5, 4, 2, 1][:n]
    frames = []
    for k in sizes:
        c = Canvas(size, size)
        for d in range(-k, k + 1):
            a = 255 if abs(d) <= max(1, k // 3) else (170 if abs(d) <= k * 2 // 3 else 90)
            rgba = _rgba('gold', 9, a) if abs(d) <= 1 else _rgba('gold', 8, a)
            c.px(c0 + d, c0, rgba)
            c.px(c0, c0 + d, rgba)
        if k >= 3:
            for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
                c.px(c0 + dx, c0 + dy, _rgba('gold', 8, 140))
        if k >= 5:
            for dx, dy in ((2, 2), (-2, 2), (2, -2), (-2, -2)):
                c.px(c0 + dx, c0 + dy, _rgba('gold', 7, 70))
        c.px(c0, c0, _rgba('gold', 9, 255))
        frames.append(c)
    return frames


# ---------------------------------------------------------------------------
# Particle sprites (tiny, with their own stepped glow pixels)
# ---------------------------------------------------------------------------
def particle_sprites():
    out = []
    # 0: single hot ember
    c = Canvas(1, 1); c.px(0, 0, _rgba('ember', 7)); out.append(c)
    # 1: single dim ember
    c = Canvas(1, 1); c.px(0, 0, _rgba('ember', 5)); out.append(c)
    # 2: ember with cross glow
    c = Canvas(3, 3)
    c.px(1, 1, _rgba('ember', 8))
    for x, y in ((0, 1), (2, 1), (1, 0), (1, 2)):
        c.px(x, y, _rgba('ember', 5, 150))
    out.append(c)
    # 3: 2x2 ember chunk
    c = Canvas(2, 2)
    c.px(0, 0, _rgba('ember', 7)); c.px(1, 0, _rgba('ember', 6)); c.px(0, 1, _rgba('ember', 5)); c.px(1, 1, _rgba('ember', 4))
    out.append(c)
    # 4: gold spark with cross glow
    c = Canvas(3, 3)
    c.px(1, 1, _rgba('gold', 9))
    for x, y in ((0, 1), (2, 1), (1, 0), (1, 2)):
        c.px(x, y, _rgba('gold', 7, 140))
    out.append(c)
    # 5: vertical ember streak
    c = Canvas(1, 3)
    c.px(0, 0, _rgba('ember', 8)); c.px(0, 1, _rgba('ember', 6, 170)); c.px(0, 2, _rgba('ember', 4, 90))
    out.append(c)
    # 6: single gold mote
    c = Canvas(1, 1); c.px(0, 0, _rgba('gold', 8)); out.append(c)
    return out
