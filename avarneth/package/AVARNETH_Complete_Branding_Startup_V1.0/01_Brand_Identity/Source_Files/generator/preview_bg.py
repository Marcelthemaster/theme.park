"""PREVIEW MOCK-UP background (480x270 native) - NOT the original AVARNETH login scene.

A self-made stand-in so the startup overlay can be judged in context: dusk sky,
drifting clouds, distant mountains on the left, a mountain fortress with lit
windows and golden gate motes on the right, moving mist, falling leaves and a
generic login-panel mock-up. It is never baked into any production asset.
"""
from __future__ import annotations

import math
import random

import numpy as np
from pix import Canvas, col, RAMPS, alpha_over, poly_mask, rect_mask, outline
from fonts import STEEL7, text_mask, styled

W, H = 480, 270


def _c(hexs):
    h = hexs.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


SKY = [_c(x) for x in ('#0c1020', '#111830', '#16203c', '#1c2a4a', '#243656', '#2f4460', '#3e5468', '#57606c',
                       '#7a6a64', '#a07a5e')]


def _static_layers(seed=7):
    rnd = random.Random(seed)
    sky = np.zeros((H, W, 4), np.uint8)
    for y in range(H):
        i = min(len(SKY) - 1, int(y / 175 * len(SKY)))
        sky[y, :] = SKY[i]
    # stars
    for _ in range(90):
        x, y = rnd.randrange(W), rnd.randrange(0, 110)
        sky[y, x] = (200, 210, 230, 255) if rnd.random() < 0.3 else (120, 135, 170, 255)

    far = Canvas(W, H)
    pts = [(0, 170)]
    x = 0
    while x < W:
        x += rnd.randint(18, 40)
        pts.append((x, rnd.randint(120, 165)))
    pts += [(W, 270), (0, 270)]
    m = poly_mask(W, H, pts)
    far.put(m, _c('#2a3550'))
    far.put(outline(m) & ~m & (np.arange(H)[:, None] < 200), _c('#3d4b68'))

    near = Canvas(W, H)
    pts = [(0, 205)]
    x = 0
    while x < 300:
        x += rnd.randint(14, 30)
        pts.append((x, rnd.randint(180, 205)))
    pts += [(300, 270), (0, 270)]
    m = poly_mask(W, H, pts)
    near.put(m, _c('#1b2236'))
    near.put(outline(m) & ~m, _c('#2c3650'))

    # mountain fortress (right)
    fort = Canvas(W, H)
    rock = poly_mask(W, H, [(270, 270), (300, 200), (330, 150), (352, 110), (372, 80), (392, 64), (410, 72),
                            (432, 60), (452, 78), (480, 70), (480, 270)])
    fort.put(rock, _c('#232633'))
    Y, X = np.mgrid[0:H, 0:W]
    fort.put(rock & ((X + Y * 2) % 23 == 0), _c('#2d3140'))
    fort.put(outline(rock) & ~rock, _c('#3a3f52'))
    keep = rect_mask(W, H, 372, 92, 430, 170) | rect_mask(W, H, 392, 70, 412, 92)
    towers = rect_mask(W, H, 350, 120, 366, 190) | rect_mask(W, H, 438, 104, 456, 186)
    for tx0, tx1, ty in ((350, 366, 120), (438, 456, 104), (372, 430, 92), (392, 412, 70)):
        for mx in range(tx0, tx1, 4):
            keep |= rect_mask(W, H, mx, ty - 3, mx + 2, ty)
    walls = rect_mask(W, H, 330, 170, 470, 200)
    for mx in range(330, 470, 4):
        walls |= rect_mask(W, H, mx, 167, mx + 2, 170)
    b = keep | towers | walls
    fort.put(b, _c('#363a48'))
    fort.put(b & (X % 16 < 2), _c('#2c303c'))
    fort.put(outline(b) & ~b, _c('#14161e'))
    # gate
    gate = rect_mask(W, H, 392, 176, 410, 200) | (((X - 401) ** 2 / 81 + (Y - 176) ** 2 / 64) <= 1)
    fort.put(gate & (Y < 200), _c('#6a3a1a'))
    fort.put(gate & (Y > 186) & (Y < 200), _c('#b86a28'))
    windows = []
    for (wx, wy) in ((356, 132), (356, 150), (444, 118), (444, 140), (380, 104), (398, 80), (420, 104), (380, 128),
                     (420, 128), (346, 180), (460, 180)):
        windows.append((wx, wy))
    ground = Canvas(W, H)
    gm = rect_mask(W, H, 0, 228, W, H)
    ground.put(gm, _c('#141a28'))
    ground.put(gm & (Y == 228), _c('#222b40'))
    return sky, far, near, fort, ground, windows


_CACHE = {}


def cloud_shape(w, h, seed):
    rnd = random.Random(seed)
    c = Canvas(w, h)
    m = np.zeros((h, w), bool)
    Y, X = np.mgrid[0:h, 0:w]
    for _ in range(6):
        cx, cy = rnd.uniform(w * 0.2, w * 0.8), rnd.uniform(h * 0.4, h * 0.8)
        rx, ry = rnd.uniform(w * 0.15, w * 0.3), rnd.uniform(h * 0.25, h * 0.45)
        m |= ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 <= 1
    c.put(m, _c('#33415e'))
    top = m & ~np.roll(m, 1, 0)
    c.put(top, _c('#4a5a78'))
    c.put(m & ~np.roll(m, -1, 0), _c('#283450'))
    return c


def login_panel():
    c = Canvas(150, 92)
    m = rect_mask(150, 92, 1, 1, 149, 91)
    c.put(m, (16, 18, 26, 235))
    c.put(outline(m, True) | (m & ~rect_mask(150, 92, 2, 2, 148, 90)), col('gold', 3))
    for i, (label, y) in enumerate((('ACCOUNT', 10), ('PASSWORD', 36))):
        t = styled(text_mask(STEEL7, label, tracking=1), ('iron', 7), edge=('iron', 0), shadow=('iron', 1), pad=1)
        alpha_over(c.a, t.a, 12, y)
        f = rect_mask(150, 92, 12, y + 11, 138, y + 22)
        c.put(f, col('iron', 1))
        c.put(outline(f) & ~f, col('iron', 4))
    btn = rect_mask(150, 92, 44, 66, 106, 82)
    c.put(btn, col('gold', 3))
    c.put(btn & (np.mgrid[0:92, 0:150][0] == 66), col('gold', 5))
    c.put(outline(btn) & ~btn, col('iron', 0))
    t = styled(text_mask(STEEL7, 'LOGIN', tracking=1), ('gold', 8), edge=('gold', 0), shadow=('gold', 1), pad=1)
    alpha_over(c.a, t.a, 75 - t.w // 2, 68)
    return c


def watermark():
    t = styled(text_mask(STEEL7, 'PREVIEW MOCKUP - TEST BACKGROUND - NOT THE ORIGINAL LOGIN SCENE', tracking=1,
                         space=3), ('iron', 6), edge=('iron', 0), shadow=('iron', 1), pad=1)
    return t


def frame(t, login_alpha=1.0):
    if 'static' not in _CACHE:
        _CACHE['static'] = _static_layers()
        _CACHE['clouds'] = [(cloud_shape(70, 22, 11), 20, 40, 3.0), (cloud_shape(90, 26, 12), 190, 62, 2.0),
                            (cloud_shape(60, 18, 13), 330, 30, 4.0), (cloud_shape(80, 24, 14), -60, 92, 2.5)]
        _CACHE['panel'] = login_panel()
        _CACHE['wm'] = watermark()
        rnd = random.Random(5)
        _CACHE['leaves'] = [(rnd.uniform(0, W), rnd.uniform(-40, H), rnd.uniform(6, 14), rnd.uniform(0, 6.28),
                             rnd.choice([col('ember', 4), col('gold', 4), col('ember', 3)])) for _ in range(14)]
        _CACHE['motes'] = [(rnd.uniform(388, 414), rnd.uniform(0, 1), rnd.uniform(0.6, 1.4)) for _ in range(10)]
    sky, far, near, fort, ground, windows = _CACHE['static']
    out = sky.copy()
    for cl, x0, y0, sp in _CACHE['clouds']:
        alpha_over(out, cl.a, int(x0 + sp * t), y0)
    alpha_over(out, far.a)
    alpha_over(out, near.a)
    alpha_over(out, fort.a)
    # lit windows with a subtle flicker
    for i, (wx, wy) in enumerate(windows):
        k = 6 if (math.sin(t * 7 + i * 1.7) > -0.6) else 5
        out[wy:wy + 4, wx:wx + 2] = col('ember', k)
        out[wy, wx:wx + 2] = col('ember', 7)
    alpha_over(out, ground.a)
    # mist bands
    Y, X = np.mgrid[0:H, 0:W]
    for (yb, amp, sp, a) in ((206, 3, 6.0, 46), (222, 2, -4.0, 60), (238, 3, 3.0, 70)):
        band = np.abs(Y - (yb + amp * np.sin((X + sp * t * 10) / 37.0))) < 3
        mist = np.zeros((H, W, 4), np.uint8)
        mist[band] = (150, 160, 180, a)
        alpha_over(out, mist)
    # golden motes at the fortress gate
    for (mx, ph, sp) in _CACHE['motes']:
        u = (ph + t * 0.35 * sp) % 1.0
        x, y = int(mx + 3 * math.sin(u * 6.28)), int(198 - u * 40)
        if 0 <= y < H:
            out[y, x] = col('gold', 8, int(255 * (1 - u)))
    # falling leaves
    for (lx, ly, sp, ph, cc) in _CACHE['leaves']:
        y = (ly + sp * t * 2.0) % (H + 40) - 20
        x = int(lx + 6 * math.sin(ph + t * 1.3)) % W
        if 0 <= int(y) < H - 1:
            out[int(y), x] = cc
            out[int(y) + 1, (x + 1) % W] = cc
    if login_alpha > 0:
        p = _CACHE['panel']
        alpha_over(out, p.a, 165, 140, opacity=login_alpha)
    wm = _CACHE['wm']
    alpha_over(out, wm.a, 4, H - wm.h - 3)
    return out
