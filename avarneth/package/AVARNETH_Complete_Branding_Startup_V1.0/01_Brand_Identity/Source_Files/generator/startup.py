"""AVARNETH startup animation: layer sprites, layout, timeline and particles (revision 2).

`build()` returns (timeline_dict, sprites, lockup) where sprites maps the contract
path (relative to Importable_Assets/, e.g. "Layers/AVE_Emblem.png") to a Canvas.
The timeline follows work/CONTRACT.md exactly and is the single source of truth
for both the preview renderer (timeline_eval.py) and Unity.

Timing principles (after the independent animation review):
* every flipbook frame lasts exactly 1/60 s;
* light leads, fills follow: the trace closes before the emblem fill is visible;
* flashes only brighten light pixels, attacks/decays are >= 0.10 s with smooth easing;
* position changes are single 1-art-px steps taken while the layer is still faint;
* particles never cross the lettering or the emblem.
"""
from __future__ import annotations

import random

import numpy as np

import emblem as emblem_mod
import wordmark as wordmark_mod
import brand
import effects as fx
from pix import Canvas

CANVAS_W, CANVAS_H = 480, 270
DURATION = 2.0
F = 1.0 / 60.0


def key(t, alpha, dx=0.0, dy=0.0, ease='linear'):
    return {'t': round(t, 4), 'alpha': round(alpha, 4), 'dx': round(dx, 4), 'dy': round(dy, 4), 'ease': ease}


def layer(id_, sprite, x, y, order, keys, frames=None, frame_start=0.0, frame_end=0.0, after='hold', fullscreen=False):
    d = {'id': id_, 'sprite': sprite or '', 'frames': frames or [], 'frameStart': round(frame_start, 4),
         'frameEnd': round(frame_end, 4), 'afterFrames': after, 'x': int(x), 'y': int(y), 'order': int(order),
         'keys': keys}
    if fullscreen:
        d['fullscreen'] = True
    return d


def build(seed=2026):
    sprites = {}

    # ---------------- art layers
    emb = emblem_mod.build(1.0, 'full')
    amask = emblem_mod.a_mask(1.0)
    wm, face = wordmark_mod.build(return_face=True)
    sub = brand.build_subtitle()
    pub = brand.build_presents_line()

    # ---------------- layout (vertical lockup, optically centred)
    gap_pub, gap_emb, gap_sub = 10, 5, 5
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
    sprites['Layers/AVE_Veil.png'] = fx.veil(CANVAS_W, CANVAS_H, cx=CANVAS_W / 2, cy=ey + 66, rx=330, ry=190)
    gw, gh = 96, 106
    sprites['Layers/AVE_EmblemGlow.png'] = fx.radial_glow(gw, gh, 46, 51)
    gx, gy = ex + emb.w // 2 - gw // 2, ey + emb.h // 2 - gh // 2
    sprites['Layers/AVE_EmblemFlash.png'] = fx.highlight_flash(emb)
    sprites['Layers/AVE_EmblemOutlineGlow.png'] = fx.emblem_outline_glow(emb, margin=2)
    sprites['Layers/AVE_WordmarkFlash.png'] = fx.highlight_flash(wm, restrict=face)

    def seq(name, frames):
        paths = []
        for i, f in enumerate(frames):
            p = f'Frames/AVE_{name}_{i:02d}.png'
            sprites[p] = f
            paths.append(p)
        return paths

    trace_paths = seq('EmblemTrace', fx.emblem_trace_frames(emb, amask, 12, 4, margin=2))
    shine_paths = seq('WordmarkShine', fx.shine_frames(face, n=28))
    glint_paths = seq('Glint', fx.glint_frames(10))
    apex_x = ex + emb.w // 2
    apex_y = ey + int(np.where(emb.alpha_mask()[:, emb.w // 2])[0].min()) + 2

    parts = fx.particle_sprites()
    part_paths = []
    for i, p in enumerate(parts):
        path = f'Particles/AVE_Particle_{i:02d}.png'
        sprites[path] = p
        part_paths.append(path)

    FADE0, FADE1 = 1.74, 2.0
    n_tr, n_sh, n_gl = len(trace_paths), len(shine_paths), len(glint_paths)
    tr0 = 0.0
    sh0 = 38 * F
    gl0 = 95 * F

    layers = [
        layer('veil', 'Layers/AVE_Veil.png', 0, 0, 0,
              [key(0.0, 0.0), key(0.30, 1.0, ease='smooth'), key(FADE0 - 0.04, 1.0), key(FADE1, 0.0, ease='smooth')],
              fullscreen=True),
        layer('emblemGlow', 'Layers/AVE_EmblemGlow.png', gx, gy, 10,
              [key(0.16, 0.0), key(0.34, 0.35, ease='smooth'), key(1.60, 0.35), key(1.72, 0.6, ease='smooth'),
               key(FADE1, 0.0, ease='smooth')]),
        layer('publisher', 'Layers/AVE_Publisher.png', px_, py_, 20,
              [key(0.30, 0.0), key(0.60, 0.65, ease='smooth'), key(FADE0, 0.65), key(FADE1, 0.0, ease='smooth')]),
        layer('emblem', 'Layers/AVE_Emblem.png', ex, ey, 30,
              [key(0.16, 0.0), key(0.34, 1.0, ease='smooth'), key(FADE0, 1.0), key(FADE1, 0.0, ease='smooth')]),
        layer('emblemFlash', 'Layers/AVE_EmblemFlash.png', ex, ey, 32,
              [key(0.22, 0.0), key(0.32, 0.55, ease='smooth'), key(0.50, 0.0, ease='smooth'),
               key(1.64, 0.0), key(1.76, 0.4, ease='smooth'), key(1.90, 0.0, ease='smooth')]),
        layer('emblemOutlineGlow', 'Layers/AVE_EmblemOutlineGlow.png', ex - 2, ey - 2, 33,
              [key(0.24, 0.0), key(0.34, 0.9, ease='smooth'), key(0.60, 0.0, ease='smooth'),
               key(1.62, 0.0), key(1.72, 0.6, ease='smooth'), key(1.86, 0.0, ease='smooth')]),
        layer('emblemTrace', '', ex - 2, ey - 2, 34, [key(0.0, 0.0), key(0.05, 1.0, ease='outCubic')],
              frames=trace_paths, frame_start=tr0, frame_end=tr0 + n_tr * F, after='hide'),
        layer('wordmark', 'Layers/AVE_Wordmark.png', wx, wy, 40,
              [key(0.35, 0.0, dy=1.0), key(0.44, 0.25, dy=1.0), key(0.445, 0.27, dy=0.0, ease='step'),
               key(0.80, 1.0, ease='outCubic'), key(FADE0, 1.0), key(FADE1, 0.0, ease='smooth')]),
        layer('wordmarkFlash', 'Layers/AVE_WordmarkFlash.png', wx, wy, 41,
              [key(0.36, 0.0, dy=1.0), key(0.44, 0.5, dy=1.0, ease='smooth'), key(0.445, 0.5, dy=0.0, ease='step'),
               key(0.62, 0.0, ease='smooth'),
               key(1.66, 0.0), key(1.78, 0.4, ease='smooth'), key(1.92, 0.0, ease='smooth')]),
        layer('wordmarkShine', '', wx, wy, 42, [key(0.0, 1.0)],
              frames=shine_paths, frame_start=sh0, frame_end=sh0 + n_sh * F, after='hide'),
        layer('subtitle', 'Layers/AVE_Subtitle.png', sx, sy, 50,
              [key(1.15, 0.0, dy=1.0), key(1.22, 0.22, dy=1.0), key(1.225, 0.24, dy=0.0, ease='step'),
               key(1.45, 1.0, ease='outCubic'), key(FADE0, 1.0), key(FADE1, 0.0, ease='smooth')]),
        layer('glint', '', apex_x - 8, apex_y - 8, 110, [key(0.0, 1.0)],
              frames=glint_paths, frame_start=gl0, frame_end=gl0 + n_gl * F, after='hide'),
    ]

    # ---------------- baked particles: deterministic, rejected if they would cross artwork
    occ = np.zeros((CANVAS_H, CANVAS_W), bool)
    for (cv, x0, y0) in ((emb, ex, ey), (wm, wx, wy), (sub, sx, sy), (pub, px_, py_)):
        occ[y0:y0 + cv.h, x0:x0 + cv.w] |= cv.alpha_mask()
    occ_d = occ.copy()
    occ_d[1:] |= occ[:-1]
    occ_d[:-1] |= occ[1:]
    occ_d[:, 1:] |= occ[:, :-1]
    occ_d[:, :-1] |= occ[:, 1:]

    def clear_path(p, spr):
        h, w = spr.h, spr.w
        t = 0.0
        while t < p['life']:
            u = t / p['life']
            fin = min(1.0, u / p['fadeIn']) if p['fadeIn'] > 0 else 1.0
            fout = max(0.0, (1 - u) / p['fadeOut']) if (p['fadeOut'] > 0 and u > 1 - p['fadeOut']) else 1.0
            if p['alpha'] * fin * fout > 0.03:
                x = int(np.floor(p['x'] + p['vx'] * t + 0.5)) - w // 2
                y = int(np.floor(p['y'] + p['vy'] * t + 0.5 * p['ay'] * t * t + 0.5)) - h // 2
                if x < 0 or y < 0 or x + w > CANVAS_W or y + h > CANVAS_H:
                    return False
                if occ_d[y:y + h, x:x + w].any():
                    return False
            t += F
        return True

    rnd = random.Random(seed)
    particles = []

    def emit(n, make):
        made, tries = 0, 0
        while made < n and tries < 20000:
            tries += 1
            p = make(made, n)
            if clear_path(p, parts[p['sprite']]):
                particles.append(p)
                made += 1
        if made < n:
            raise RuntimeError(f'particle emitter produced only {made}/{n} clear paths')

    em_mask = emb.alpha_mask()
    ring = [(y, x) for y, x in zip(*np.where(em_mask))
            if 0 < y < emb.h - 1 and 0 < x < emb.w - 1 and not em_mask[y - 1:y + 2, x - 1:x + 2].all()]

    def mote(i, n):   # phase 1: gold motes lifting off the emblem rim as the light passes
        y0, x0 = ring[rnd.randrange(len(ring))]
        dx_, dy_ = x0 - emb.w / 2, y0 - emb.h / 2
        nrm = max(1e-6, (dx_ * dx_ + dy_ * dy_) ** 0.5)
        ux, uy = dx_ / nrm, dy_ / nrm
        sp = rnd.uniform(6, 12)
        return _p(sprite=rnd.choice([4, 4, 5]), t0=0.08 + 0.20 * i / max(1, n - 1), life=rnd.uniform(0.35, 0.5),
                  x=ex + x0 + ux * 4, y=ey + y0 + uy * 4, vx=ux * sp, vy=uy * sp - rnd.uniform(4, 9), ay=6.0,
                  alpha=0.9, fadeIn=0.15, fadeOut=0.6)

    lock_x0 = min(wx, sx)                        # horizontal extent of the lettering
    lock_x1 = max(wx + wm.w, sx + sub.w)

    def ember(i, n):  # phase 3: a few embers beside the lockup and smouldering just below the subtitle
        mode = i % 3
        if mode == 0:
            x0, y0 = rnd.uniform(lock_x0 - 26, lock_x0 - 6), rnd.uniform(sy - 14, sy + 10)
            vx, vy = rnd.uniform(-8, 1), rnd.uniform(-28, -12)
        elif mode == 1:
            x0, y0 = rnd.uniform(lock_x1 + 6, lock_x1 + 26), rnd.uniform(sy - 14, sy + 10)
            vx, vy = rnd.uniform(-1, 8), rnd.uniform(-28, -12)
        else:
            x0, y0 = rnd.uniform(sx + 20, sx + sub.w - 20), sy + sub.h + rnd.uniform(3, 9)
            vx, vy = rnd.uniform(-6, 6), rnd.uniform(-7, -2)
        t0 = 1.15 + 0.40 * i / max(1, n - 1) + rnd.uniform(-0.02, 0.02)
        return _p(sprite=rnd.choice([0, 1, 2, 2, 3]), t0=t0, life=min(rnd.uniform(0.40, 0.70), 1.97 - t0),
                  x=x0, y=y0, vx=vx, vy=vy, ay=8.0 if mode < 2 else 0.0, alpha=1.0, fadeIn=0.15, fadeOut=0.55)

    def accent(i, n):  # phase 4: a few gold motes released beside the emblem as the accent passes
        side = -1 if i % 2 == 0 else 1
        x0 = ex + emb.w / 2 + side * rnd.uniform(emb.w / 2 + 3, emb.w / 2 + 10)
        y0 = ey + rnd.uniform(16, emb.h - 16)
        return _p(sprite=rnd.choice([4, 5]), t0=1.62 + 0.08 * i / max(1, n - 1), life=rnd.uniform(0.22, 0.30),
                  x=x0, y=y0, vx=side * rnd.uniform(2, 6), vy=rnd.uniform(-10, -4), ay=0.0, alpha=0.85,
                  fadeIn=0.2, fadeOut=0.6)

    emit(8, mote)
    emit(12, ember)
    emit(4, accent)

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


def _content_bounds(items, pad=0):
    x0 = min(x for x, y, c in items) - pad
    y0 = min(y for x, y, c in items) - pad
    x1 = max(x + c.w for x, y, c in items) + pad
    y1 = max(y + c.h for x, y, c in items) + pad
    return {'x': int(x0), 'y': int(y0), 'width': int(x1 - x0), 'height': int(y1 - y0)}
