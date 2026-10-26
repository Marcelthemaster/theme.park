"""Subtitle (VEIL OF EMBERS) and publisher (ECKERTENGINEERING / PRESENTS) layers."""
from __future__ import annotations

import numpy as np
from pix import Canvas, col, outline, alpha_over
from fonts import EMBER9, STEEL7, text_mask, styled


def _gold_face(c, m, Y):
    idx = np.full(Y.shape, 6)
    idx[Y <= 2] = 7
    idx[Y >= 6] = 5
    idx[Y >= 8] = 4
    c.put_index(m, 'gold', idx)
    c.put(m & (Y == 0), col('gold', 8))


def flourish(length=22, mirror=False):
    """Thin forged rule ending in an ember diamond: ---<>  (left side)."""
    h = 7
    c = Canvas(length + 6, h)
    cy = h // 2
    # rule: 1px gold line with a dark outline, tapering into dots at the far end
    for x in range(length):
        if x < 6 and x % 2 == 1:
            continue
        c.px(x, cy, col('gold', 5 if x > length // 2 else 4))
    # diamond at the inner end
    dx = length + 2
    for (ox, oy, k) in [(0, -2, 6), (-1, -1, 5), (0, -1, 7), (1, -1, 5), (-2, 0, 4), (-1, 0, 6), (0, 0, 8),
                        (1, 0, 6), (2, 0, 4), (-1, 1, 4), (0, 1, 5), (1, 1, 4), (0, 2, 3)]:
        c.px(dx + ox, cy + oy, col('ember', k))
    m = c.alpha_mask()
    c.put(outline(m), col('iron', 0))
    if mirror:
        c.a = c.a[:, ::-1].copy()
    return c


def build_subtitle(with_flourish=True, tracking=2):
    m = text_mask(EMBER9, 'VEIL OF EMBERS', tracking=tracking, space=3)
    t = styled(m, _gold_face, edge=('iron', 0), shadow=('gold', 1))
    if not with_flourish:
        return t
    fl = flourish()
    fr = flourish(mirror=True)
    gap = 3
    W = fl.w + gap + t.w + gap + fr.w
    H = max(t.h, fl.h)
    c = Canvas(W, H)
    ty = (H - t.h) // 2
    fy = ty + 2 + 4 - fl.h // 2  # align diamond centre with the cap middle (cap rows start at pad=2)
    alpha_over(c.a, fl.a, 0, fy)
    alpha_over(c.a, t.a, fl.w + gap, ty)
    alpha_over(c.a, fr.a, fl.w + gap + t.w + gap, fy)
    return c


def _steel_face(c, m, Y):
    idx = np.full(Y.shape, 7)
    idx[Y <= 1] = 8
    idx[Y >= 5] = 6
    c.put_index(m, 'iron', idx)


def _steel_dim(c, m, Y):
    idx = np.full(Y.shape, 6)
    idx[Y <= 1] = 7
    idx[Y >= 5] = 5
    c.put_index(m, 'iron', idx)


def build_publisher(text='ECKERTENGINEERING', tracking=2):
    m = text_mask(STEEL7, text, tracking=tracking, space=4)
    return styled(m, _steel_face, edge=('iron', 0), shadow=('iron', 2))


def build_presents_line():
    """ECKERTENGINEERING PRESENTS as one dezent line (name bright, 'PRESENTS' dimmer)."""
    a = text_mask(STEEL7, 'ECKERTENGINEERING', tracking=2)
    b = text_mask(STEEL7, 'PRESENTS', tracking=2)
    sp = 7
    m = np.zeros((a.shape[0], a.shape[1] + sp + b.shape[1]), bool)
    m[:, :a.shape[1]] = a
    m[:, a.shape[1] + sp:] = b
    split = a.shape[1] + sp // 2

    def face(c, mm, Y):
        X = np.arange(c.w)[None, :].repeat(c.h, 0) - 2
        _steel_face(c, mm & (X < split), Y)
        _steel_dim(c, mm & (X >= split), Y)
    return styled(m, face, edge=('iron', 0), shadow=('iron', 2))
