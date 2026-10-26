"""AVARNETH wordmark - custom forged pixel capitals (no font is used).

Glyphs are built from polygons on an integer grid with clean diagonal slopes
(3:1 for A/V, 2:1 for N/R legs), wedge serifs, then shaded as one piece:
banded aged-gold face, 1px bevel, a dark-iron extrusion plate and a dark
outline. The A's apex rises above the cap line like a mountain spire,
echoing the emblem.
"""
from __future__ import annotations

import numpy as np
from pix import Canvas, col, poly_mask, rect_mask, outline, inner_edge, ellipse_mask

CAP = 32          # cap height in art px
UP = 6            # extra headroom above the cap line (A spires)
DOWN = 6          # room below the baseline (extrusion + outline)
PAD = 3


_K = 1  # supersampling factor used when rendering the shading field


def _P(w, h, pts, ox, oy):
    return poly_mask(w, h, [((x + ox) * _K, (y + oy) * _K) for x, y in pts])


def flare_foot(x0, x1, y=CAP, ext=3, h=5):
    """Pointed spur serifs at the foot of a stem spanning x0..x1."""
    return [[(x0 - ext, y), (x0, y - h), (x0, y)], [(x1, y), (x1, y - h), (x1 + ext, y)]]


def flare_head(x0, x1, y=0, ext=3, h=5):
    return [[(x0 - ext, y), (x0, y), (x0, y + h)], [(x1, y + h), (x1, y), (x1 + ext, y)]]


def _polys(W, H, polys, ox, oy):
    m = np.zeros((H, W), bool)
    for p in polys:
        m |= _P(W, H, p, ox, oy)
    return m


STEM = 6      # main stem width
THIN = 4      # thin stroke / bar thickness


def stem(W, H, ox, oy, x0, w, top=True, foot=True, y0=0, y1=CAP):
    m = _P(W, H, [(x0, y0), (x0 + w, y0), (x0 + w, y1), (x0, y1)], ox, oy)
    if foot:
        m |= _polys(W, H, flare_foot(x0, x0 + w, y1), ox, oy)
    if top:
        m |= _polys(W, H, flare_head(x0, x0 + w, y0), ox, oy)
    return m


def glyph_A(W, H, ox, oy):
    w = 27
    c = w / 2.0
    apex = -6.0
    outer = _P(W, H, [(c, apex), (c + (CAP - apex) / 3.0, CAP), (c - (CAP - apex) / 3.0, CAP)], ox, oy)
    t = 6.5
    inner_apex = apex + 3 * t
    inner = _P(W, H, [(c, inner_apex), (c + (CAP - inner_apex) / 3.0, CAP + 0.01),
                      (c - (CAP - inner_apex) / 3.0, CAP + 0.01)], ox, oy)
    m = outer & ~inner
    m |= _P(W, H, [(0, 20), (w, 20), (w, 23), (0, 23)], ox, oy) & outer
    lx0 = c - (CAP - apex) / 3.0
    rx1 = c + (CAP - apex) / 3.0
    m |= _P(W, H, [(lx0 - 3, CAP), (lx0 + 1.2, CAP - 5), (lx0 + t + 1.5, CAP), ], ox, oy)
    m |= _P(W, H, [(rx1 - t - 1.5, CAP), (rx1 - 1.2, CAP - 5), (rx1 + 3, CAP)], ox, oy)
    return m, w


def glyph_V(W, H, ox, oy):
    w = 27
    c = w / 2.0
    t = 6.5
    tip = CAP + 4.0
    outer = _P(W, H, [(c - tip / 3.0, 0), (c + tip / 3.0, 0), (c, tip)], ox, oy)
    outer &= _P(W, H, [(-10, -10), (w + 10, -10), (w + 10, CAP), (-10, CAP)], ox, oy)
    inner_tip = tip - 3 * t
    inner = _P(W, H, [(c - (inner_tip + 10) / 3.0, -10), (c + (inner_tip + 10) / 3.0, -10), (c, inner_tip)], ox, oy)
    m = outer & ~inner
    lx = c - tip / 3.0
    rx = c + tip / 3.0
    m |= _P(W, H, [(lx - 3, 0), (lx + t + 1.5, 0), (lx + 1.2, 5)], ox, oy)
    m |= _P(W, H, [(rx - t - 1.5, 0), (rx + 3, 0), (rx - 1.2, 5)], ox, oy)
    return m, w


def glyph_R(W, H, ox, oy):
    m = stem(W, H, ox, oy, 3, STEM)
    bowl_out = _P(W, H, [(3, 0), (17, 0), (21, 2), (23, 5), (23, 13), (21, 16), (17, 18), (3, 18)], ox, oy)
    bowl_in = _P(W, H, [(3 + STEM, THIN), (15, THIN), (17, 6), (17, 12), (15, 18 - THIN), (3 + STEM, 18 - THIN)], ox, oy)
    m |= bowl_out & ~bowl_in
    m |= _P(W, H, [(12, 16), (19, 16), (25, CAP - 1), (27, CAP), (19, CAP)], ox, oy)
    return m, 27


def glyph_N(W, H, ox, oy):
    w = 28
    m = stem(W, H, ox, oy, 3, THIN, top=False)
    m |= stem(W, H, ox, oy, w - 3 - THIN, THIN, foot=False)
    m |= _P(W, H, [(3, 0), (3 + 7, 0), (3 + 7 + CAP / 2.0, CAP), (3 + CAP / 2.0, CAP)], ox, oy) & \
        _P(W, H, [(3, -1), (w - 3, -1), (w - 3, CAP + 1), (3, CAP + 1)], ox, oy)
    m |= _P(W, H, [(0, 0), (3, 0), (3, 4)], ox, oy)
    return m, w


def glyph_E(W, H, ox, oy):
    w = 23
    m = stem(W, H, ox, oy, 3, STEM, top=False, foot=False)
    m |= _P(W, H, [(0, 0), (w, 0), (w, 7), (w - 2, 3), (3 + STEM, THIN), (3, THIN), (3, 4)], ox, oy)
    m |= _P(W, H, [(3, 14), (w - 5, 14), (w - 3, 16), (w - 5, 18), (3, 18)], ox, oy)
    m |= _P(W, H, [(0, CAP), (3, CAP - 4), (3, CAP - THIN), (3 + STEM, CAP - THIN), (w - 2, CAP - 3), (w, CAP - 7), (w, CAP)], ox, oy)
    return m, w


def glyph_T(W, H, ox, oy):
    w = 26
    c = w / 2.0
    m = _P(W, H, [(0, 7), (0, 0), (w, 0), (w, 7), (w - 2, 3), (2, 3)], ox, oy)
    m |= _P(W, H, [(0, 0), (w, 0), (w, THIN), (0, THIN)], ox, oy)
    m |= stem(W, H, ox, oy, c - STEM / 2, STEM, top=False)
    return m, w


def glyph_H(W, H, ox, oy):
    w = 28
    m = stem(W, H, ox, oy, 3, STEM)
    m |= stem(W, H, ox, oy, w - 3 - STEM, STEM)
    m |= _P(W, H, [(3, 14), (w - 3, 14), (w - 3, 18), (3, 18)], ox, oy)
    return m, w


GLYPHS = {'A': glyph_A, 'V': glyph_V, 'R': glyph_R, 'N': glyph_N, 'E': glyph_E, 'T': glyph_T, 'H': glyph_H}


def layout(text, gap=4, diag_gap=3):
    """Place glyph masks left to right with auto-kerning (min horizontal gap per row)."""
    Wt = 60 * len(text) + 40
    Ht = CAP + UP + DOWN + 2 * PAD
    oy = UP + PAD
    full = np.zeros((Ht, Wt), bool)
    letters = []
    x = PAD + 3
    prev = None
    prev_ch = None
    for ch in text:
        tmp, adv = GLYPHS[ch](Wt, Ht, 0, oy)
        if prev is not None:
            # find smallest offset so every row keeps >= gap between prev and this glyph
            best = None
            for off in range(0, Wt - 60):
                cand = np.zeros_like(tmp)
                cand[:, off:] = tmp[:, :Wt - off]
                # dilate prev horizontally by gap
                pd = prev.copy()
                g_ = gap + (2 if (prev_ch + ch) in ('AV', 'VA') else 0)
                for k in range(1, g_ + 1):
                    pd[:, k:] |= prev[:, :-k]
                if not (pd & cand).any():
                    best = off
                    break
            x = best
        g = np.zeros_like(tmp)
        g[:, x:] = tmp[:, :Wt - x]
        letters.append((ch, x, g))
        full |= g
        prev = full.copy()
        prev_ch = ch
    return full, letters


def facet_field(letters, H, W, k=4):
    """Light term per art pixel from a k-times supersampled distance field."""
    global _K
    from scipy import ndimage
    acc = np.zeros((H, W))
    for ch, x, _g in letters:
        _K = k
        big, _ = GLYPHS[ch](W * k, H * k, x, UP + PAD)
        _K = 1
        d = ndimage.distance_transform_edt(np.pad(big, 1))[1:-1, 1:-1]
        d = ndimage.gaussian_filter(d, 1.0)
        gy, gx = np.gradient(d)
        n = np.hypot(gx, gy) + 1e-6
        lx, ly = -0.5, -0.86
        val = (-gx / n) * lx + (-gy / n) * ly
        val = np.where(big, val, 0.0)
        acc += val.reshape(H, k, W, k).sum(axis=(1, 3))
    cnt = np.zeros((H, W))
    for ch, x, _g in letters:
        _K = k
        big, _ = GLYPHS[ch](W * k, H * k, x, UP + PAD)
        _K = 1
        cnt += big.reshape(H, k, W, k).sum(axis=(1, 3))
    return acc / np.maximum(cnt, 1)


def shade(mask, letters=None, ember=True):
    H, W = mask.shape
    c = Canvas(W, H)
    Y = np.arange(H)[:, None].repeat(W, 1) - (UP + PAD)   # y relative to cap line
    X = np.arange(W)[None, :].repeat(H, 0)

    ext_depth = 3
    ext = np.zeros_like(mask)
    for k in range(1, ext_depth + 1):
        ext[k:] |= mask[:-k]
    ext &= ~mask
    # extrusion: dark iron plate, lit top row, ember-hot seam at its lowest row
    c.put(ext, col('iron', 3))
    top_row = ext & np.roll(mask, 1, axis=0)
    c.put(top_row, col('iron', 5))
    low = ext & ~np.roll(ext, -1, axis=0)
    c.put(low, col('iron', 2))
    if ember:
        # a faint ember line along the lower edge (heated metal), only under wide bottoms
        c.put(low & (Y >= CAP + 2), col('ember', 2))

    # chiseled facets: each stroke splits into a lit and a shaded facet along
    # its medial ridge (normal of the nearest edge vs. top-left light)
    ndl = facet_field(letters, H, W)
    idx = np.where(ndl > 0.28, 7, np.where(ndl > -0.22, 6, 4))
    # gentle vertical falloff: lower third one step darker, spire tips brighter
    idx = idx - (Y >= 22).astype(int)
    idx = np.where(Y < 0, idx + 1, idx)
    c.put_index(mask, 'gold', idx)
    up_empty = mask & ~np.roll(mask, 1, axis=0)
    down_empty = mask & ~np.roll(mask, -1, axis=0)
    right_empty = mask & ~np.roll(mask, -1, axis=1)
    left_empty = mask & ~np.roll(mask, 1, axis=1)
    c.put(right_empty & ~up_empty, col('gold', 3))
    c.put(down_empty, col('gold', 2))
    c.put(left_empty & ~down_empty & (ndl > -0.25), col('gold', 8))
    c.put(up_empty, col('gold', 9))
    # outline around face + extrusion
    sil = mask | ext
    c.put(outline(sil, diagonal=False), col('iron', 0))
    return c


def build(text='AVARNETH', gap=4, ember=True, return_face=False):
    """Returns the wordmark canvas trimmed to its pixels (and optionally the face mask)."""
    m, letters = layout(text, gap=gap)
    c = shade(m, letters, ember=ember)
    a = c.a
    ys, xs = np.where(a[..., 3] > 0)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    out = Canvas(x1 - x0, y1 - y0)
    out.a = a[y0:y1, x0:x1].copy()
    if return_face:
        return out, m[y0:y1, x0:x1].copy()
    return out


if __name__ == '__main__':
    import sys
    c = build()
    c.save(sys.argv[1] if len(sys.argv) > 1 else 'wordmark.png')
    print(c.w, c.h)
