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
        fine = detail == 'fine'          # V1.1: 'full' + extra surface detail for the 2x bootstrap-matched density
        full = detail in ('full', 'fine')
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
        base_i = 4 if icon else 3
        c.put(field, col('iron', base_i))
        fe = inner_edge(field, diagonal=False)
        c.put(fe & (X > cx), col('iron', base_i - 1))                    # right inner bevel (shade)
        c.put(fe & (X < cx) & (Y >= low_y), col('iron', base_i - 1))
        c.put(fe & (X < cx) & (Y < low_y), col('iron', base_i + 1))      # left inner bevel (lit)
        c.put(fe & (Y < r(12) + max(3, r(5))), col('iron', base_i + 1))  # top inner bevel (lit, both sides)
        if full:
            seam_y = r(31)
            c.put(field & (Y == seam_y) & ~fe, col('iron', 2))
            c.put(field & (Y == seam_y + 1) & ~fe, col('iron', 4))
            for (rx, ry) in [(9, 17), (9, 45), (54, 17), (54, 45)]:
                px_, py_ = r(rx), r(ry)
                if field[py_, px_]:
                    c.px(px_, py_, col('iron', 6))
                    c.px(px_ + 1, py_ + 1, col('iron', 2))
                    c.px(px_ - 1, py_, col('iron', 5))
        if fine:
            self._fine_plate(c, field, fe)

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
    def _fine_plate(self, c, field, fe):
        """V1.1 (fine grid only): heraldic diaper lattice and a lit upper-left sheen on the plate, one ramp step
        each, so the field reads as worked metal/cloth like the banners of the bootstrap fortress."""
        W, H, X, Y, cx = self.W, self.H, self.X, self.Y, self.cx
        r = self.r
        inner = field & ~fe & ~dilate(fe, 1.0)
        seam_y = r(31)
        inner &= np.abs(Y - seam_y - 0.5) > 2
        p = max(8, r(7))                                   # lattice period
        u = (X - cx) + (Y - r(12))
        v = -(X - cx) + (Y - r(12))
        lattice = inner & ((u % p == 0) | (v % p == 0))
        sheen = inner & ((X - cx) * 0.55 + (Y - r(12)) < r(14))
        c.put(sheen, col('iron', 4))
        c.put(lattice, col('iron', 4))
        c.put(lattice & sheen, col('iron', 5))
        knots = inner & (u % p == 0) & (v % p == 0)
        c.put(knots, col('iron', 6))

    def _keep(self, c, field, outer, detail):
        W, H, X, Y, cx = self.W, self.H, self.X, self.Y, self.cx
        s, r = self.s, self.r
        full = detail in ('full', 'fine')
        leg = max(2, r(3))
        peak = self.peak()
        inner = self.peak(inset=leg)
        base_y = r(59)
        bar_y0 = r(36)
        bar_h = max(2, r(3))
        bar_y1 = bar_y0 + bar_h

        upper = inner & (Y < bar_y0)
        lower = inner & (Y >= bar_y1)

        # ---- upper counter: dark void with a slim keep tower (3 one-pixel merlons, one arrow slit)
        c.put(upper, col('iron', 1))
        tw = max(1, r(2))                      # half width of the keep (5 px at S=1)
        t_top = r(23)
        tower = rect_mask(W, H, cx - tw, t_top, cx + tw + 1, bar_y0) & upper
        mh = max(1, r(2))
        mer = np.zeros_like(tower)
        for mx in range(cx - tw, cx + tw + 1, 2):
            mer |= rect_mask(W, H, mx, t_top - mh, mx + 1, t_top)
        tower |= mer & upper
        c.put(tower, col('stone', 4))
        c.put(tower & (X < cx), col('stone', 5))
        c.put(tower & (X == cx - tw), col('stone', 6))
        c.put(tower & (X == cx + tw), col('stone', 3))
        tops = tower & ~np.roll(tower, 1, axis=0)
        if detail == 'fine':                   # V1.1: sunlit keep like the fortress towers (light left, cool right)
            c.put(tower, col('stone', 5))
            c.put(tower & (X < cx), col('stone', 6))
            c.put(tower & (X <= cx - tw + 1), col('stone', 7))
            c.put(tower & (X >= cx + tw - 1), col('stone', 3))
        c.put(tops, col('stone', 7))
        c.put(outline(tower) & upper, col('iron', 0))
        if self.S >= 0.6:
            sy0 = r(29)
            c.put(rect_mask(W, H, cx, sy0, cx + 1, sy0 + max(2, r(3))), col('iron', 0))   # arrow slit

        # ---- lower counter: dark void with a rectangular gatehouse
        c.put(lower, col('iron', 1))
        gh_w = max(3, r(8))                    # gatehouse half width
        gh_top = bar_y1 + max(1, r(2))
        house = rect_mask(W, H, cx - gh_w, gh_top + max(1, r(2)), cx + gh_w + 1, base_y) & lower
        par = np.zeros_like(house)              # crenellated parapet
        for mx in range(cx - gh_w, cx + gh_w + 1, 3):
            par |= rect_mask(W, H, mx, gh_top, mx + 2, gh_top + max(1, r(2)))
        house |= par & lower
        c.put(house, col('stone', 4))
        c.put(house & (X > cx + r(3)), col('stone', 3))
        c.put(house & (X == cx - gh_w), col('stone', 6))
        c.put(house & (X == cx + gh_w), col('stone', 2))
        htops = house & ~np.roll(house, 1, axis=0)
        c.put(htops, col('stone', 6))
        if full:
            yy = Y - (gh_top + 2)
            body = house & (Y > gh_top + 2) & (X > cx - gh_w) & (X < cx + gh_w)
            mortar = body & (yy % 4 == 3)
            joint = body & (((X - cx + 2 * ((yy // 4) % 2)) % 4) == 0) & (yy % 4 != 3)
            c.put(mortar | joint, col('stone', 2))
        c.put(outline(house) & lower, col('iron', 0))

        # gate (arch) with frame, dark ember glow and an iron portcullis
        gr = max(2, r(4))
        g_top = gh_top + max(3, r(5))
        gate = rect_mask(W, H, cx - gr, g_top + gr, cx + gr + 1, base_y)
        gate |= ellipse_mask(W, H, self.CX, g_top + gr + 0.5, gr + 0.5, gr + 0.5) & (Y < g_top + gr + 1)
        gate &= house
        gframe = dilate(gate, 1.0) & ~gate & house
        c.put(gframe, col('stone', 6))
        c.put(gframe & (X > cx), col('stone', 3))
        c.put(gate, col('ember', 1))
        c.put(gate & (Y >= base_y - max(4, r(6))), col('ember', 2))
        core = gate & (np.abs(X - cx) <= max(1, r(1))) & (Y >= base_y - max(2, r(3)))
        c.put(core, col('ember', 5))
        c.put(core & (Y == base_y - 1), col('ember', 6))
        if self.S >= 0.6:
            vbars = gate & (((X - cx) % 2) == 0) & (np.abs(X - cx) <= gr - 1) & (Y < base_y - 1)
            hrows = (Y == g_top + gr + 1) | (Y == g_top + gr + max(3, r(5)))
            hbars = gate & hrows
            c.put(vbars | hbars, col('iron', 5))
            c.put(vbars & (Y == g_top + gr - 1), col('iron', 6))
            c.put(hbars & ~vbars, col('iron', 4))
            c.put(gate & (((X - cx) % 2) == 0) & (np.abs(X - cx) <= gr - 1) & (Y == base_y - 2), col('iron', 6))  # spikes
        # keystone
        c.put(rect_mask(W, H, cx - 1, g_top - 1, cx + 2, g_top + 1) & house, col('gold', 7))
        c.px(cx, g_top - 1, col('gold', 9))

        # ---- gold flanks of the A: bands by horizontal distance from the outer edge (clean 1:3 stairs)
        flank = peak & ~inner
        for y in range(H):
            xs = np.where(peak[y])[0]
            if len(xs) == 0:
                continue
            x0, x1 = xs.min(), xs.max()
            for x in range(x0, x1 + 1):
                if not flank[y, x]:
                    continue
                if x < cx:
                    d = x - x0
                    c.px(x, y, col('gold', 7 if d == 0 else (6 if d == 1 else 5)))
                elif x > cx:
                    d = x1 - x
                    c.px(x, y, col('gold', 5 if d == 0 else (4 if d == 1 else 3)))
                else:
                    c.px(x, y, col('gold', 8))
        c.px(cx, r(3) + 1, col('gold', 9))

        # ---- crossbar / lintel with the arcane rune (the only cool accent)
        bar = (Y >= bar_y0) & (Y < bar_y1) & peak
        c.put(bar, col('gold', 5))
        c.put(bar & (Y == bar_y0), col('gold', 8))
        c.put(bar & (Y == bar_y1 - 1), col('gold', 3))
        ry = bar_y0 + (1 if bar_h >= 3 else 0)
        rw = max(1, r(2))
        c.put(rect_mask(W, H, cx - rw, ry, cx + rw + 1, ry + 1), col('arcane', 5))
        c.px(cx, ry, col('arcane', 7))
        if rw >= 2:
            c.px(cx - rw - 1, ry, col('gold', 2))
            c.px(cx + rw + 1, ry, col('gold', 2))

        # ---- base ledge (one tone on top, single darker pixel at the right end)
        k = (s(59) - s(3)) / 3.0
        ledge = (Y >= base_y) & (Y < base_y + max(2, r(3))) & (np.abs(X - self.CX + 0.5) <= k + 1) & field
        c.put(ledge, col('stone', 4))
        top_row = ledge & (Y == base_y)
        c.put(top_row, col('stone', 6))
        xs = np.where(top_row.any(0))[0]
        if len(xs):
            c.px(xs.max(), base_y, col('stone', 5))
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
