"""Debug viewer: show an RGBA PNG on dark + checker backgrounds at integer zoom."""
import sys
import numpy as np
from PIL import Image
from pix import alpha_over, checker_bg

def sheet(paths, zoom, out, bg=(20, 22, 28)):
    ims = [np.array(Image.open(p).convert('RGBA')) for p in paths]
    tiles = []
    for a in ims:
        h, w = a.shape[:2]
        d = np.zeros((h + 4, w + 4, 4), np.uint8); d[..., :3] = bg; d[..., 3] = 255
        alpha_over(d, a, 2, 2)
        k = checker_bg(w + 4, h + 4, 4)
        alpha_over(k, a, 2, 2)
        t = np.concatenate([d, k], axis=1)
        t = np.repeat(np.repeat(t, zoom, 0), zoom, 1)
        tiles.append(t)
    H = sum(t.shape[0] for t in tiles); W = max(t.shape[1] for t in tiles)
    o = np.zeros((H, W, 4), np.uint8); o[..., 3] = 255
    y = 0
    for t in tiles:
        o[y:y + t.shape[0], :t.shape[1]] = t; y += t.shape[0]
    Image.fromarray(o).save(out)

if __name__ == '__main__':
    zoom = int(sys.argv[1]); out = sys.argv[2]
    sheet(sys.argv[3:], zoom, out)
