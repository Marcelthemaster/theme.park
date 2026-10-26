"""Reference evaluator + compositor for Animation_Timeline.json (see CONTRACT.md).

Implements exactly the semantics the Unity runtime implements, so the preview
video shows what Unity will show (alpha blending, pixel-snapped positions).
"""
from __future__ import annotations

import math

import numpy as np
from pix import alpha_over


def f32(v):
    """Unity stores timeline values and the timeline time as float32; mirror that exactly."""
    return float(np.float32(v))


def ease(name, u):
    u = min(1.0, max(0.0, u))
    if name == 'inCubic':
        return u ** 3
    if name == 'outCubic':
        return 1 - (1 - u) ** 3
    if name == 'inOutCubic':
        return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2
    if name == 'smooth':
        return u * u * (3 - 2 * u)
    if name == 'step':
        return 0.0 if u < 1 else 1.0
    return u


def snap(v):
    return int(math.floor(v + 0.5))


def eval_keys(keys, t):
    t = f32(t)
    keys = [{'t': f32(k['t']), 'alpha': f32(k['alpha']), 'dx': f32(k['dx']), 'dy': f32(k['dy']), 'ease': k.get('ease', 'linear')}
            for k in keys]
    if t <= keys[0]['t']:
        k = keys[0]
        return k['alpha'], k['dx'], k['dy']
    if t >= keys[-1]['t']:
        k = keys[-1]
        return k['alpha'], k['dx'], k['dy']
    for a, b in zip(keys, keys[1:]):
        if a['t'] <= t < b['t']:
            span = b['t'] - a['t']
            u = (t - a['t']) / span if span > 0 else 1.0
            e = ease(b.get('ease', 'linear'), u)
            return (a['alpha'] + (b['alpha'] - a['alpha']) * e,
                    a['dx'] + (b['dx'] - a['dx']) * e,
                    a['dy'] + (b['dy'] - a['dy']) * e)
    k = keys[-1]
    return k['alpha'], k['dx'], k['dy']


def flipbook_index(t, start, end, n, after):
    """>=0 frame index, -1 static sprite, -2 hidden."""
    if n == 0:
        return -1
    t, start, end = f32(t), f32(start), f32(end)
    if t < start:
        return -2
    if t < end:
        i = int(math.floor((t - start) / (end - start) * n))
        return max(0, min(n - 1, i))
    if after == 'hold':
        return n - 1
    if after == 'sprite':
        return -1
    return -2


def eval_particle(p, t):
    t = f32(t)
    p = {k: (v if k == 'sprite' else f32(v)) for k, v in p.items()}
    if not (p['t0'] <= t < p['t0'] + p['life']):
        return None
    tau = t - p['t0']
    u = tau / p['life']
    x = p['x'] + p['vx'] * tau
    y = p['y'] + p['vy'] * tau + 0.5 * p['ay'] * tau * tau
    fin = min(1.0, u / p['fadeIn']) if p['fadeIn'] > 0 else 1.0
    fout = max(0.0, (1 - u) / p['fadeOut']) if (p['fadeOut'] > 0 and u > 1 - p['fadeOut']) else 1.0
    return x, y, p['alpha'] * fin * fout


def layer_state(L, t):
    alpha, dx, dy = eval_keys(L['keys'], t)
    idx = flipbook_index(t, L['frameStart'], L['frameEnd'], len(L['frames']), L['afterFrames'])
    if idx == -2:
        sprite = None
    elif idx == -1:
        sprite = L['sprite'] or None
    else:
        sprite = L['frames'][idx]
    visible = sprite is not None and alpha > 0.001
    return visible, sprite, idx, snap(L['x'] + dx), snap(L['y'] + dy), alpha


def render(timeline, sprite_arrays, t, base=None):
    """Composite the overlay at time t onto `base` (HxWx4) or a transparent canvas."""
    W, H = timeline['canvasWidth'], timeline['canvasHeight']
    out = np.zeros((H, W, 4), np.uint8) if base is None else base.copy()
    if t >= timeline['duration']:
        return out
    layers = sorted(enumerate(timeline['layers']), key=lambda il: (il[1]['order'], il[0]))
    back = [L for _, L in layers if L['order'] < 100]
    front = [L for _, L in layers if L['order'] >= 100]

    def draw_layers(ls):
        for L in ls:
            vis, spr, idx, x, y, a = layer_state(L, t)
            if vis:
                alpha_over(out, sprite_arrays[spr], x, y, opacity=min(1.0, a))

    draw_layers(back)
    for p in timeline['particles']:
        st = eval_particle(p, t)
        if st is None:
            continue
        x, y, a = st
        if a <= 0.001:
            continue
        arr = sprite_arrays[timeline['particleSprites'][p['sprite']]]
        h, w = arr.shape[:2]
        alpha_over(out, arr, snap(x) - w // 2, snap(y) - h // 2, opacity=min(1.0, a))
    draw_layers(front)
    return out


def csv_rows(timeline, fps):
    """Same CSV as the C# math test harness: frame,kind,id,visible,index,x,y,alpha."""
    rows = []
    n = int(math.floor(timeline['duration'] * fps))
    for i in range(n + 1):
        t = i / fps
        done = t >= timeline['duration']   # contract 3.3: finished overlay shows nothing
        for L in timeline['layers']:
            alpha, dx, dy = eval_keys(L['keys'], t)
            idx = flipbook_index(t, L['frameStart'], L['frameEnd'], len(L['frames']), L['afterFrames'])
            vis = 1 if (not done and alpha > 0.001 and idx != -2 and (idx != -1 or L['sprite'])) else 0
            rows.append(f"{i},L,{L['id']},{vis},{idx},{snap(L['x'] + dx)},{snap(L['y'] + dy)},{alpha:.4f}")
        for j, p in enumerate(timeline['particles']):
            st = eval_particle(p, t)
            if st is None:
                rows.append(f"{i},P,{j},0,{p['sprite']},0,0,0.0000")
                continue
            x, y, a = st
            rows.append(f"{i},P,{j},{1 if (a > 0.001 and not done) else 0},{p['sprite']},{snap(x)},{snap(y)},{a:.4f}")
    return rows
