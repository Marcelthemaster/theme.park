"""Three design directions built on the same identity (same geometry, different
materials) via exact palette remapping - every pixel stays a palette colour.

* Magic_And_Iron  - production standard: dark iron, aged gold, ember, arcane blue.
* Classic_Fantasy - heraldic royal blue steel with bright gold (classic MMORPG).
* Dark_Fantasy    - monumental blackened silver with crimson embers.
"""
from __future__ import annotations

import numpy as np
from pix import RAMPS, _hex

EXTRA = {
    'royal': ['#05081a', '#0a1230', '#101c46', '#17285e', '#203877', '#2c4b8f', '#4064a8', '#5f86c4', '#8cb0de', '#c8dcf4'],
    'silver': ['#0a0a0c', '#16161a', '#222228', '#303038', '#40414b', '#565863', '#70737e', '#9195a0', '#b9bcc5', '#e6e8ec'],
    'crimson': ['#1c0306', '#3a060c', '#5e0b14', '#8a121c', '#b51d24', '#d9352e', '#f0604a', '#ff9a7e', '#ffd6c8'],
    'warmstone': ['#14110d', '#211d17', '#2e2820', '#3e362b', '#504638', '#665a47', '#7f725b', '#9c8e74'],
}
EXTRA = {k: [_hex(c) for c in v] for k, v in EXTRA.items()}

THEMES = {
    'Magic_And_Iron': {},
    'Classic_Fantasy': {'iron': ('royal', 0), 'stone': ('warmstone', 0)},
    'Dark_Fantasy': {'gold': ('silver', 1), 'ember': ('crimson', 0), 'stone': ('stone', -1), 'iron': ('iron', -1)},
}

# material treatment per direction: depth of the dark wordmark extrusion (art px)
EXTRUSION = {'Magic_And_Iron': 2, 'Classic_Fantasy': 3, 'Dark_Fantasy': 4}

DESCRIPTIONS = {
    'Magic_And_Iron': 'Produktionsstandard – magische Eisen-/Schmiede-Fantasy: dunkles Eisen, Altgold, Glut, arkanes Blau; schlanke 2-px-Extrusion.',
    'Classic_Fantasy': 'Klassische Fantasy – heraldisches Königsblau mit hellem Gold und warmem Stein; 3-px-Extrusion in Blau.',
    'Dark_Fantasy': 'Dunkle, monumentale Fantasy – geschwärztes Silber, karmesinrote Glut, tieferer Stein; schwere 4-px-Extrusion.',
}


def _ramp(name):
    return RAMPS[name] if name in RAMPS else EXTRA[name]


def lut(theme):
    out = {}
    for src, cols in RAMPS.items():
        dst, shift = THEMES[theme].get(src, (src, 0))
        dc = _ramp(dst)
        for i, c in enumerate(cols):
            j = max(0, min(len(dc) - 1, i + shift))
            out[tuple(c)] = tuple(dc[j])
    return out


def recolor(arr, theme):
    if not THEMES[theme]:
        return arr.copy()
    table = lut(theme)
    out = arr.copy()
    flat = out.reshape(-1, 4)
    keys = [tuple(int(v) for v in p[:3]) for p in flat]
    for n, k in enumerate(keys):
        if flat[n, 3] and k in table:
            flat[n, :3] = table[k]
    return out
