"""AVARNETH wordmark - custom forged pixel capitals (no font is used). Revision 2.

Glyphs are constructed from polygons on the native grid with clean diagonal
slopes (3:1 for A/V, 2:1 for N/R legs) and pointed spur serifs. Symmetric
letters (A, V, T, H) are built from their left half and mirrored, so they are
pixel-exact symmetric. Shading uses a 4x supersampled distance field: chiseled
lit/shaded facets inside each stroke and edge colours chosen from the true edge
normal (top / left-facing / right-facing / bottom), so diagonals get continuous
rims instead of a highlight bead on every step. A 2 px dark-iron extrusion and a
1 px outline finish the letters. Each A carries the emblem's motif in its lower
counter: a tiny gate glowing with an ember core.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage
from pix import Canvas, col, poly_mask, mirror_x, outline

CAP = 32          # cap height in art px
UP = 5            # headroom above the cap line (A spires)
DOWN = 6          # room below the baseline (extrusion + outline)
PAD = 2
STEM = 6          # main stem width
THIN = 4          # bars / hairlines
LIGHT = (-0.5, -0.86)
EMBER_GATES = False


def _P(w, h, pts, k=1, oy=0):
    return poly_mask(w * k, h * k, [(x * k, (y + oy) * k) for x, y in pts])


def _flare_foot(x0, x1, y=CAP, ext=3, h=5):
    return [[(x0 - ext, y), (x0, y - h), (x0, y)], [(x1, y), (x1, y - h), (x1 + ext, y)]]


def _flare_head(x0, x1, y=0, ext=3, h=5):
    return [[(x0 - ext, y), (x0, y), (x0, y + h)], [(x1, y + h), (x1, y), (x1 + ext, y)]]


def _stem(polys, x0, w, top=True, foot=True, y0=0, y1=CAP):
    polys.append([(x0, y0), (x0 + w, y0), (x0 + w, y1), (x0, y1)])
    if foot:
        polys += _flare_foot(x0, x0 + w, y1)
    if top:
        polys += _flare_head(x0, x0 + w, y0)


def _A():
    w = 27
    c = w / 2.0
    apex = -4.0
    t = 5.5                           # horizontal leg thickness
    outer = [(c, apex), (c + (CAP - apex) / 3.0, CAP), (c - (CAP - apex) / 3.0, CAP)]
    ia = apex + 3 * t
    inner = [(c, ia), (c + (CAP - ia) / 3.0, CAP + 0.01), (c - (CAP - ia) / 3.0, CAP + 0.01)]
    lx = c - (CAP - apex) / 3.0
    bar = [[(0, 20), (w, 20), (w, 23), (0, 23)]]                       # crossbar (clipped to outer)
    feet = [[(lx - 3, CAP), (lx + 1.2, CAP - 5), (lx + t + 1.2, CAP)]]  # left foot, mirrored
    return {'w': w, 'sym': True, 'outer': outer, 'inner': inner, 'bar': bar, 'feet': feet}


def _V():
    w = 27
    c = w / 2.0
    t = 5.5
    tip = CAP + 4.0
    outer = [(c - tip / 3.0, 0), (c + tip / 3.0, 0), (c, tip)]
    it = tip - 3 * t
    inner = [(c - (it + 10) / 3.0, -10), (c + (it + 10) / 3.0, -10), (c, it)]
    lx = c - tip / 3.0
    heads = [[(lx - 3, 0), (lx + t + 1.2, 0), (lx + 1.2, 5)]]
    return {'w': w, 'sym': True, 'outer': outer, 'inner': inner, 'clip_bottom': True, 'feet': heads}


def _R():
    polys = []
    _stem(polys, 3, STEM)
    bowl_out = [(3, 0), (17, 0), (21, 2), (23, 5), (23, 13), (21, 16), (17, 18), (3, 18)]
    bowl_in = [(3 + STEM, THIN), (15, THIN), (17, 6), (17, 12), (15, 18 - THIN), (3 + STEM, 18 - THIN)]
    leg = [(12, 16), (19, 16), (25, CAP - 1), (27, CAP), (19, CAP)]
    return {'w': 28, 'sym': False, 'polys': polys + [leg], 'ring': (bowl_out, bowl_in)}


def _N():
    w = 29
    polys = []
    sw = 5
    _stem(polys, 3, sw, top=False)
    _stem(polys, w - 3 - sw, sw, foot=False)
    diag = [(3, 0), (3 + 7.5, 0), (3 + 7.5 + (CAP / 2.0), CAP), (3 + CAP / 2.0, CAP)]
    polys.append([(0, 0), (3, 0), (3, 4)])
    return {'w': w, 'sym': False, 'polys': polys, 'diag': (diag, [(3, -1), (w - 3, -1), (w - 3, CAP + 1), (3, CAP + 1)])}


def _E():
    w = 23
    polys = []
    _stem(polys, 3, STEM, top=False, foot=False)
    polys.append([(0, 0), (w, 0), (w, 7), (w - 2, 3), (3 + STEM, THIN), (3, THIN), (3, 4)])
    polys.append([(3, 14), (w - 5, 14), (w - 3, 16), (w - 5, 18), (3, 18)])
    polys.append([(0, CAP), (3, CAP - 4), (3, CAP - THIN), (3 + STEM, CAP - THIN), (w - 2, CAP - 3), (w, CAP - 7), (w, CAP)])
    return {'w': w, 'sym': False, 'polys': polys}


def _T():
    w = 27
    c = w / 2.0
    polys = [[(0, 7), (0, 0), (c, 0), (c, 3), (2, 3)], [(0, 0), (c, 0), (c, THIN), (0, THIN)]]
    polys.append([(c - STEM / 2, 0), (c, 0), (c, CAP), (c - STEM / 2, CAP)])
    polys.append([(c - STEM / 2 - 3, CAP), (c - STEM / 2, CAP - 5), (c - STEM / 2, CAP)])
    return {'w': w, 'sym': True, 'polys': polys}


def _H():
    w = 29
    c = w / 2.0
    polys = []
    _stem(polys, 3, STEM)
    polys.append([(3, 14), (c, 14), (c, 18), (3, 18)])
    return {'w': w, 'sym': True, 'polys': polys}


GLYPHS = {'A': _A, 'V': _V, 'R': _R, 'N': _N, 'E': _E, 'T': _T, 'H': _H}


def glyph_mask(ch, k=1):
    """Local glyph mask (Ht*k, w*k) with the cap line at y = UP+PAD."""
    g = GLYPHS[ch]()
    w = g['w']
    Ht = CAP + UP + DOWN + 2 * PAD
    oy = UP + PAD
    m = np.zeros((Ht * k, w * k), bool)
    if 'outer' in g:
        o = _P(w, Ht, g['outer'], k, oy)
        if g.get('clip_bottom'):
            o &= _P(w, Ht, [(-10, -10), (w + 10, -10), (w + 10, CAP), (-10, CAP)], k, oy)
        m |= o & ~_P(w, Ht, g['inner'], k, oy)
        for p in g.get('bar', []):
            m |= _P(w, Ht, p, k, oy) & o
        for p in g.get('feet', []):
            m |= _P(w, Ht, p, k, oy)
    for p in g.get('polys', []):
        m |= _P(w, Ht, p, k, oy)
    if 'ring' in g:
        m |= _P(w, Ht, g['ring'][0], k, oy) & ~_P(w, Ht, g['ring'][1], k, oy)
    if 'diag' in g:
        m |= _P(w, Ht, g['diag'][0], k, oy) & _P(w, Ht, g['diag'][1], k, oy)
    if g['sym']:
        m = mirror_x(m)
    return m, w, g


def _gaps(prev, cur, rows):
    """Per-row horizontal gap between the right edge of prev and left edge of cur."""
    out = []
    for y in rows:
        a = np.where(prev[y])[0]
        b = np.where(cur[y])[0]
        if len(a) and len(b):
            out.append(b.min() - a.max() - 1)
    return out


def layout(text, target=7.0, min_gap=2):
    """Optical spacing: mean gap over the cap band ~= target, never closer than min_gap."""
    Ht = CAP + UP + DOWN + 2 * PAD
    Wt = 40 * len(text) + 40
    full = np.zeros((Ht, Wt), bool)
    letters = []
    oy = UP + PAD
    cap_rows = range(oy + 1, oy + CAP - 1)
    all_rows = range(0, Ht)
    x = PAD + 3
    for i, ch in enumerate(text):
        g, w, _ = glyph_mask(ch)
        if i:
            best = None
            prev_only = full.copy()
            for off in range(0, Wt - w):
                cand = np.zeros_like(full)
                cand[:, off:off + w] = g
                if (cand & prev_only).any():
                    continue
                gp = _gaps(prev_only, cand, all_rows)
                if not gp or min(gp) < min_gap:
                    continue
                mean = np.mean(_gaps(prev_only, cand, cap_rows) or [99])
                if mean >= target:
                    best = off
                    break
            x = best
        cur = np.zeros_like(full)
        cur[:, x:x + w] = g
        full |= cur
        letters.append((ch, x, w))
    return full, letters


def normals(letters, H, W, k=4):
    """Per-pixel mean outward normal (nx, ny) from a k-x supersampled distance field."""
    nx = np.zeros((H, W))
    ny = np.zeros((H, W))
    cnt = np.zeros((H, W))
    for ch, x, w in letters:
        big, _, _ = glyph_mask(ch, k)
        d = ndimage.distance_transform_edt(np.pad(big, 1))[1:-1, 1:-1]
        d = ndimage.gaussian_filter(d, 1.0)
        gy, gx = np.gradient(d)
        n = np.hypot(gx, gy) + 1e-6
        ox, oy_ = -gx / n, -gy / n
        h = big.shape[0] // k
        for arr, dst in ((np.where(big, ox, 0), nx), (np.where(big, oy_, 0), ny), (big.astype(float), cnt)):
            dst[:h, x:x + w] += arr.reshape(h, k, w, k).sum(axis=(1, 3))
    cnt = np.maximum(cnt, 1)
    return nx / cnt, ny / cnt


def shade(mask, letters, ember_gates=EMBER_GATES, ext_depth=2):
    H, W = mask.shape
    c = Canvas(W, H)
    Y = np.arange(H)[:, None].repeat(W, 1) - (UP + PAD)

    # dark-iron extrusion: lit first row, darker rows below (production: 2 px)
    ext = np.zeros_like(mask)
    acc = mask.copy()
    for k in range(ext_depth):
        e = np.zeros_like(mask)
        e[1:] = acc[:-1]
        e &= ~acc
        c.put(e, col('iron', 4 if k == 0 else (2 if k == ext_depth - 1 else 3)))
        ext |= e
        acc |= e
    e1, e2 = ext, np.zeros_like(ext)

    nx, ny = normals(letters, H, W)
    lx, ly = LIGHT
    ndl = nx * lx + ny * ly
    idx = np.where(ndl > 0.28, 7, np.where(ndl > -0.22, 6, 4))
    idx = np.where(Y < 0, np.minimum(idx + 1, 8), idx)
    c.put_index(mask, 'gold', idx)
    edge = mask & ~ndimage.binary_erosion(mask, ndimage.generate_binary_structure(2, 1))
    top = edge & (ny < -0.8)
    left = edge & (nx < -0.3) & ~top
    right = edge & (nx > 0.3) & ~top
    bottom = edge & (ny > 0.5) & ~left & ~right
    c.put(left, col('gold', 8))
    c.put(right, col('gold', 4))
    c.put(right & (ny > 0.2), col('gold', 3))
    c.put(bottom, col('gold', 2))
    c.put(top, col('gold', 9))

    if ember_gates:
        _ember_gates(c, mask, letters)
    sil = mask | e1 | e2
    c.put(outline(sil), col('iron', 0))
    return c, e1 | e2


def _ember_gates(c, mask, letters):
    """A tiny glowing gate in the lower counter of every A (links wordmark and emblem)."""
    oy = UP + PAD
    for ch, x, w in letters:
        if ch != 'A':
            continue
        cx = x + w // 2
        y0, y1 = oy + 25, oy + CAP          # below the crossbar to the baseline
        for y in range(y0, y1):
            row = mask[y]
            span = [xx for xx in range(cx - 8, cx + 9)
                    if not row[xx] and any(row[xx - j] for j in range(1, 9)) and any(row[xx + j] for j in range(1, 9))]
            if len(span) < 3:
                continue
            a, b = min(span) + 1, max(span) - 1           # keep a 1 px dark gap to the legs
            rel = (y - y0) / max(1, (y1 - y0 - 1))
            k = 4 if rel < 0.3 else (5 if rel < 0.65 else 6)
            for xx in range(a, b + 1):
                c.px(xx, y, col('ember', k))
            c.px(a - 1, y, col('iron', 0))
            c.px(b + 1, y, col('iron', 0))


def build(text='AVARNETH', return_face=False, ember_gates=EMBER_GATES, ext_depth=2):
    """Returns the wordmark canvas trimmed to its pixels (and optionally the face mask)."""
    m, letters = layout(text)
    c, _ext = shade(m, letters, ember_gates=ember_gates, ext_depth=ext_depth)
    a = c.a
    ys, xs = np.where(a[..., 3] > 0)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    out = Canvas(x1 - x0, y1 - y0)
    out.a = a[y0:y1, x0:x1].copy()
    if return_face:
        face = m[y0:y1, x0:x1].copy()
        return out, face
    return out


if __name__ == '__main__':
    import sys
    c = build()
    c.save(sys.argv[1] if len(sys.argv) > 1 else 'wordmark.png')
    print(c.w, c.h)
