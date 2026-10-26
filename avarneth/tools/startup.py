"""AVARNETH startup animation: layer sprites, layout, timeline and particles.

`build()` returns (timeline_dict, sprites) where sprites maps the contract path
(relative to Importable_Assets/, e.g. "Layers/AVE_Emblem.png") to a Canvas.
The timeline follows work/CONTRACT.md exactly and is the single source of
truth for both the preview renderer (timeline_eval.py) and Unity.
"""
from __future__ import annotations

import random

import emblem as emblem_mod
import wordmark as wordmark_mod
import brand
import effects as fx
from pix import Canvas

CANVAS_W, CANVAS_H = 480, 270
DURATION = 2.0


def key(t, alpha, dx=0.0, dy=0.0, ease='linear'):
    return {'t': round(t, 4), 'alpha': round(alpha, 4), 'dx': round(dx, 4), 'dy': round(dy, 4), 'ease': ease}


def layer(id_, sprite, x, y, order, keys, frames=None, frame_start=0.0, frame_end=0.0, after='hold'):
    return {'id': id_, 'sprite': sprite or '', 'frames': frames or [], 'frameStart': frame_start,
            'frameEnd': frame_end, 'afterFrames': after, 'x': int(x), 'y': int(y), 'order': int(order),
            'keys': keys}


def build(seed=2026):
    sprites = {}

    # ---------------- art layers
    emb = emblem_mod.build(1.0, 'full')
    wm, face = wordmark_mod.build(return_face=True)
    sub = brand.build_subtitle()
    pub = brand.build_presents_line()

    # ---------------- layout (vertical lockup, optically centred)
    gap_pub, gap_emb, gap_sub = 9, 4, 4
    total = pub.h + gap_pub + emb.h + gap_emb + wm.h + gap_sub + sub.h
    top = (CANVAS_H - total) // 2 - 4
    px_, py_ = (CANVAS_W - pub.w) // 2, top
    ex, ey = (CANVAS_W - emb.w) // 2, py_ + pub.h + gap_pub
    wx, wy = (CANVAS_W - wm.w) // 2, ey + emb.h + gap_emb
    sx, sy = (CANVAS_W - sub.w) // 2, wy + wm.h + gap_sub

    sprites['Layers/AVE_Emblem.png'] = emb
    sprites['Layers/AVE_Wordmark.png'] = wm
    sprites['Layers/AVE_Subtitle.png'] = sub
    sprites['Layers/AVE_Publisher.png'] = pub

    # ---------------- effect layers
    veil = fx.veil(CANVAS_W, CANVAS_H, cx=CANVAS_W / 2, cy=ey + 70, rx=330, ry=190, max_alpha=165, min_alpha=60)
    sprites['Layers/AVE_Veil.png'] = veil

    gw, gh = 128, 136
    glow = fx.radial_glow(gw, gh, 60, 64, ramp='ember', idx=(6, 5, 4, 3), alphas=(70, 48, 30, 16))
    sprites['Layers/AVE_EmblemGlow.png'] = glow
    gx, gy = ex + emb.w // 2 - gw // 2, ey + emb.h // 2 + 4 - gh // 2

    sprites['Layers/AVE_EmblemFlash.png'] = fx.silhouette_flash(emb, 'gold', 8)
    og = fx.emblem_outline_glow(emb, margin=2)
    sprites['Layers/AVE_EmblemOutlineGlow.png'] = og
    sprites['Layers/AVE_WordmarkFlash.png'] = fx.silhouette_flash(wm, 'gold', 9, mask=face)

    trace = fx.emblem_trace_frames(emb, n=14, margin=2)
    trace_paths = []
    for i, f in enumerate(trace):
        p = f'Frames/AVE_EmblemTrace_{i:02d}.png'
        sprites[p] = f
        trace_paths.append(p)

    shine = fx.shine_frames(face, n=16)
    shine_paths = []
    for i, f in enumerate(shine):
        p = f'Frames/AVE_WordmarkShine_{i:02d}.png'
        sprites[p] = f
        shine_paths.append(p)

    glint = fx.glint_frames(10)
    glint_paths = []
    for i, f in enumerate(glint):
        p = f'Frames/AVE_Glint_{i:02d}.png'
        sprites[p] = f
        glint_paths.append(p)
    # apex of the emblem spire (first opaque pixel row, centre column)
    apex_x = ex + emb.w // 2
    apex_y = ey + 2

    parts = fx.particle_sprites()
    part_paths = []
    for i, p in enumerate(parts):
        path = f'Particles/AVE_Particle_{i:02d}.png'
        sprites[path] = p
        part_paths.append(path)

    FADE0, FADE1 = 1.72, 2.0

    layers = [
        layer('veil', 'Layers/AVE_Veil.png', 0, 0, 0,
              [key(0.0, 0.0), key(0.30, 1.0, ease='smooth'), key(FADE0 - 0.04, 1.0), key(FADE1, 0.0, ease='smooth')]),
        layer('emblemGlow', 'Layers/AVE_EmblemGlow.png', gx, gy, 10,
              [key(0.0, 0.0), key(0.32, 1.0, ease='outCubic'), key(0.70, 0.55, ease='smooth'),
               key(1.58, 0.55), key(1.68, 1.0, ease='outCubic'), key(FADE1, 0.0, ease='smooth')]),
        layer('publisher', 'Layers/AVE_Publisher.png', px_, py_, 20,
              [key(0.05, 0.0), key(0.40, 0.9, ease='outCubic'), key(FADE0, 0.9), key(FADE1, 0.0, ease='smooth')]),
        layer('emblem', 'Layers/AVE_Emblem.png', ex, ey, 30,
              [key(0.08, 0.0), key(0.34, 1.0, ease='outCubic'), key(FADE0, 1.0), key(FADE1, 0.0, ease='smooth')]),
        layer('emblemFlash', 'Layers/AVE_EmblemFlash.png', ex, ey, 32,
              [key(0.18, 0.0), key(0.30, 0.4, ease='outCubic'), key(0.50, 0.0, ease='smooth'),
               key(1.60, 0.0), key(1.66, 0.25, ease='outCubic'), key(1.80, 0.0, ease='smooth')]),
        layer('emblemOutlineGlow', 'Layers/AVE_EmblemOutlineGlow.png', ex - 2, ey - 2, 33,
              [key(0.30, 0.0), key(0.34, 1.0, ease='outCubic'), key(0.64, 0.0, ease='outCubic'),
               key(1.60, 0.0), key(1.66, 0.8, ease='outCubic'), key(1.86, 0.0, ease='smooth')]),
        layer('emblemTrace', '', ex - 2, ey - 2, 34, [key(0.0, 1.0)],
              frames=trace_paths, frame_start=0.0, frame_end=0.34, after='hide'),
        layer('wordmark', 'Layers/AVE_Wordmark.png', wx, wy, 40,
              [key(0.35, 0.0, dy=3.0), key(0.80, 1.0, dy=0.0, ease='outCubic'), key(FADE0, 1.0),
               key(FADE1, 0.0, ease='smooth')]),
        layer('wordmarkShine', '', wx, wy, 42, [key(0.0, 1.0)],
              frames=shine_paths, frame_start=0.64, frame_end=1.12, after='hide'),
        layer('wordmarkFlash', 'Layers/AVE_WordmarkFlash.png', wx, wy, 44,
              [key(1.58, 0.0), key(1.66, 0.4, ease='outCubic'), key(1.84, 0.0, ease='smooth')]),
        layer('subtitle', 'Layers/AVE_Subtitle.png', sx, sy, 50,
              [key(1.15, 0.0, dy=2.0), key(1.45, 1.0, dy=0.0, ease='outCubic'), key(FADE0, 1.0),
               key(FADE1, 0.0, ease='smooth')]),
        layer('glint', '', apex_x - 8, apex_y - 8, 110, [key(0.0, 1.0)],
              frames=glint_paths, frame_start=1.58, frame_end=1.82, after='hide'),
    ]

    # ---------------- baked particles (deterministic)
    rnd = random.Random(seed)
    particles = []
    ring_pts = _ring_points(emb)
    for i in range(10):  # phase 1: gold motes released while the emblem is traced
        y0, x0 = ring_pts[rnd.randrange(len(ring_pts))]
        cx0, cy0 = ex + x0, ey + y0
        ang_x = (x0 - emb.w / 2) / (emb.w / 2)
        particles.append(_p(sprite=rnd.choice([4, 6, 6]), t0=0.10 + 0.22 * i / 9 + rnd.uniform(-0.02, 0.02),
                            life=rnd.uniform(0.38, 0.55), x=cx0, y=cy0, vx=ang_x * rnd.uniform(6, 14),
                            vy=rnd.uniform(-16, -6), ay=8.0, alpha=0.95, fadeIn=0.1, fadeOut=0.6))
    for i in range(24):  # phase 3: embers rising from the subtitle / under the wordmark
        x0 = rnd.uniform(sx + 14, sx + sub.w - 14)
        y0 = rnd.uniform(sy + 3, sy + sub.h + 2) if i % 3 else rnd.uniform(wy + wm.h - 8, wy + wm.h)
        t0 = 1.12 + 0.44 * i / 23 + rnd.uniform(-0.02, 0.02)
        life = min(rnd.uniform(0.45, 0.8), 1.97 - t0)
        particles.append(_p(sprite=rnd.choice([0, 0, 1, 2, 3, 5]), t0=t0, life=life, x=x0, y=y0,
                            vx=rnd.uniform(-7, 7), vy=rnd.uniform(-36, -16), ay=14.0, alpha=1.0,
                            fadeIn=0.12, fadeOut=0.55))
    for i in range(6):  # phase 4: a few gold motes around the wordmark accent
        x0 = rnd.uniform(wx + 10, wx + wm.w - 10)
        y0 = rnd.uniform(wy + 4, wy + wm.h - 6)
        particles.append(_p(sprite=rnd.choice([4, 6]), t0=1.60 + 0.08 * i / 5, life=rnd.uniform(0.22, 0.32),
                            x=x0, y=y0, vx=rnd.uniform(-4, 4), vy=rnd.uniform(-10, -4), ay=0.0, alpha=0.9,
                            fadeIn=0.2, fadeOut=0.6))

    timeline = {
        'schema': 'avarneth.startup.timeline/1',
        'name': 'AVARNETH: VEIL OF EMBERS - startup branding',
        'version': '1.0',
        'duration': DURATION,
        'canvasWidth': CANVAS_W,
        'canvasHeight': CANVAS_H,
        'pixelScaleAt1080p': 4,
        'contentBounds': _content_bounds([(px_, py_, pub), (ex, ey, emb), (wx, wy, wm), (sx, sy, sub)], pad=6),
        'layers': layers,
        'particleSprites': part_paths,
        'particles': particles,
    }
    lockup = {'publisher': (px_, py_), 'emblem': (ex, ey), 'wordmark': (wx, wy), 'subtitle': (sx, sy)}
    return timeline, sprites, lockup


def _p(**kw):
    out = {}
    for k in ('sprite', 't0', 'life', 'x', 'y', 'vx', 'vy', 'ay', 'alpha', 'fadeIn', 'fadeOut'):
        v = kw[k]
        out[k] = int(v) if k == 'sprite' else round(float(v), 3)
    return out


def _ring_points(c: Canvas):
    import numpy as np
    from pix import inner_edge
    ring = inner_edge(c.alpha_mask())
    ys, xs = np.where(ring)
    return list(zip(ys.tolist(), xs.tolist()))


def _content_bounds(items, pad=0):
    x0 = min(x for x, y, c in items) - pad
    y0 = min(y for x, y, c in items) - pad
    x1 = max(x + c.w for x, y, c in items) + pad
    y1 = max(y + c.h for x, y, c in items) + pad
    return {'x': int(x0), 'y': int(y0), 'width': int(x1 - x0), 'height': int(y1 - y0)}
