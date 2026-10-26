"""Subtitle (VEIL OF EMBERS) and publisher (ECKERTENGINEERING / PRESENTS) layers. Revision 2.

* Subtitle: 9 px small capitals in the wordmark's construction logic, one tone
  quieter than the wordmark (max highlight gold7), flanked by a single forged
  rule ending in an ember lozenge.
* Publisher: 5 px capitals with 1 px strokes in one flat steel tone - a discreet
  studio credit that never competes with the title.
"""
from __future__ import annotations

import numpy as np
from pix import Canvas, col, outline, alpha_over
from fonts import EMBER9, SMALL5, text_mask, styled


def _gold_face(c, m, Y):
    idx = np.full(Y.shape, 5)
    idx[Y <= 1] = 6
    idx[Y >= 7] = 4
    c.put_index(m, 'gold', idx)
    c.put(m & (Y == 0), col('gold', 7))


def flourish(length=20, mirror=False):
    """Single forged rule ending in an ember lozenge: ------<>  (left side)."""
    h = 7
    c = Canvas(length + 6, h)
    cy = h // 2
    for x in range(length):
        c.px(x, cy, col('gold', 4 if x > length // 3 else 3))
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
    fy = ty + 2 + 4 - fl.h // 2      # diamond centre on the cap middle (cap rows start at pad=2)
    alpha_over(c.a, fl.a, 0, fy)
    alpha_over(c.a, t.a, fl.w + gap, ty)
    alpha_over(c.a, fr.a, fl.w + gap + t.w + gap, fy)
    return c


def _steel_flat(c, m, Y):
    c.put(m, col('iron', 7))


def build_publisher(text='ECKERTENGINEERING', tracking=2):
    m = text_mask(SMALL5, text, tracking=tracking, space=4)
    return styled(m, _steel_flat, edge=('iron', 0), shadow=('iron', 1))


def build_presents_line(tracking=1):
    """ECKERTENGINEERING PRESENTS as one discreet line in a single flat steel tone."""
    m = text_mask(SMALL5, 'ECKERTENGINEERING PRESENTS', tracking=tracking, space=4)
    return styled(m, _steel_flat, edge=('iron', 0), shadow=('iron', 1))
