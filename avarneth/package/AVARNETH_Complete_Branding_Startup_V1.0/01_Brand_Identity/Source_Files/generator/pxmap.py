"""Pixel map <-> PNG via palette letter codes (for hand-tuned small icons)."""
import numpy as np
from PIL import Image
from pix import RAMPS

# letter codes: ramp prefix char + index digit  -> we use 2-char cells "g7", "i0", "..".
PRE = {'iron': 'i', 'gold': 'g', 'stone': 's', 'ember': 'e', 'arcane': 'a'}
INV = {v: k for k, v in PRE.items()}

def to_map(arr):
    lut = {}
    for r, cols in RAMPS.items():
        for i, c in enumerate(cols):
            lut[tuple(c)] = PRE[r] + str(i)
    rows = []
    for y in range(arr.shape[0]):
        row = []
        for x in range(arr.shape[1]):
            p = arr[y, x]
            if p[3] == 0:
                row.append('..')
            else:
                row.append(lut.get(tuple(int(v) for v in p[:3]), '??'))
        rows.append(' '.join(row))
    return '\n'.join(rows)

def from_map(text):
    rows = [r.split() for r in text.strip('\n').split('\n') if r.strip()]
    h, w = len(rows), max(len(r) for r in rows)
    a = np.zeros((h, w, 4), np.uint8)
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c == '..':
                continue
            ramp = INV[c[0]]; i = int(c[1])
            a[y, x, :3] = RAMPS[ramp][i]; a[y, x, 3] = 255
    return a

if __name__ == '__main__':
    import sys
    print(to_map(np.array(Image.open(sys.argv[1]).convert('RGBA'))))
