"""Effect layers for the AVARNETH startup (revision 2).

* Emblem trace: golden light draws the silhouette (12 frames), then runs down
  both legs of the A and across the crossbar (4 frames) - 1 frame = 1/60 s.
* Highlight flashes: only the already-light pixels (rims, A legs, lit facets)
  receive a warm 3-step highlight, so light never bleaches dark areas.
* Outline glow: one ring just OUTSIDE the dark contour plus a faint ember halo.
* Shine sweep: 28 frames (1/60 s each), 12-14 px golden band with 3-step
  falloff, clipped to the gold letter faces.
* Particles: 1x1 / 1x2 / 1x3 embers and motes (no '+' twinkles).
* Veil: smooth full-screen radial dim (not pixel art, stretched in Unity).

Everything uses the master palette; alpha is stepped except for the veil.
"""
from __future__ import annotations

from collections import deque

import numpy as np
from pix import Canvas, col, RAMPS, inner_edge, outline, BAYER4

STEP = 1.0 / 60.0


def _rgba(ramp, i, a=255):
    r = RAMPS[ramp][i]
    return (r[0], r[1], r[2], int(a))


def _geodesic(mask, start):
    dist = np.full(mask.shape, -1, int)
    dist[start] = 0
    q = deque([start])
    while q:
        y, x = q.popleft()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny, nx = y + dy, x + dx
                if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx] and dist[ny, nx] < 0:
                    dist[ny, nx] = dist[y, x] + 1
                    q.append((ny, nx))
    return dist


def _top_center(mask):
    ys, xs = np.where(mask)
    i = np.argmin(ys * 10000 + np.abs(xs - mask.shape[1] // 2))
    return ys[i], xs[i]


def _draw_progress(c, mask, dist, p, margin, tail=0.35, head_halo=True, base_alpha=1.0):
    dmax = max(1, dist.max())
    s = np.where(mask & (dist >= 0), dist / dmax, -1.0)
    lit = (s >= 0) & (s <= p)
    age = np.where(lit, (p - s) / tail, 9)
    for y, x in zip(*np.where(lit)):
        a = age[y, x]
        if a < 0.12:
            rgba = _rgba('gold', 9, 255 * base_alpha)
        elif a < 0.35:
            rgba = _rgba('gold', 8, 235 * base_alpha)
        elif a < 0.7:
            rgba = _rgba('gold', 7, 200 * base_alpha)
        elif a < 1.0:
            rgba = _rgba('gold', 6, 150 * base_alpha)
        else:
            rgba = _rgba('gold', 6, 110 * base_alpha)
        c.px(x + margin, y + margin, rgba)
    if head_halo:
        head = lit & (age < 0.12)
        for y, x in zip(*np.where(head)):
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    yy, xx = y + dy + margin, x + dx + margin
                    if c.a[yy, xx, 3] == 0:
                        c.a[yy, xx] = _rgba('gold', 7, 110 if (dx == 0 or dy == 0) else 55)


def emblem_trace_frames(emblem: Canvas, a_mask, n_outline=12, n_branch=4, margin=2):
    """a_mask: gold legs + crossbar of the A (same size as the emblem)."""
    sil = emblem.alpha_mask()
    ring = inner_edge(sil, diagonal=False)
    rdist = _geodesic(ring, _top_center(ring))
    adist = _geodesic(a_mask, _top_center(a_mask))
    W, H = emblem.w + 2 * margin, emblem.h + 2 * margin
    frames = []
    for f in range(n_outline):
        c = Canvas(W, H)
        _draw_progress(c, ring, rdist, (f + 1) / n_outline, margin)
        frames.append(c)
    for f in range(n_branch):
        c = Canvas(W, H)
        fade = 1.0 - (f + 1) / (n_branch + 1)
        ys, xs = np.where(ring)
        for y, x in zip(ys, xs):
            c.px(x + margin, y + margin, _rgba('gold', 7, 170 * fade + 40))
        _draw_progress(c, a_mask, adist, (f + 1) / n_branch, margin, tail=0.5)
        frames.append(c)
    return frames


def emblem_outline_glow(emblem: Canvas, margin=2):
    """Ring of light one pixel OUTSIDE the dark contour, plus a faint ember halo."""
    mask = emblem.alpha_mask()
    W, H = emblem.w + 2 * margin, emblem.h + 2 * margin
    big = np.zeros((H, W), bool)
    big[margin:margin + emblem.h, margin:margin + emblem.w] = mask
    ring1 = outline(big)
    ring2 = outline(big | ring1) & ~big
    c = Canvas(W, H)
    c.a[ring2] = _rgba('gold', 5, 70)
    c.a[ring1] = _rgba('gold', 7, 200)
    Y = np.arange(H)[:, None].repeat(W, 1)
    c.a[ring1 & (Y < 6)] = _rgba('gold', 8, 220)          # near-white only at the very apex
    return c


_RAMP_LUT = {}


def _ramp_index():
    if not _RAMP_LUT:
        for ramp, cols in RAMPS.items():
            for i, c in enumerate(cols):
                _RAMP_LUT[tuple(c)] = (ramp, i)
    return _RAMP_LUT


def _lum(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def ramp_shift(rgb, steps):
    """Same colour moved `steps` up its own palette ramp (never darker)."""
    info = _ramp_index().get(tuple(int(v) for v in rgb))
    if info is None:
        return None
    ramp, i = info
    j = min(len(RAMPS[ramp]) - 1, i + steps)
    if j == i:
        return None
    return RAMPS[ramp][j]


def highlight_flash(layer: Canvas, restrict=None, steps=2, min_lum=95):
    """Light layer: every reasonably light pixel of `layer`, moved `steps` up its own ramp.

    Drawn with normal alpha blending it can only brighten (each colour is lighter than the pixel below),
    so the flash reads as light on the metal instead of a tint. Outline / extrusion / shadow pixels
    (luminance < min_lum) are excluded."""
    c = Canvas(layer.w, layer.h)
    a = layer.a
    for y, x in zip(*np.where(a[..., 3] > 0)):
        if restrict is not None and not restrict[y, x]:
            continue
        rgb = a[y, x, :3]
        if _lum(rgb) < min_lum:
            continue
        nc = ramp_shift(rgb, steps)
        if nc is not None:
            c.a[y, x] = (nc[0], nc[1], nc[2], 255)
    return c


def radial_glow(w, h, rx, ry, ramp='gold', idx=(7, 6, 6, 5, 5, 4), alphas=(110, 82, 58, 38, 22, 10)):
    c = Canvas(w, h)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    Y, X = np.mgrid[0:h, 0:w]
    r = np.hypot((X - cx) / rx, (Y - cy) / ry)
    nb = len(alphas)
    band = np.floor(r * nb).astype(int)
    frac = r * nb - band
    th = BAYER4[Y % 4, X % 4]
    band = band + ((frac > 0.7) & (th < (frac - 0.7) / 0.3 * 0.5)).astype(int)   # dithered seams
    for b in range(nb):
        c.a[band == b] = _rgba(ramp, idx[b], alphas[b])
    return c


def veil(w=480, h=270, cx=240.0, cy=135.0, rx=300.0, ry=170.0, center=140, edge=64):
    """Smooth full-screen radial dim (dark iron). Not pixel art: stretched to the screen in Unity."""
    c = Canvas(w, h)
    Y, X = np.mgrid[0:h, 0:w]
    r = np.clip(np.hypot((X + 0.5 - cx) / rx, (Y + 0.5 - cy) / ry), 0, 1)
    t = 1 - r
    t = t * t * (3 - 2 * t)
    a = edge + (center - edge) * t
    # constant outermost rows/columns so a clamped bilinear edge is invisible
    a[0, :], a[-1, :], a[:, 0], a[:, -1] = edge, edge, edge, edge
    rgb = RAMPS['iron'][0]
    c.a[..., 0], c.a[..., 1], c.a[..., 2] = rgb
    c.a[..., 3] = np.clip(np.round(a), 0, 255).astype(np.uint8)
    return c


def shine_frames(layer: Canvas, face_mask, n=28, slope=0.5, min_lum=95):
    """Slanted band of light sweeping left -> right over the gold faces: core +2 ramp steps,
    flanks +1 step, computed from the pixel below (never darker); outline/extrusion excluded.
    The sweep range is fitted to the letters, so every one of the n frames lights some pixels."""
    H, W = face_mask.shape
    Y, X = np.mgrid[0:H, 0:W]
    v = X - (H - Y) * slope
    lit = face_mask & (np.array([[_lum(layer.a[y, x, :3]) for x in range(W)] for y in range(H)]) >= min_lum)
    start, end = v[lit].min() - 3, v[lit].max() + 3
    frames = []
    for f in range(n):
        p = f / (n - 1)
        x0 = start + (end - start) * p
        u = np.abs(v - x0)
        c = Canvas(W, H)
        for y, x in zip(*np.where((u <= 7) & lit)):
            rgb = layer.a[y, x, :3]
            steps = 2 if u[y, x] <= 2.5 else 1
            nc = ramp_shift(rgb, steps)
            if nc is None:
                continue
            alpha = 255 if u[y, x] <= 4.5 else 150
            c.a[y, x] = (nc[0], nc[1], nc[2], alpha)
        frames.append(c)
    return frames


def glint_frames(n=8, size=17):
    c0 = size // 2
    sizes = [1, 3, 5, 8, 7, 5, 3, 1][:n]
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
        c.px(c0, c0, _rgba('gold', 9, 255))
        frames.append(c)
    return frames


def particle_sprites():
    out = []
    c = Canvas(1, 1); c.px(0, 0, _rgba('ember', 7)); out.append(c)                    # 0 hot ember
    c = Canvas(1, 1); c.px(0, 0, _rgba('ember', 5)); out.append(c)                    # 1 dim ember
    c = Canvas(1, 2); c.px(0, 0, _rgba('ember', 7)); c.px(0, 1, _rgba('ember', 4, 150)); out.append(c)   # 2 ember + trail
    c = Canvas(1, 3); c.px(0, 0, _rgba('ember', 8)); c.px(0, 1, _rgba('ember', 6, 170)); c.px(0, 2, _rgba('ember', 4, 80)); out.append(c)  # 3 streak
    c = Canvas(1, 1); c.px(0, 0, _rgba('gold', 8)); out.append(c)                     # 4 gold mote
    c = Canvas(1, 2); c.px(0, 0, _rgba('gold', 9)); c.px(0, 1, _rgba('gold', 6, 140)); out.append(c)    # 5 gold mote + trail
    return out
