"""Small icon emblems (16, 20, 24, 30, 32, 36, 40 px) - revision 2.

At these sizes the full emblem turns to mush, so a reduced drawing is laid out on
the pixel grid per size: ONE closed shield silhouette (unbroken dark outline,
gold rim, mid-iron plate that stays visible on a dark taskbar), the A as two
clearly gold legs (left lit, right one step darker - never brown) with a gold
crossbar, a dark upper counter with an arcane window, and below the crossbar a
dark gate opening with an ember core. No sparks, no pendant.
Every size is generated from the same rules and then checked at 1:1.
"""
from __future__ import annotations

import numpy as np
from pix import Canvas, col, poly_mask, bezier, mirror_x, outline, inner_edge, rect_mask


def build(size):
    N = size
    Wc = N if N % 2 == 1 else N - 1           # odd content width -> 1 px centre column
    cx = Wc // 2
    H = N
    X, Y = np.meshgrid(np.arange(Wc), np.arange(H))
    c = Canvas(Wc, H)

    big = N >= 30
    y_top = 2 if N < 24 else (3 if N < 36 else 4)            # shield top edge (outline row)
    y_side = int(round(N * 0.56))
    # ---- shield silhouette (outline included)
    half = [(Wc / 2.0, y_top), (0, y_top), (0, y_side)]
    half += bezier((0, y_side), (0.2, N * 0.86), (Wc / 2.0, N), 30)[1:]
    sil = mirror_x(poly_mask(Wc, H, half + [(Wc - x, y) for x, y in reversed(half)]))
    inside = sil & ~inner_edge(sil, diagonal=False)            # everything but the outline ring
    rim = inner_edge(inside, diagonal=False)
    plate = inside & ~rim
    rim2 = inner_edge(plate, diagonal=False) if big else np.zeros_like(rim)
    plate2 = plate & ~rim2

    low = int(round(N * 0.62))
    c.put(rim & (X <= cx), col('gold', 7))
    c.put(rim & (X > cx), col('gold', 5))
    c.put(rim & (X <= cx) & (Y >= low), col('gold', 6))
    c.put(rim & (X > cx) & (Y >= low), col('gold', 5))
    c.put(rim & (Y == y_top + 1), col('gold', 7))
    if big:
        c.put(rim2, col('gold', 4))
        c.put(rim2 & (X <= cx) & (Y < low), col('gold', 5))
    c.put(plate2 if big else plate, col('iron', 4))
    pe = inner_edge(plate2 if big else plate, diagonal=False)
    c.put(pe & ((X < cx) | (Y <= y_top + (3 if big else 2))) & (Y < low), col('iron', 5))

    # ---- the A (gold legs) - apex rises above the shield top
    y_b = int(round(N * 0.80))                       # base of the A
    hw = max(4, int(round(N * 0.30)))                # half width at the base
    lt = 1 if N < 24 else (2 if N < 40 else 3)       # leg thickness
    apex = 0
    slope = (y_b - apex) / hw

    def leg_x(y):                                    # outer half width at row y
        return int(np.floor((y - apex) / slope + 0.5))

    peak = np.zeros((H, Wc), bool)
    for y in range(apex, y_b + 1):
        k = leg_x(y)
        peak[y, cx - k:cx + k + 1] = True
    inner = np.zeros_like(peak)
    for y in range(apex, y_b + 1):
        k = leg_x(y) - lt
        if k >= 0 and y > apex + lt:
            inner[y, cx - k:cx + k + 1] = True
    legs = peak & ~inner
    c.put(legs & (X <= cx), col('gold', 7))
    c.put(legs & (X > cx), col('gold', 5))
    c.put(legs & (X == cx), col('gold', 8))
    c.px(cx, apex, col('gold', 9))
    if lt >= 2:
        il = legs & ~np.roll(legs, -1, axis=1) & (X < cx)      # inner pixel of the left leg
        ir = legs & ~np.roll(legs, 1, axis=1) & (X > cx)       # inner pixel of the right leg
        c.put(il, col('gold', 6))
        c.put(ir, col('gold', 4))

    # crossbar
    y_c = int(round(apex + (y_b - apex) * 0.56))
    bt = 1 if N < 30 else 2
    bar = peak & (Y >= y_c) & (Y < y_c + bt)
    c.put(bar, col('gold', 7))
    if bt == 2:
        c.put(bar & (Y == y_c + 1), col('gold', 4))

    upper = inner & (Y < y_c)
    lower = inner & (Y >= y_c + bt)
    c.put(upper, col('iron', 1))
    c.put(lower, col('stone', 4))
    c.put(lower & (X > cx + (1 if N < 24 else 1)), col('stone', 3))

    # keep tower in the upper counter (>= 30 px): slim stone block with a dark arrow slit
    if N >= 30:
        t_top = max(apex + lt + 3, y_c - 5)
        tower = (np.abs(X - cx) <= 1) & (Y >= t_top) & (Y < y_c) & upper
        c.put(tower, col('stone', 5))
        c.put(tower & (X == cx + 1), col('stone', 3))
        c.put(tower & (Y == t_top), col('stone', 7))
        c.px(cx, t_top, col('iron', 1))                       # crenel between two merlons
        c.put(tower & (X == cx) & (Y >= y_c - 3) & (Y < y_c - 1), col('iron', 0))

    # arcane rune set into the gold crossbar (the only cool accent)
    if N >= 30:
        for dx in (-1, 0, 1):
            c.px(cx + dx, y_c, col('arcane', 5))
        c.px(cx, y_c, col('arcane', 7))
    else:
        c.px(cx, y_c, col('arcane', 6))

    # gate: dark arched opening, ember glow only at its foot
    g_top = y_c + bt + 1
    gw = 1 if N < 30 else 2                          # half width of the opening
    gate = (np.abs(X - cx) <= gw) & (Y >= g_top) & (Y <= y_b) & inner
    gate &= ~((Y == g_top) & (np.abs(X - cx) == gw))         # rounded arch corners
    c.put(gate, col('ember', 1))
    t = (Y - g_top) / max(1, y_b - g_top)
    c.put(gate & (t >= 0.5), col('ember', 3))
    c.put(gate & (t >= 0.75) & (np.abs(X - cx) <= max(0, gw - 1)), col('ember', 6))
    c.put(gate & (Y == y_b) & (X == cx), col('ember', 7))
    if N >= 30:
        c.put(gate & (((X - cx) % 2) == 1) & (t < 0.75), col('iron', 4))
    c.put((outline(gate) & lower) & ~gate, col('stone', 6))

    # dark separation around the A legs on the plate
    sep = outline(peak) & (plate2 if big else plate)
    c.put(sep, col('iron', 1))
    by = y_b + 1
    k = leg_x(y_b)
    for x in range(cx - k, cx + k + 1):
        if 0 <= by < H and (plate2 if big else plate)[by, x]:        # never across the gold rim
            c.px(x, by, col('iron', 1))

    if N >= 30:                                                      # 2 px ember stone in the tip
        gy = y_b + 3
        if gy + 1 < H - 1 and inside[gy + 1, cx]:
            c.px(cx, gy, col('ember', 7))
            c.px(cx, gy + 1, col('ember', 4))

    # ---- global outline (shield + peak above it)
    m = c.alpha_mask()
    c.put(outline(m), col('iron', 0))
    out = Canvas(N, N)
    out.a[:, 0:Wc] = c.a
    return out


SIZES = (16, 20, 24, 28, 30, 32, 36, 40, 42)


if __name__ == '__main__':
    from pxmap import to_map
    for s in SIZES:
        print(s)
        print(to_map(build(s).a))
