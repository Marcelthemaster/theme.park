"""AVARNETH V1.1 - bootstrap visual match (targeted revision of the V1.0 art).

Findings from the side-by-side with the real WOE login capture (see docs):
* density: the fortress artwork (879x510) is shown point-filtered at ~2.18 screen px per art px at 1080p,
  the V1.0 logo at 4 -> V1.1 renders the SAME designs on a 2x finer grid (2 screen px per art px);
* colour: the V1.0 neutral dark-iron field reads as a black patch in the bright daylight scene -> the iron
  ramp is remapped to a heraldic navy taken from the fortress banners / login panel, the stone ramp to the
  fortress stone (violet-grey shadows, warm cream lights); gold, ember and arcane stay unchanged;
* the bitmap fonts (subtitle 9 px, publisher 5 px) are enlarged with Scale2x (EPX: no new colours, no
  anti-aliasing) on the glyph MASKS and then restyled with a 1 px outline on the fine grid.

Nothing here changes the V1.0 generators' default output (regression hashes in work/v11/).
"""
from __future__ import annotations

import numpy as np

import brand
import emblem as emblem_mod
import wordmark as wordmark_mod
from fonts import EMBER9, SMALL5, text_mask, styled
from pix import Canvas, RAMPS, alpha_over, col, outline

D = 2                                   # pixel density factor vs. V1.0 (art px per V1.0 art px)


def _hex(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ramps sampled from the bootstrap artwork / login panel (login_base_clean.png, Login.png):
# banner + roof navy #111933 #222d48 #303d60 #425072 #586484, panel #1f314b,
# fortress stone #3e3c45 #51505c #686570 #83797d #ab978d #c9b19d
HERALDIC = [_hex(h) for h in ('#08090f', '#0f1424', '#151d33', '#1d2944', '#263555',
                              '#303d60', '#425072', '#586484', '#8a93ab', '#d4d9e4')]
CASTLESTONE = [_hex(h) for h in ('#141318', '#24222a', '#3e3c45', '#51505c',
                                 '#686570', '#83797d', '#ab978d', '#c9b19d')]
assert len(HERALDIC) == len(RAMPS['iron']) and len(CASTLESTONE) == len(RAMPS['stone'])

LUT = {}
for i, c in enumerate(RAMPS['iron']):
    LUT[tuple(c)] = HERALDIC[i]
for i, c in enumerate(RAMPS['stone']):
    LUT[tuple(c)] = CASTLESTONE[i]


def recolor(c: Canvas) -> Canvas:
    out = Canvas(c.w, c.h)
    a = c.a.copy()
    flat = a.reshape(-1, 4)
    for n in np.flatnonzero(flat[:, 3]):
        k = (int(flat[n, 0]), int(flat[n, 1]), int(flat[n, 2]))
        if k in LUT:
            flat[n, :3] = LUT[k]
    out.a = a
    return out


def scale2x(m):
    """Scale2x / EPX on a 2-D array (bool mask or palette index map): 2x enlargement that rounds diagonal
    stair steps without creating new values."""
    h, w = m.shape
    p = np.pad(m, 1, mode='edge')
    B, D_, F, H_ = p[:-2, 1:-1], p[1:-1, :-2], p[1:-1, 2:], p[2:, 1:-1]
    E = m
    out = np.empty((2 * h, 2 * w), m.dtype)
    e0 = np.where((D_ == B) & (B != F) & (D_ != H_), D_, E)
    e1 = np.where((B == F) & (B != D_) & (F != H_), F, E)
    e2 = np.where((D_ == H_) & (D_ != B) & (H_ != F), D_, E)
    e3 = np.where((H_ == F) & (D_ != H_) & (B != F), F, E)
    out[0::2, 0::2], out[0::2, 1::2], out[1::2, 0::2], out[1::2, 1::2] = e0, e1, e2, e3
    return out


# ------------------------------------------------------------------ fine-grid art
def emblem(S=2.0):
    return recolor(emblem_mod.build(S, 'fine'))


def a_mask(S=2.0):
    return emblem_mod.a_mask(S)


def wordmark(kd=D, return_face=False):
    wm, face = wordmark_mod.build(return_face=True, kd=kd, ext_depth=2 * kd)
    wm = recolor(wm)
    return (wm, face) if return_face else wm


def _gold_face_2x(c, m, Y):
    """V1.0 subtitle face (brand._gold_face) with row thresholds for the 2x grid."""
    idx = np.full(Y.shape, 5)
    idx[Y <= 3] = 6
    idx[Y >= 14] = 4
    c.put_index(m, 'gold', idx)
    c.put(m & (Y <= 1), col('gold', 7))


def subtitle(with_flourish=True):
    m = scale2x(text_mask(EMBER9, 'VEIL OF EMBERS', tracking=2, space=3))
    t = styled(m, _gold_face_2x, edge=('iron', 0), shadow=('iron', 2), pad=2)
    t = recolor(t)
    if not with_flourish:
        return t
    fl = _flourish_2x()
    fr = Canvas(fl.w, fl.h)
    fr.a = fl.a[:, ::-1].copy()
    gap = 6
    W = fl.w + gap + t.w + gap + fr.w
    H = max(t.h, fl.h)
    c = Canvas(W, H)
    ty = (H - t.h) // 2
    fy = ty + 2 + 9 - fl.h // 2                    # lozenge centre on the cap middle (cap rows 2..19)
    alpha_over(c.a, fl.a, 0, fy)
    alpha_over(c.a, t.a, fl.w + gap, ty)
    alpha_over(c.a, fr.a, fl.w + gap + t.w + gap, fy)
    return c


def _flourish_2x():
    """V1.0 forged rule + ember lozenge, enlarged with Scale2x on its colour indices, outline redrawn 1 px."""
    src = brand.flourish()
    a = src.a
    body = (a[..., 3] > 0) & ~np.all(a[..., :3] == np.array(RAMPS['iron'][0]), axis=-1)
    keys = {}
    idx = np.zeros(body.shape, np.int32)
    for y, x in zip(*np.where(body)):
        k = tuple(int(v) for v in a[y, x])
        idx[y, x] = keys.setdefault(k, len(keys) + 1)
    big = scale2x(idx)
    c = Canvas(big.shape[1] + 2, big.shape[0] + 2)
    inv = {v: k for k, v in keys.items()}
    for v, k in inv.items():
        m = np.zeros((c.h, c.w), bool)
        m[1:-1, 1:-1] = big == v
        c.put(m, k)
    c.put(outline(c.alpha_mask()), col('iron', 0))
    return recolor(c)


def publisher_line(text='ECKERTENGINEERING PRESENTS'):
    """5 px studio credit, Scale2x on the mask, flat fortress cream + navy shadow (no outline)."""
    m = scale2x(text_mask(SMALL5, text, tracking=1, space=3))

    def face(c, mm, Y):
        c.put(mm, col('stone', 7))                   # -> fortress cream #c9b19d after recolor
    t = styled(m, face, edge=None, shadow=('iron', 1), pad=2)
    return recolor(t)


# ------------------------------------------------------------------ login header (static)
HEADER_W, HEADER_H = 204, 52             # = LogoText rect 408 x 104 (1080p reference) at 2 screen px per art px


def header():
    """Static login header for LogoAreaTopLeft/LogoText: emblem left, AVARNETH + VEIL OF EMBERS right,
    left-aligned like the original title."""
    em = recolor(emblem_mod.build(0.667, 'icon'))                 # = the 48 px icon drawing (clearest at this size)
    wm = recolor(wordmark_mod.build(kd=1, ext_depth=2))           # V1.0 grid, recoloured
    sub = subtitle_small()
    c = Canvas(HEADER_W, HEADER_H)
    ey = (HEADER_H - em.h) // 2
    alpha_over(c.a, em.a, 0, ey)
    x = em.w + 5
    room = HEADER_W - x
    if wm.w > room:
        # fit: wordmark at density 2/3 (cap 21 px) built from the same polygons
        wm = recolor(_wordmark_scaled(2.0 / 3.0))
    gap = 3
    block = wm.h + gap + sub.h
    y0 = (HEADER_H - block) // 2
    alpha_over(c.a, wm.a, x, y0)
    alpha_over(c.a, sub.a, x + (wm.w - sub.w) // 2, y0 + wm.h + gap)
    return c, {'emblem': (0, ey, em.w, em.h), 'wordmark': (x, y0, wm.w, wm.h),
               'subtitle': (x + (wm.w - sub.w) // 2, y0 + wm.h + gap, sub.w, sub.h)}


def subtitle_small():
    m = text_mask(EMBER9, 'VEIL OF EMBERS', tracking=1, space=3)
    t = styled(m, brand._gold_face, edge=('iron', 0), shadow=('iron', 2), pad=1)
    return recolor(t)


def _wordmark_scaled(f):
    """Wordmark from the same glyph polygons sampled at a fractional density f (< 1) - header only."""
    return _build_fractional(f)


def _build_fractional(f):
    import wordmark as W
    letters_src = []
    Ht = int(round((W.CAP + W.UP + W.DOWN + 2 * W.PAD) * f))
    for ch in 'AVARNETH':
        g, _, _ = W.glyph_mask(ch, f)
        letters_src.append((ch, g[:Ht]))
    # optical spacing on the small grid
    gap_target, min_gap = 7.0 * f, 2
    Wt = sum(g.shape[1] for _, g in letters_src) + 12 * len(letters_src) + 8
    full = np.zeros((Ht, Wt), bool)
    letters = []
    x = 3
    oy = int(round((W.UP + W.PAD) * f))
    cap_rows = range(oy + 1, oy + int(W.CAP * f) - 1)
    for i, (ch, g) in enumerate(letters_src):
        w = g.shape[1]
        if i:
            for off in range(0, Wt - w):
                cand = np.zeros_like(full)
                cand[:, off:off + w] = g
                if (cand & full).any():
                    continue
                gp = W._gaps(full, cand, range(Ht))
                if not gp or min(gp) < min_gap:
                    continue
                cg = W._gaps(full, cand, cap_rows)
                if np.mean(np.minimum(cg, 11 * f)) >= gap_target:
                    x = off
                    break
        full[:, x:x + w] |= g
        letters.append((ch, x, w))
    # flat 3-tone face (normals from the 1x drawing do not fit this grid) + 1 px rims, 2 px navy extrusion
    c = Canvas(Wt, Ht)
    Y = np.arange(Ht)[:, None].repeat(Wt, 1) - oy
    m = full
    ext = np.zeros_like(m)
    acc = m.copy()
    src = m.copy()
    for k in range(2):
        e = np.zeros_like(m)
        e[1:] = src[:-1] & ~acc[1:]
        e &= ~acc
        c.put(e, col('iron', 4 if k == 0 else 2))
        ext |= e
        acc |= e
        src = e
    face = np.where(Y < W.CAP * f * 0.35, 7, np.where(Y >= W.CAP * f * 0.75, 5, 6))
    c.put_index(m, 'gold', face)
    edge_top = m & ~np.roll(m, 1, axis=0)
    edge_left = m & ~np.roll(m, 1, axis=1)
    edge_right = m & ~np.roll(m, -1, axis=1)
    c.put(edge_left, col('gold', 8))
    c.put(edge_right, col('gold', 4))
    c.put(edge_top, col('gold', 9))
    c.put(outline(m | ext), col('iron', 0))
    ys, xs = np.where(c.a[..., 3] > 0)
    out = Canvas(xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)
    out.a = c.a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    return out
