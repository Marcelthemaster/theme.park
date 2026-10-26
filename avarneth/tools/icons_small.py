"""Hand-specified small icon emblems (16 / 24 / 32 px).

At these sizes the procedural emblem turns to mush, so each size is laid out
row by row on the pixel grid: a simplified shield (single gold rim), the A-peak
with gold flanks, the blue window, the gold crossbar and the glowing gate, and
the ember gem in the shield tip. The result is exported both as PNG and as a
palette pixel map (Source_Files) so it can be retouched by hand.
"""
from __future__ import annotations

import numpy as np
from pix import col, Canvas

C = {
    '0': ('iron', 0), '1': ('iron', 2), '2': ('iron', 3), '3': ('stone', 2), '4': ('iron', 5),
    'G': ('gold', 7), 'g': ('gold', 5), 'd': ('gold', 3), 'D': ('gold', 2), 'W': ('gold', 9), 'Y': ('gold', 8),
    'L': ('stone', 5), 'M': ('stone', 3), 'n': ('stone', 1), 'R': ('stone', 6), 'S': ('stone', 7),
    'b': ('arcane', 4), 'B': ('arcane', 7),
    'r': ('ember', 1), 'q': ('ember', 2), 'e': ('ember', 3), 'f': ('ember', 5), 'F': ('ember', 7), 'H': ('ember', 8),
}


def to_canvas(rows, size):
    h = len(rows)
    w = max(len(r) for r in rows)
    c = Canvas(size, size)
    ox = (size - w) // 2
    oy = (size - h) // 2
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in C:
                c.px(ox + x, oy + y, col(*C[ch]))
    return c


def build_grid(W, H, cx, shield_top, left_edge, peak_k, rim, field_bands, gate, window, bar, base_y, gem, sparks=()):
    """Rule-based layout on a char grid; outlines/rims are derived from masks so
    stepped diagonals stay continuous. left_edge: row -> left outline x (mirrored)."""
    from pix import inner_edge, outline as outline_of
    g = np.full((H, W), '.', dtype='<U1')

    def setp(x, y, ch):
        if 0 <= x < W and 0 <= y < H:
            g[y, x] = ch

    # --- shield interior (inside the outline)
    inside = np.zeros((H, W), bool)
    for y, lx in left_edge.items():
        if y <= shield_top or y >= H - 1:
            continue
        inside[y, lx + 1:W - 1 - lx] = True
    # point row(s) at the very bottom stay outline
    for y in range(H):
        for x in range(W):
            if inside[y, x]:
                ch = '1'
                for (y0, fch) in field_bands:
                    if y >= y0:
                        ch = fch
                g[y, x] = ch
    rimm = inner_edge(inside, diagonal=False)
    low = H - 6
    for y, x in zip(*np.where(rimm)):
        if y == shield_top + 1:
            ch = 'G' if x < W - 2 else 'g'
        elif x < cx:
            ch = 'G' if y < low else 'g'
        elif x > cx:
            ch = 'g' if y < low else 'd'
        else:
            ch = 'd'
        g[y, x] = ch
    if rim == 2:
        rim2 = inner_edge(inside & ~rimm, diagonal=False)
        g[rim2] = 'D'

    gy, gch = gem
    for (dx, dy, ch) in gch:
        setp(cx + dx, gy + dy, ch)
    for (sx, sy, ch) in sparks:
        setp(sx, sy, ch)

    # --- peak
    peak = np.zeros((H, W), bool)
    for y in range(0, base_y + 1):
        k = peak_k(y)
        x0, x1 = cx - k, cx + k
        for x in range(x0, x1 + 1):
            peak[y, x] = True
            d_l, d_r = x - x0, x1 - x
            if x == cx:
                ch = 'Y' if k <= 1 or d_l < 2 else 'S'
            elif d_l < 2 and x < cx:
                ch = 'G' if d_l == 0 else 'g'
            elif d_r < 2 and x > cx:
                ch = 'd' if d_r == 0 else 'D'
            else:
                ch = 'L' if x < cx else 'M'
            g[y, x] = ch
    g[0, cx] = 'W'
    # dark separation line between the peak and the shield field/rim
    sep = outline_of(peak) & (g != '.')
    g[sep] = '0'

    by, bh = bar
    for yy in range(by, by + bh):
        k = peak_k(yy)
        for x in range(cx - k, cx + k + 1):
            g[yy, x] = 'G' if yy == by else 'D'
    for (dx, dy, ch) in window:
        setp(cx + dx, dy, ch)
    for (dx, dy, ch) in gate:
        setp(cx + dx, dy, ch)
    k = peak_k(base_y)
    for x in range(cx - k - 1, cx + k + 2):
        if g[base_y + 1, x] != '.':
            setp(x, base_y + 1, 'R' if x < cx else 'L')

    # --- global silhouette outline
    m = g != '.'
    g[outline_of(m)] = '0'
    return [''.join(r) for r in g]


def icon32():
    W, H, cx = 31, 32, 15
    left = {5: 0}
    for y in range(6, 20):
        left[y] = 0
    left.update({20: 1, 21: 1, 22: 2, 23: 3, 24: 4, 25: 5, 26: 6, 27: 7, 28: 8, 29: 10, 30: 12, 31: 14})
    gate = []
    # arch: rows 19..26, cols -2..2 ; frame R around
    glow = {19: 'q', 20: 'e', 21: 'e', 22: 'f', 23: 'f', 24: 'F', 25: 'F', 26: 'H'}
    for y in range(19, 27):
        w = 1 if y == 19 else 2
        for dx in range(-w, w + 1):
            ch = glow[y]
            if abs(dx) == w and y >= 21:
                ch = {'e': 'q', 'f': 'e', 'F': 'f', 'H': 'F'}.get(ch, ch)
            gate.append((dx, y, ch))
        gate.append((-w - 1, y, 'S' if y > 19 else 'R'))
        gate.append((w + 1, y, 'R' if y > 19 else 'M'))
    gate += [(-1, 18, 'R'), (0, 18, 'W'), (1, 18, 'R'), (-2, 19, 'R'), (2, 19, 'R')]
    window = [(0, 10, 'b'), (-1, 11, 'b'), (0, 11, 'B'), (1, 11, 'b'), (0, 12, 'b'), (0, 9, 'n'), (0, 13, 'n')]
    gem = (29, [(0, -1, 'g'), (-1, 0, 'f'), (0, 0, 'H'), (1, 0, 'e'), (0, 1, 'f'),
                (-2, 0, 'r'), (2, 0, 'r'), (-1, -1, 'r'), (1, -1, 'r'), (-1, 1, 'r'), (1, 1, 'r')])
    rows = build_grid(W, H, cx, 5, left, lambda y: y // 3, 2,
                      [(8, '1'), (14, '2'), (21, '3')], gate, window, (16, 2), 26, gem,
                      sparks=[(5, 11, 'f'), (25, 14, 'e'), (7, 17, 'e')])
    return rows


def icon24():
    W, H, cx = 23, 24, 11
    left = {4: 0}
    for y in range(5, 14):
        left[y] = 0
    left.update({14: 1, 15: 1, 16: 2, 17: 3, 18: 4, 19: 5, 20: 6, 21: 7, 22: 9, 23: 10})
    glow = {14: 'e', 15: 'f', 16: 'f', 17: 'F', 18: 'H', 19: 'H'}
    gate = []
    for y in range(14, 20):
        w = 0 if y == 14 else 1
        for dx in range(-w, w + 1):
            ch = glow[y]
            if abs(dx) == 1 and y >= 16:
                ch = {'f': 'e', 'F': 'f', 'H': 'F'}[ch]
            gate.append((dx, y, ch))
        gate.append((-w - 1, y, 'S'))
        gate.append((w + 1, y, 'R'))
    gate += [(0, 13, 'W')]
    window = [(0, 7, 'b'), (0, 8, 'B'), (-1, 8, 'b'), (1, 8, 'b'), (0, 9, 'b')]
    gem = (21, [(0, 0, 'H'), (-1, 0, 'f'), (1, 0, 'e'), (0, 1, 'f'), (0, -1, 'r'), (-2, 0, 'r'), (2, 0, 'r')])
    rows = build_grid(W, H, cx, 4, left, lambda y: y // 3, 2,
                      [(6, '1'), (11, '2'), (16, '3')], gate, window, (11, 2), 19, gem,
                      sparks=[(4, 8, 'f'), (18, 10, 'e')])
    return rows


def icon16():
    W, H, cx = 15, 16, 7
    left = {3: 0}
    for y in range(4, 10):
        left[y] = 0
    left.update({10: 1, 11: 1, 12: 2, 13: 3, 14: 5, 15: 6})
    gate = [(0, 9, 'f'), (-1, 10, 'f'), (0, 10, 'H'), (1, 10, 'e'), (-1, 11, 'F'), (0, 11, 'H'), (1, 11, 'f'),
            (0, 8, 'W')]
    window = [(0, 5, 'B')]
    gem = (13, [(0, 0, 'F'), (0, 1, 'e')])
    rows = build_grid(W, H, cx, 3, left, lambda y: y // 3, 1,
                      [(5, '1'), (8, '2'), (11, '3')], gate, window, (7, 1), 11, gem)
    return rows


SIZES = {16: icon16, 24: icon24, 32: icon32}


def build(size):
    return to_canvas(SIZES[size](), size)


if __name__ == '__main__':
    for s, f in SIZES.items():
        print(s)
        print('\n'.join(f()))
