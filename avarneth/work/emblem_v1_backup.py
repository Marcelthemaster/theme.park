"""AVARNETH emblem - "The Ember Gate".

A forged heater shield (dark iron frame + aged-gold rim). Its summit breaks the
frame: a mountain keep shaped like the letter A, with a monumental gate glowing
with an ember core, an arcane window above, curtain walls and flanking towers
silhouetted against an ember-lit sky, and an ember gem set in the shield's tip.

Everything is generated on the native pixel grid in a 63x72 design space and
can be rendered at other scales (S) for icon masters.
"""
from __future__ import annotations

import numpy as np
from pix import (Canvas, col, poly_mask, ellipse_mask, rect_mask, bezier,
                 mirror_x, outline, inner_edge, erode, dilate, edt_inside,
                 bevel_light, dither_levels)


class Emblem:
    def __init__(self, S=1.0):
        self.S = S
        W = int(round(63 * S))
        if W % 2 == 0:
            W += 1
        self.W = W
        self.H = int(round(72 * S))
        self.CX = W / 2.0
        self.X, self.Y = np.meshgrid(np.arange(self.W), np.arange(self.H))
        self.cxi = W // 2  # centre column index

    # ---- geometry helpers (design units -> pixels)
    def s(self, v):
        return v * self.S

    def sym(self, half_pts):
        right = [(self.W - x, y) for (x, y) in reversed(half_pts)]
        return mirror_x(poly_mask(self.W, self.H, list(half_pts) + right))

    def shield(self, inset=0.0):
        s, i, CX = self.s, inset, self.CX
        top = s(13) + i
        half = [(CX, top + s(1.2)), (s(9), top), (s(2.5) + i, top - s(2.2) + i * 0.3),
                (s(3) + i, s(41))]
        half += bezier((s(3) + i, s(41)), (s(3.5) + i, s(60) - i * 0.3),
                       (CX, s(71.5) - i * 1.35), 32)[1:]
        return self.sym(half)

    def peak(self, inset=0.0, apex=1.0, base=58.0):
        s, CX = self.s, self.CX
        hw = (s(base) - s(apex)) / 3.0
        return self.sym([(CX, s(apex) + inset * 3.2), (CX - hw + inset, s(base)), (CX, s(base))])

    def gate(self):
        s, CX = self.s, self.CX
        r = s(5.5)
        top, bottom = s(41.5), s(58)
        m = rect_mask(self.W, self.H, int(round(CX - r)), int(round(top + r)), int(round(CX + r)), int(round(bottom)))
        m |= ellipse_mask(self.W, self.H, CX, top + r, r, r) & (self.Y + 0.5 <= top + r + 0.5)
        return mirror_x(m)

    # ---- rendering
    def build(self, detail='full'):
        """detail: 'full' (logo), 'medium' (no towers/rivets/portcullis), 'low' (icon basics)."""
        W, H, X, Y, s, cx = self.W, self.H, self.X, self.Y, self.s, self.cxi
        full = detail == 'full'
        sparks = detail != 'low'
        c = Canvas(W, H)

        outer = self.shield(0)
        goldm = self.shield(max(1.0, s(2.0)))
        field = self.shield(max(3.0, s(5.0)))

        # --- iron frame (outermost band)
        d, ndl = bevel_light(outer, smooth=0.8)
        iron_v = 4.2 + 2.2 * ndl
        c.put_index(outer & ~goldm, 'iron', np.round(iron_v).astype(int))
        # --- aged gold rim
        d2, ndl2 = bevel_light(goldm, smooth=0.8)
        gold_v = 5.0 + 2.6 * ndl2 - 0.5 * np.clip(d2 - 1.0, 0, 3)
        c.put_index(goldm & ~field, 'gold', np.round(gold_v).astype(int))
        c.put(inner_edge(goldm, True) & ~field & (ndl2 < -0.2), col('gold', 2))
        c.put(outline(field) & goldm, col('gold', 1))
        # rivets on the gold rim
        if full and self.S >= 0.8:
            for (rx, ry) in [(5.5, 14.5), (5.5, 27.5), (5.5, 40.5), (12.5, 58.5), (21.5, 66.0)]:
                for px_ in (int(rx * self.S), W - 1 - int(rx * self.S)):
                    py_ = int(ry * self.S)
                    if goldm[py_, px_] and not field[py_, px_]:
                        c.px(px_, py_, col('gold', 9))
                        if py_ + 1 < H and goldm[py_ + 1, px_] and not field[py_ + 1, px_]:
                            c.px(px_, py_ + 1, col('gold', 3))

        # --- field: ember-lit sky in clean horizontal bands
        top = int(round(s(12)))
        horizon = int(round(s(56)))
        u = np.clip((Y - top) / max(1, horizon - top), 0, 1)
        # dark iron sky in calm bands, warming slightly towards the horizon
        bands = [(0.00, ('iron', 2)), (0.30, ('iron', 3)), (0.62, ('stone', 2)), (0.86, ('ember', 0))]
        for th, (rp, ix) in bands:
            c.put(field & (u >= th), col(rp, ix))
        # below the horizon (ground behind the base) dark stone
        c.put(field & (Y >= horizon), col('stone', 1))

        # embers rising in the sky
        if sparks:
            for (ex, ey, e) in [(11, 22, 5), (52, 19, 4), (15, 33, 4), (49, 31, 5), (8, 43, 6), (55, 42, 6),
                                (21, 16, 3), (43, 25, 3)]:
                px, py = int(round(s(ex))), int(round(s(ey)))
                if field[py, px]:
                    c.px(px, py, col('ember', e))

        # --- curtain walls + towers (fortress), symmetrical, lit from the left
        if full:
            self._fortress(c, field)
        self._keep(c, field, outer, detail)
        return c

    def _fortress(self, c, field):
        W, H, X, Y, s = self.W, self.H, self.X, self.Y, self.s
        fort = np.zeros((H, W), bool)
        lit = np.zeros((H, W), bool)
        dark = np.zeros((H, W), bool)
        for side in (0, 1):
            def X0(v):
                return s(v) if side == 0 else W - s(v)
            # tower
            tx0, tx1 = sorted([X0(7), X0(15)])
            tm = rect_mask(W, H, int(round(tx0)), int(round(s(37))), int(round(tx1)), int(round(s(58))))
            mer = np.zeros_like(tm)
            step = max(2, int(round(s(3))))
            for k, mx in enumerate(range(int(round(tx0)), int(round(tx1)), step)):
                if k % 2 == 0:
                    mer |= rect_mask(W, H, mx, int(round(s(34))), min(mx + max(1, step - 1) + 1, int(round(tx1))), int(round(s(37))))
            tm |= mer
            # wall from tower to the peak
            wx0, wx1 = sorted([X0(13), X0(26)])
            wm = rect_mask(W, H, int(round(wx0)), int(round(s(50))), int(round(wx1)), int(round(s(58))))
            wmer = np.zeros_like(wm)
            for k, mx in enumerate(range(int(round(wx0)), int(round(wx1)), step)):
                if k % 2 == 0:
                    wmer |= rect_mask(W, H, mx, int(round(s(48))), mx + max(1, step - 1), int(round(s(50))))
            wm |= wmer
            part = (tm | wm) & field
            fort |= part
            # lighting: tower left edge lit, right edge dark
            ltx = int(round(tx0))
            lit |= tm & (X < ltx + max(1, int(round(s(2)))))
            dark |= tm & (X >= int(round(tx1)) - max(1, int(round(s(2)))))
        c.put(fort, col('stone', 3))
        c.put(fort & lit, col('stone', 5))
        c.put(fort & dark, col('stone', 2))
        # crenel tops lit
        c.put(inner_edge(fort) & ~shift_down(fort) & fort, col('stone', 6))
        c.put(outline(fort) & field, col('stone', 0))
        # tower windows (arrow slits glowing)
        for side in (0, 1):
            wxp = int(round(s(10.5))) if side == 0 else W - 1 - int(round(s(10.5)))
            for wy in (s(41), s(51)):
                c.put(rect_mask(W, H, wxp, int(round(wy)), wxp + 1, int(round(wy + max(2, s(4))))), col('ember', 6))
            c.px(wxp, int(round(s(41))), col('ember', 8))

    def _keep(self, c, field, outer, detail):
        W, H, X, Y, s, cx = self.W, self.H, self.X, self.Y, self.s, self.cxi
        full = detail == 'full'
        # --- the A peak (mountain keep)
        peak = self.peak()
        inner = self.peak(inset=max(2.0, s(3.0)))
        face_l = inner & (X < cx)
        face_r = inner & (X > cx)
        c.put(peak, col('stone', 3))
        # left face: lit stone with crag strata, right face: shadow
        crag = ((Y * 2 + X * 3) % 13 == 0) & (detail != 'low')
        c.put(face_l, col('stone', 5))
        c.put(face_l & crag, col('stone', 4))
        c.put(face_l & (X == cx - 1), col('stone', 6))
        c.put(face_r, col('stone', 2))
        c.put(face_r & crag, col('stone', 1))
        c.put(inner & (X == cx), col('stone', 7))
        # gold flanks of the A (the 'forged letter')
        flank = peak & ~inner
        dd = np.floor(edt_inside(peak)).astype(int)
        lf = flank & (X < cx)
        rf = flank & (X > cx)
        c.put(lf, col('gold', 5)); c.put(lf & (dd <= 1), col('gold', 7)); c.put(lf & (dd == 2), col('gold', 6))
        c.put(rf, col('gold', 3)); c.put(rf & (dd <= 1), col('gold', 4)); c.put(rf & (dd >= 3), col('gold', 2))
        c.put(flank & (X == cx), col('gold', 8))
        # apex specular
        c.px(cx, int(round(s(1.0))) + 1, col('gold', 9))
        c.px(cx, int(round(s(1.0))) + 2, col('gold', 8))

        # --- lintel / crossbar of the A
        bar_y = int(round(s(37)))
        bar = (Y >= bar_y) & (Y < bar_y + max(2, int(round(s(3))))) & self.peak(inset=0.0)
        c.put(bar, col('gold', 4))
        c.put(bar & (Y == bar_y), col('gold', 7))
        c.put(bar & (Y == bar_y + max(2, int(round(s(3)))) - 1), col('gold', 2))
        c.put(outline(bar) & inner & (Y > bar_y), col('stone', 0))

        # --- gate with portcullis and ember core
        gate = self.gate()
        frame = dilate(gate, max(1.0, s(1.6))) & ~gate & (Y < int(round(s(58)))) & inner
        c.put(frame, col('stone', 6))
        c.put(frame & (X > cx), col('stone', 4))
        gd = np.hypot((X - cx) / s(5.0), (Y - s(58)) / s(14.0))
        gv = np.clip(8.4 - gd * 6.4, 1, 8)
        c.put_index(gate, 'ember', dither_levels(gv, None, strength=0.45))
        # portcullis bars (dark ember lines so the glow still reads)
        if full and self.S >= 0.8:
            for bx in (cx - 3, cx, cx + 3):
                c.put(gate & (X == bx) & (Y < s(55)), col('ember', 3))
            c.put(gate & (Y == int(round(s(48)))), col('ember', 3))
        # keystone
        ky = int(round(s(40)))
        c.put(rect_mask(W, H, cx - 1, ky, cx + 2, ky + 2), col('gold', 7))
        c.px(cx, ky, col('gold', 9))

        # --- arcane window
        wy = s(27.0)
        dm = (np.abs(X - cx) + np.abs(Y - wy) * 0.55) <= max(1.5, s(2.6))
        c.put(outline(dm) & inner, col('stone', 0))
        c.put(dm & inner, col('arcane', 4))
        c.put((np.abs(X - cx) + np.abs(Y - wy) * 0.55 <= max(0.6, s(1.2))) & inner, col('arcane', 7))

        # --- rock base the keep stands on + steps
        base = (Y >= int(round(s(58)))) & (Y < int(round(s(62)))) & field
        base &= (np.abs(X - cx) <= s(26) - (Y - s(58)) * 1.2)
        c.put(base, col('stone', 4))
        c.put(base & (Y == int(round(s(58)))), col('stone', 6))
        c.put(base & (X < cx) & (Y == int(round(s(58)))), col('stone', 7))
        c.put(base & (Y == int(round(s(61)))), col('stone', 2))
        c.put(outline(base) & field & (Y > int(round(s(58)))), col('stone', 0))

        # --- ember gem in the shield tip (the ember core / seal)
        gcy = s(65.5)
        gem = (np.abs(X - cx) * 1.0 + np.abs(Y - gcy) * 0.8) <= max(1.6, s(3.2))
        setting = dilate(gem, 1.0) & ~gem & field
        c.put(setting, col('gold', 5))
        c.put(setting & (Y > gcy), col('gold', 3))
        gg = np.clip(7.5 - np.hypot(X - cx + s(0.8), Y - gcy + s(0.8)) * 1.3, 3, 8)
        c.put_index(gem, 'ember', np.round(gg).astype(int))

        # --- separating outlines and the global silhouette outline
        c.put(outline(peak) & ~peak & (c.alpha_mask()) & field & (Y < int(round(s(58)))), col('iron', 0))
        sil = c.alpha_mask() | peak
        c.put(outline(sil), col('iron', 0))
        # peak outside the shield needs its own outline (above the frame)
        above = peak & ~outer
        c.put(outline(above) & ~peak & ~outer, col('iron', 0))


def shift_down(m):
    out = np.zeros_like(m)
    out[1:] = m[:-1]
    return out


def build(S=1.0, detail='full'):
    return Emblem(S).build(detail)


if __name__ == '__main__':
    import sys
    S = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    det = sys.argv[3] if len(sys.argv) > 3 else 'full'
    build(S, det).save(sys.argv[1] if len(sys.argv) > 1 else 'emblem.png')
