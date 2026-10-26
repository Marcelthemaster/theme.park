"""AVARNETH emblem - "The Ember Gate" (V1.0 revision 2).

A forged heater shield: dark-iron frame, aged-gold rim, riveted iron plate
field. Inside stands the A of AVARNETH as a fortress: two gold flanks meeting
in a summit that breaks the frame, a crenellated keep tower with two arcane
lancet windows in the upper counter, the gold crossbar as the lintel, and below
it a masonry wall with the monumental gate - an iron portcullis over an ember
glow. A small ember stone is set flush into the shield tip.

All shading is explicit and monotonic per region (no per-row noise). Geometry is
authored in a 63x72 design space and can be rendered at other scales (S) for
the icon masters.
"""
from __future__ import annotations

import numpy as np
from pix import (Canvas, col, poly_mask, ellipse_mask, rect_mask, bezier,
                 mirror_x, outline, inner_edge, dilate, edt_inside)


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
        self.cx = W // 2

    def s(self, v):
        return v * self.S

    def r(self, v):
        return int(round(v * self.S))

    def sym(self, half_pts):
        right = [(self.W - x, y) for (x, y) in reversed(half_pts)]
        return mirror_x(poly_mask(self.W, self.H, list(half_pts) + right))

    def shield(self, inset=0.0):
        s, i, CX = self.s, inset, self.CX
        top = s(11) + i
        half = [(CX, top), (s(3) + i, top), (s(3) + i, s(41))]
        half += bezier((s(3) + i, s(41)), (s(3.5) + i, s(60) - i * 0.3), (CX, s(71.5) - i * 1.35), 40)[1:]
        return self.sym(half)

    def peak(self, inset=0.0, apex=3.0, base=59.0, slope=3.0):
        s, CX = self.s, self.CX
        hw = (s(base) - s(apex)) / slope
        return self.sym([(CX, s(apex) + inset * slope * 1.05), (CX - hw + inset, s(base)), (CX, s(base))])

    # ------------------------------------------------------------------
    def build(self, detail='full'):
        """detail: 'full' (logo), 'medium' (reduced), 'icon' (reduced + brighter plate/right side
        so the silhouette survives a dark Windows taskbar)."""
        W, H, X, Y, cx = self.W, self.H, self.X, self.Y, self.cx
        s, r = self.s, self.r
        full = detail == 'full'
        icon = detail == 'icon'
        c = Canvas(W, H)

        outer = self.shield(0)
        goldm = self.shield(max(1.0, s(2.0)))
        field = self.shield(max(3.0, s(5.0)))
        low_y = r(50)          # where the side becomes the lower curve

        # ---- iron frame: explicit, monotonic per region
        frame = outer & ~goldm
        c.put(frame, col('iron', 5))
        c.put(frame & (X < cx) & (Y >= low_y), col('iron', 4))
        c.put(frame & (X > cx) & (Y < low_y), col('iron', 5 if icon else 4))
        c.put(frame & (X > cx) & (Y >= low_y), col('iron', 4 if icon else 3))
        c.put(frame & (Y < r(11) + 1), col('iron', 6))
        c.put(frame & (Y == r(11)) & (X < W - r(4)), col('iron', 7))

        # ---- gold rim: top lit, left lit, right shade, lower curve one step darker each side
        rim = goldm & ~field
        c.put(rim & (X <= cx), col('gold', 6))
        c.put(rim & (X > cx), col('gold', 5 if icon else 4))
        c.put(rim & (X <= cx) & (Y >= low_y), col('gold', 5))
        c.put(rim & (X > cx) & (Y >= low_y), col('gold', 4 if icon else 3))
        top_rim = rim & (Y < r(11) + r(3) + 1)
        c.put(top_rim & (X <= cx), col('gold', 7))
        c.put(top_rim & (X > cx), col('gold', 6))
        c.put(rim & (Y == r(11) + max(1, r(2))) & (X < W - r(6)), col('gold', 8))
        # inner bevel line (dark) separating rim and field
        c.put(outline(field) & rim, col('gold', 2))
        if full:
            for (rx, ry) in [(4.5, 15.5), (4.5, 28.5), (4.5, 41.5)]:
                for px_ in (r(rx), W - 1 - r(rx)):
                    py_ = r(ry)
                    if rim[py_, px_]:
                        c.px(px_, py_, col('gold', 9))
                        c.px(px_, py_ + 1, col('gold', 3))

        # ---- field: riveted dark iron plate
        base_i = 4 if icon else 2
        c.put(field, col('iron', base_i))
        fe = inner_edge(field, diagonal=False)
        c.put(fe & (Y < r(12) + max(3, r(5))), col('iron', base_i + 1))          # top inner bevel (lit)
        c.put(fe & (X < cx) & (Y < low_y), col('iron', base_i + 1))               # left inner bevel (lit)
        c.put(fe & (X > cx), col('iron', 1))                             # right inner bevel (shade)
        c.put(fe & (X < cx) & (Y >= low_y), col('iron', 1))
        if full:
            seam_y = r(31)
            c.put(field & (Y == seam_y) & ~fe, col('iron', 1))
            c.put(field & (Y == seam_y + 1) & ~fe, col('iron', 3))
            for (rx, ry) in [(9, 17), (9, 45), (54, 17), (54, 45)]:
                px_, py_ = r(rx), r(ry)
                if field[py_, px_]:
                    c.px(px_, py_, col('iron', 5))
                    c.px(px_ + 1, py_ + 1, col('iron', 1))
                    c.px(px_ - 1, py_, col('iron', 4))

        # ---- engraved mountain relief on the plate (low contrast, mirrored)
        if full:
            pts = [(s(4), s(56)), (s(4), s(47)), (s(8), s(42)), (s(11), s(45)), (s(16), s(37)),
                   (s(21), s(44)), (s(24), s(41)), (s(28), s(48)), (s(28), s(60)), (s(4), s(60))]
            mt = mirror_x(poly_mask(W, H, pts)) & field
            c.put(mt, col('iron', 3))
            ridge = mt & ~np.roll(mt, 1, axis=0)
            # lit slopes rise to the right (light from the left), shaded slopes fall
            left_lit = ridge & np.roll(~mt, -1, axis=1)
            c.put(ridge, col('iron', 4))
            c.put(ridge & (X > cx), col('iron', 3))
            c.put(mt & ~ridge & np.roll(ridge, 1, axis=0) & (X < cx), col('iron', 3))

        self._keep(c, field, outer, detail)

        # ---- ember stone set flush into the shield tip
        gy = r(65)
        gem = (np.abs(X - cx) + np.abs(Y - gy)) <= max(1, r(1.6))
        setting = dilate(gem, 1.0) & ~gem & (goldm | field)
        c.put(setting & (Y <= gy), col('gold', 6))
        c.put(setting & (Y > gy), col('gold', 3))
        c.put(gem, col('ember', 5))
        c.put(gem & (Y < gy), col('ember', 7))
        c.put(gem & (Y == gy) & (X < cx), col('ember', 7))
        c.px(cx, gy - 1 if gem[gy - 1, cx] else gy, col('ember', 8))
        c.put(gem & (Y > gy), col('ember', 3))

        # ---- global silhouette outline
        sil = c.alpha_mask()
        c.put(outline(sil), col('iron', 0))
        return c

    # ------------------------------------------------------------------
    def _keep(self, c, field, outer, detail):
        W, H, X, Y, cx = self.W, self.H, self.X, self.Y, self.cx
        s, r = self.s, self.r
        full = detail == 'full'
        leg = max(2, r(3))
        peak = self.peak()
        inner = self.peak(inset=leg)
        base_y = r(59)
        bar_y0 = r(36)
        bar_h = max(2, r(3))
        bar_y1 = bar_y0 + bar_h

        upper = inner & (Y < bar_y0)
        lower = inner & (Y >= bar_y1)

        # ---- upper counter: dark sky-iron with the keep tower
        c.put(upper, col('iron', 1))
        tw = max(1, r(3))                      # half width of the keep tower
        t_top = r(26)
        tower = rect_mask(W, H, cx - tw, t_top, cx + tw + 1, bar_y0) & upper
        mh = max(1, r(2))
        # crenellations: merlon / crenel / merlon / crenel / merlon
        mer = rect_mask(W, H, cx - tw, t_top - mh, cx - tw + max(1, r(2)), t_top)
        mer |= rect_mask(W, H, cx + tw + 1 - max(1, r(2)), t_top - mh, cx + tw + 1, t_top)
        if tw >= 3:
            mer |= rect_mask(W, H, cx, t_top - mh, cx + 1, t_top)
        tower |= mer & upper
        c.put(tower, col('stone', 4))
        c.put(tower & (X <= cx - tw + max(0, r(1))), col('stone', 6))
        c.put(tower & (X >= cx + tw - max(0, r(1))), col('stone', 3))
        tops = tower & ~np.roll(tower, 1, axis=0)
        c.put(tops, col('stone', 7))
        c.put(outline(tower) & upper, col('iron', 0))
        # two arcane lancet windows
        if self.S >= 0.6:
            wy0, wy1 = r(29), r(29) + max(2, r(4))
            for wx in (cx - max(1, r(1.5)), cx + max(1, r(1.5))):
                c.put(rect_mask(W, H, wx, wy0, wx + 1, wy1), col('arcane', 5))
                c.px(wx, wy0, col('arcane', 7))
                c.px(wx, wy1 - 1, col('arcane', 3))
        else:
            c.px(cx, r(30), col('arcane', 6))

        # ---- lower counter: masonry wall with the gate
        c.put(lower, col('stone', 4))
        c.put(lower & (X > cx + r(5)), col('stone', 3))
        if full:
            yy = Y - bar_y1
            mortar = lower & (yy % 5 == 4)
            joint = lower & (((X - cx + 3 * ((yy // 5) % 2)) % 6) == 0) & (yy % 5 != 4)
            c.put(mortar | joint, col('stone', 2))
            c.put(lower & (yy % 5 == 0) & (X <= cx + r(5)) & ~joint, col('stone', 5))

        # gate (arch) with frame, ember glow and iron portcullis
        gr = max(2, r(5.5))
        g_top = r(43)
        gate = rect_mask(W, H, cx - gr, g_top + gr, cx + gr + 1, base_y)
        gate |= ellipse_mask(W, H, self.CX, g_top + gr + 0.5, gr + 0.5, gr + 0.5) & (Y < g_top + gr + 1)
        gate &= lower
        gframe = dilate(gate, 1.0) & ~gate & lower
        c.put(gframe, col('stone', 6))
        c.put(gframe & (X > cx), col('stone', 3))
        span = max(1, base_y - g_top)
        t = (Y - g_top) / span
        c.put(gate, col('ember', 3))
        c.put(gate & (t >= 0.35), col('ember', 4))
        c.put(gate & (t >= 0.62), col('ember', 5))
        c.put(gate & (t >= 0.84), col('ember', 6))
        if self.S >= 0.6:
            bars = gate & (((X - cx) % 2) == 1)
            c.put(bars, col('iron', 1))
            c.put(gate & (Y == g_top + gr + 1) & ~bars, col('iron', 2))
        # keystone
        c.put(rect_mask(W, H, cx - 1, g_top - 1, cx + 2, g_top + 1) & lower, col('gold', 7))
        c.px(cx, g_top - 1, col('gold', 9))

        # ---- gold flanks of the A (left lit, right shade - both clearly gold)
        flank = peak & ~inner
        dd = np.floor(edt_inside(peak)).astype(int)
        lf = flank & (X < cx)
        rf = flank & (X > cx)
        c.put(lf, col('gold', 5))
        c.put(lf & (dd <= 1), col('gold', 7))
        c.put(lf & (dd == 2), col('gold', 6))
        c.put(rf, col('gold', 3))
        c.put(rf & (dd <= 1), col('gold', 5))
        c.put(rf & (dd == 2), col('gold', 4))
        c.put(flank & (X == cx), col('gold', 8))
        c.px(cx, r(3) + 1, col('gold', 9))

        # ---- crossbar / lintel
        bar = (Y >= bar_y0) & (Y < bar_y1) & peak
        c.put(bar, col('gold', 5))
        c.put(bar & (Y == bar_y0), col('gold', 8))
        c.put(bar & (Y == bar_y1 - 1), col('gold', 3))

        # ---- base ledge
        k = (s(59) - s(3)) / 3.0
        ledge = (Y >= base_y) & (Y < base_y + max(2, r(3))) & (np.abs(X - self.CX + 0.5) <= k + 1) & field
        c.put(ledge, col('stone', 4))
        c.put(ledge & (Y == base_y), col('stone', 6))
        c.put(ledge & (Y == base_y) & (X < cx), col('stone', 7))
        c.put(ledge & (Y == base_y + max(2, r(3)) - 1), col('stone', 2))

        # ---- dark separation lines around the keep (inside the shield)
        keep = peak | ledge
        sep = outline(keep) & (field | (outer & ~keep))
        c.put(sep & ~keep, col('iron', 0))


def a_mask(S=1.0):
    """Gold legs + crossbar of the A (used by the light-trace animation)."""
    e = Emblem(S)
    r = e.r
    leg = max(2, r(3))
    peak = e.peak()
    inner = e.peak(inset=leg)
    bar = (e.Y >= r(36)) & (e.Y < r(36) + max(2, r(3))) & peak
    return (peak & ~inner) | bar


def build(S=1.0, detail='full'):
    return Emblem(S).build(detail)


if __name__ == '__main__':
    import sys
    S = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    det = sys.argv[3] if len(sys.argv) > 3 else 'full'
    build(S, det).save(sys.argv[1] if len(sys.argv) > 1 else 'emblem.png')
