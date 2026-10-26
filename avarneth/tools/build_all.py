"""Build every AVARNETH branding/startup deliverable into the package folder.

    python3 build_all.py [stage ...]     stages: brand variants icons startup frames sheets previews sources
                                         (default: all)

Deterministic: the same sources always produce the same pixels.
"""
from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import emblem as emblem_mod  # noqa: E402
import wordmark as wordmark_mod  # noqa: E402
import brand  # noqa: E402
import variants  # noqa: E402
import icons as icons_mod  # noqa: E402
import icons_small  # noqa: E402
import startup  # noqa: E402
import timeline_eval as te  # noqa: E402
import preview_bg  # noqa: E402
from pix import Canvas, alpha_over, RAMPS, checker_bg  # noqa: E402
from fonts import STEEL7, text_mask, styled  # noqa: E402
import pxmap  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..'))
PKG = os.environ.get('AVARNETH_PACKAGE_DIR') or os.path.join(ROOT, 'package', 'AVARNETH_Complete_Branding_Startup_V1.0')
P = lambda *a: os.path.join(PKG, *a)  # noqa: E731


def mkdir(p):
    os.makedirs(p, exist_ok=True)
    return p


def save(arr, path, scale=1):
    mkdir(os.path.dirname(path))
    im = Image.fromarray(arr, 'RGBA')
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path, optimize=True)


def stack(items, gaps, pad=4):
    """Vertically stack canvases (centred). items: list of Canvas; gaps between them."""
    W = max(c.w for c in items) + 2 * pad
    H = sum(c.h for c in items) + sum(gaps) + 2 * pad
    out = Canvas(W, H)
    y = pad
    for i, c in enumerate(items):
        alpha_over(out.a, c.a, (W - c.w) // 2, y)
        y += c.h + (gaps[i] if i < len(gaps) else 0)
    return out


def pad_canvas(c, pad=4):
    out = Canvas(c.w + 2 * pad, c.h + 2 * pad)
    alpha_over(out.a, c.a, pad, pad)
    return out


# ---------------------------------------------------------------------------
def brand_assets(ext_depth=2):
    emb = emblem_mod.build(1.0, 'full')
    wm = wordmark_mod.build(ext_depth=ext_depth)
    sub = brand.build_subtitle()
    sub_plain = brand.build_subtitle(with_flourish=False)
    pres = brand.build_presents_line()
    name = brand.build_publisher('ECKERTENGINEERING')
    return {
        'AVARNETH_Logo': pad_canvas(wm),                                   # Variant A
        'AVARNETH_Logo_With_Emblem': stack([emb, wm], [4]),                # Variant A + optional emblem
        'AVARNETH_Complete_Logo': stack([emb, wm, sub], [4, 4]),           # Variant B
        'AVARNETH_Publisher_Presentation': stack([pres, emb, wm, sub], [9, 4, 4]),  # Variant C
        'AVARNETH_Emblem': pad_canvas(emb),                                # Variant D
        'AVARNETH_VeilOfEmbers': pad_canvas(sub),
        'AVARNETH_VeilOfEmbers_Plain': pad_canvas(sub_plain),
        'Eckertengineering_Presents': pad_canvas(pres),
        'Eckertengineering': pad_canvas(name),
    }


def stage_brand():
    assets = brand_assets()
    main = P('01_Brand_Identity')
    for n, c in assets.items():
        save(c.a, os.path.join(main, n + '.png'), 4)
        save(c.a, os.path.join(main, 'Source_Files', 'native_1x', n + '_1x.png'))
        save(c.a, os.path.join(main, 'Source_Files', 'exports_2x', n + '_2x.png'), 2)
        save(c.a, os.path.join(main, 'Source_Files', 'exports_8x', n + '_8x.png'), 8)
    return assets


def card(c: Canvas, scale, label, bg=(14, 15, 21)):
    big = np.repeat(np.repeat(c.a, scale, 0), scale, 1)
    lab = styled(text_mask(STEEL7, label, tracking=1, space=3), ('iron', 7), edge=('iron', 0), shadow=('iron', 1), pad=1)
    labbig = np.repeat(np.repeat(lab.a, 2, 0), 2, 1)
    W = max(big.shape[1], labbig.shape[1]) + 64
    H = big.shape[0] + labbig.shape[0] + 72
    out = np.zeros((H, W, 4), np.uint8)
    out[..., :3] = bg
    out[..., 3] = 255
    alpha_over(out, big, (W - big.shape[1]) // 2, 24)
    alpha_over(out, labbig, (W - labbig.shape[1]) // 2, H - labbig.shape[0] - 20)
    return out


def stage_variants():
    cards = []
    for theme in ('Classic_Fantasy', 'Dark_Fantasy', 'Magic_And_Iron'):
        assets = brand_assets(variants.EXTRUSION[theme])
        d = P('02_Logo_Variants', theme)
        for n in ('AVARNETH_Emblem', 'AVARNETH_Logo', 'AVARNETH_Complete_Logo', 'AVARNETH_Publisher_Presentation'):
            arr = variants.recolor(assets[n].a, theme)
            save(arr, os.path.join(d, f'{n}_{theme}.png'), 4)
            save(arr, os.path.join(d, 'native_1x', f'{n}_{theme}_1x.png'))
        cc = Canvas(assets['AVARNETH_Complete_Logo'].w, assets['AVARNETH_Complete_Logo'].h)
        cc.a = variants.recolor(assets['AVARNETH_Complete_Logo'].a, theme)
        label = theme.replace('_', ' ').upper() + (' - PRODUCTION STANDARD' if theme == 'Magic_And_Iron' else '')
        cd = card(cc, 3, label)
        save(cd, os.path.join(d, f'Preview_Card_{theme}.png'))
        with open(os.path.join(d, 'DESIGN_NOTE.txt'), 'w') as f:
            f.write(variants.DESCRIPTIONS[theme] + '\n\nDesignrichtung als Material-/Farbwelt: gleiche Geometrie wie der '
                    'Produktionsstandard (bewusst dieselbe Markenidentität), Material und Farbe per exaktem Paletten-Remapping, '
                    'eigene Extrusionstiefe. Keine abweichenden Logo-Konzepte (siehe 07_Documentation/BRAND_GUIDELINES.md, Abschnitt 8).\n')
        cards.append(cd)
    H = max(c.shape[0] for c in cards)
    W = sum(c.shape[1] for c in cards)
    ov = np.zeros((H, W, 4), np.uint8)
    ov[..., :3] = (14, 15, 21)
    ov[..., 3] = 255
    x = 0
    for c in cards:
        ov[:c.shape[0], x:x + c.shape[1]] = c
        x += c.shape[1]
    save(ov, P('02_Logo_Variants', 'Variants_Overview.png'))


def stage_icons():
    ic = icons_mod.build_all()
    d = P('03_Windows_Icons')
    for s in (16, 24, 32, 48, 64, 128, 256, 512):
        save(ic[s].a, os.path.join(d, f'AVARNETH_{s}.png'))
    for s in sorted(set(ic) - {16, 24, 32, 48, 64, 128, 256, 512}):
        save(ic[s].a, os.path.join(d, 'Extra', f'AVARNETH_{s}.png'))
    icons_mod.write_ico(os.path.join(d, 'AVARNETH.ico'), ic)
    # Unity copies (PlayerSettings icon slots - the helper picks exact sizes)
    for s in sorted(ic):
        save(ic[s].a, P('05_Unity_Integration', 'Importable_Assets', 'Icons', f'AVE_Icon_{s}.png'))
    # pixel maps of the per-size drawings (editable source)
    src = mkdir(P('01_Brand_Identity', 'Source_Files', 'pixelmaps'))
    for s in icons_small.SIZES + (48, 64):
        with open(os.path.join(src, f'AVARNETH_Icon_{s}.pixelmap.txt'), 'w') as f:
            f.write(f'# AVARNETH icon {s}x{s} - palette cell codes (see palette/AVARNETH_Palette.txt), .. = transparent\n')
            f.write(pxmap.to_map(ic[s].a) + '\n')
    return ic


def stage_startup():
    tl, sprites, lockup = startup.build()
    ia = P('05_Unity_Integration', 'Importable_Assets')
    for rel, c in sprites.items():
        save(c.a, os.path.join(ia, rel))
    js = json.dumps(tl, indent=2)
    for path in (os.path.join(ia, 'Animation_Timeline.json'), P('04_Animated_Startup', 'Animation_Timeline.json')):
        mkdir(os.path.dirname(path))
        with open(path, 'w') as f:
            f.write(js + '\n')
    # 04 layer folders: native + @4x (1080p) copies
    a4 = P('04_Animated_Startup')
    logo_layers = ['AVE_Emblem', 'AVE_Wordmark', 'AVE_Subtitle', 'AVE_Publisher']
    fx_layers = ['AVE_Veil', 'AVE_EmblemGlow', 'AVE_EmblemFlash', 'AVE_EmblemOutlineGlow', 'AVE_WordmarkFlash']
    for n in logo_layers:
        c = sprites[f'Layers/{n}.png']
        save(c.a, os.path.join(a4, 'Logo_Layers', f'{n}.png'))
        save(c.a, os.path.join(a4, 'Logo_Layers', '1080p_4x', f'{n}@4x.png'), 4)
    for n in fx_layers:
        c = sprites[f'Layers/{n}.png']
        save(c.a, os.path.join(a4, 'Effect_Layers', f'{n}.png'))
        save(c.a, os.path.join(a4, 'Effect_Layers', '1080p_4x', f'{n}@4x.png'), 4)
    for rel, c in sprites.items():
        if rel.startswith('Frames/'):
            save(c.a, os.path.join(a4, 'Effect_Layers', 'Flipbooks', os.path.basename(rel)))
        if rel.startswith('Particles/'):
            save(c.a, os.path.join(a4, 'Particle_Sprites', os.path.basename(rel)))
            save(c.a, os.path.join(a4, 'Particle_Sprites', 'preview_8x', os.path.basename(rel).replace('.png', '@8x.png')), 8)
    with open(os.path.join(ROOT, 'work', 'lockup.json'), 'w') as f:
        json.dump({k: [int(v[0]), int(v[1])] for k, v in lockup.items()}, f)
    return tl, sprites


def sheet(frames, cols, path, meta_extra):
    fw, fh = frames[0].w, frames[0].h
    rows = math.ceil(len(frames) / cols)
    out = np.zeros((rows * fh, cols * fw, 4), np.uint8)
    rects = []
    for i, f in enumerate(frames):
        x, y = (i % cols) * fw, (i // cols) * fh
        out[y:y + fh, x:x + fw] = f.a
        rects.append({'index': i, 'x': x, 'y': y, 'w': fw, 'h': fh})
    save(out, path)
    meta = {'image': os.path.basename(path), 'frameWidth': fw, 'frameHeight': fh, 'frameCount': len(frames),
            'columns': cols, 'rows': rows, 'origin': 'top-left, y down', 'frames': rects}
    meta.update(meta_extra)
    with open(path.replace('.png', '.json'), 'w') as f:
        json.dump(meta, f, indent=2)


def stage_sheets(tl, sprites):
    d = P('04_Animated_Startup', 'SpriteSheets')
    by_id = {L['id']: L for L in tl['layers']}
    for lid, name, cols in (('emblemTrace', 'AVE_EmblemTrace_Sheet', 7), ('wordmarkShine', 'AVE_WordmarkShine_Sheet', 1),
                            ('glint', 'AVE_Glint_Sheet', 8)):
        L = by_id[lid]
        frames = [sprites[p] for p in L['frames']]
        sheet(frames, cols, os.path.join(d, name + '.png'),
              {'layerId': lid, 'timelineStart': L['frameStart'], 'timelineEnd': L['frameEnd'],
               'afterFrames': L['afterFrames'], 'positionArtPx': [L['x'], L['y']],
               'note': 'Frames are evenly distributed over [timelineStart, timelineEnd) - see Animation_Timeline.json.'})
    parts = [sprites[p] for p in tl['particleSprites']]
    cell = max(max(c.w, c.h) for c in parts)
    out = np.zeros((cell, cell * len(parts), 4), np.uint8)
    rects = []
    for i, c in enumerate(parts):
        x, y = i * cell + (cell - c.w) // 2, (cell - c.h) // 2
        out[y:y + c.h, x:x + c.w] = c.a
        rects.append({'index': i, 'x': x, 'y': y, 'w': c.w, 'h': c.h, 'source': tl['particleSprites'][i]})
    save(out, os.path.join(d, 'AVE_Particles_Sheet.png'))
    with open(os.path.join(d, 'AVE_Particles_Sheet.json'), 'w') as f:
        json.dump({'image': 'AVE_Particles_Sheet.png', 'frames': rects,
                   'note': 'Exact sprite rects (sprites have different sizes). Particle tracks: Animation_Timeline.json'}, f, indent=2)


def stage_frames(tl, sprites):
    arr = {k: v.a for k, v in sprites.items()}
    d60 = mkdir(P('04_Animated_Startup', 'Animation_Frames', 'native_480x270_60fps'))
    d30 = mkdir(P('04_Animated_Startup', 'Animation_Frames', '1080p_1920x1080_30fps'))
    n60 = int(round(tl['duration'] * 60))
    for i in range(n60):
        f = te.render(tl, arr, i / 60.0)
        save(f, os.path.join(d60, f'AVE_Startup_{i:03d}.png'))
        if i % 2 == 0:
            save(f, os.path.join(d30, f'AVE_Startup_1080p_{i // 2:03d}.png'), 4)
    with open(P('04_Animated_Startup', 'Animation_Frames', 'FRAMES_INFO.txt'), 'w') as f:
        f.write(
            'Transparent full-overlay frames rendered from Animation_Timeline.json (straight alpha, RGBA PNG).\n'
            f'native_480x270_60fps : {n60} frames, frame i shows t = i/60 s (0.000 .. {(n60 - 1) / 60:.3f} s). '
            'Upscale x4 nearest-neighbour for 1920x1080.\n'
            f'1080p_1920x1080_30fps: {n60 // 2} frames, frame i shows t = i/30 s.\n'
            f'At t >= {tl["duration"]:.2f} s the overlay is fully transparent (finished).\n'
            'These frames are a reference / fallback; the Unity integration animates the separate layers instead.\n')


def stage_previews(tl, sprites):
    arr = {k: v.a for k, v in sprites.items()}
    d = mkdir(P('06_Previews'))
    tmp = mkdir(os.path.join(ROOT, 'work', 'preview_tmp'))
    fps, total = 60, 3.0
    n = int(round(total * fps))

    def login_alpha(t):
        return 0.0 if t < 1.6 else min(1.0, (t - 1.6) / 0.4)

    frames = []
    for i in range(n):
        t = i / fps
        base = preview_bg.frame(t, login_alpha(t))
        frames.append(te.render(tl, arr, t, base))
    mp4 = os.path.join(d, 'AVARNETH_Startup_Preview.mp4')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', str(fps),
           '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
           '-metadata', 'title=AVARNETH: VEIL OF EMBERS - startup preview (mock-up background)', mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in frames:
        big = np.repeat(np.repeat(f[..., :3], 4, 0), 4, 1)
        p.stdin.write(np.ascontiguousarray(big).tobytes())
    p.stdin.close()
    assert p.wait() == 0
    # GIF (960x540, 30 fps, no dithering for pixel art)
    for i in range(0, n, 2):
        Image.fromarray(np.repeat(np.repeat(frames[i][..., :3], 2, 0), 2, 1)).save(os.path.join(tmp, f'g{i // 2:03d}.png'))
    gif = os.path.join(d, 'AVARNETH_Startup_Preview.gif')
    subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', os.path.join(tmp, 'g%03d.png'),
                           '-vf', 'split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];[b][p]paletteuse=dither=none',
                           '-loop', '0', gif])
    # final logo still (on the mock-up) and on plain dark
    still = te.render(tl, arr, 1.50, preview_bg.frame(1.50, 0.0))
    save(still, os.path.join(d, 'AVARNETH_Logo_Preview.png'), 4)
    plain = np.zeros((270, 480, 4), np.uint8)
    plain[..., :3] = (12, 13, 19)
    plain[..., 3] = 255
    save(te.render(tl, arr, 1.50, plain), os.path.join(d, 'AVARNETH_Logo_Preview_Dark.png'), 4)
    contact_sheet(tl, arr, os.path.join(d, 'Animation_ContactSheet.png'))
    icon_preview(os.path.join(d, 'AVARNETH_Icon_Preview.png'))
    shutil.rmtree(tmp)


PHASES = [(0.0, 0.35, 'PHASE 1 EMBLEM'), (0.35, 1.15, 'PHASE 2 WORDMARK'), (1.15, 1.60, 'PHASE 3 SUBTITLE + EMBERS'),
          (1.60, 2.0, 'PHASE 4 ACCENT + FADE'), (2.0, 99, 'LOGIN SCENE')]


def contact_sheet(tl, arr, path):
    times = [0.00, 0.08, 0.17, 0.25, 0.33, 0.45, 0.60, 0.75, 0.90, 1.05, 1.20, 1.30, 1.42, 1.55, 1.63, 1.68, 1.76, 1.85,
             1.93, 2.10]
    cols = 4
    tw, th = 480, 270
    lab_h = 22
    rows = math.ceil(len(times) / cols)
    W = cols * tw + (cols + 1) * 12
    head = 40
    H = head + rows * (th + lab_h) + (rows + 1) * 12
    out = np.zeros((H, W, 4), np.uint8)
    out[..., :3] = (10, 11, 16)
    out[..., 3] = 255
    title = styled(text_mask(STEEL7, 'AVARNETH STARTUP - CONTACT SHEET - 2.00 S - PREVIEW MOCKUP BACKGROUND', tracking=1,
                             space=3), ('gold', 7), edge=('iron', 0), shadow=('iron', 1), pad=1)
    alpha_over(out, np.repeat(np.repeat(title.a, 2, 0), 2, 1), 12, 10)
    for k, t in enumerate(times):
        r, c = k // cols, k % cols
        x = 12 + c * (tw + 12)
        y = head + 12 + r * (th + lab_h + 12)
        la = 0.0 if t < 1.6 else min(1.0, (t - 1.6) / 0.4)
        f = te.render(tl, arr, t, preview_bg.frame(t, la))
        out[y:y + th, x:x + tw] = f
        ph = next(p for p in PHASES if p[0] <= t < p[1])[2]
        lab = styled(text_mask(STEEL7, f'T {t:.2f} S  {ph}', tracking=1, space=3), ('iron', 7), edge=('iron', 0),
                     shadow=('iron', 1), pad=1)
        alpha_over(out, lab.a, x + 2, y + th + 4)
    save(out, path)


def icon_preview(path):
    ic = icons_mod.build_all()
    sizes = (16, 20, 24, 28, 30, 32, 36, 40, 42, 48, 64, 128, 256)
    W, H = 1640, 760
    out = np.zeros((H, W, 4), np.uint8)
    out[..., 3] = 255
    out[:H // 2, :, :3] = (16, 17, 24)        # dark (taskbar-like)
    out[H // 2:, :, :3] = (236, 238, 242)     # light (explorer-like)
    for half, y0 in ((0, 0), (1, H // 2)):
        x = 24
        base = y0 + 40
        for s in sizes:
            alpha_over(out, ic[s].a, x, base + (256 - s) // 2 if s < 256 else base)
            lab = styled(text_mask(STEEL7, f'{s}', tracking=1), ('iron', 7) if half == 0 else ('iron', 2),
                         edge=('iron', 0) if half == 0 else ('iron', 8), shadow=('iron', 1) if half == 0 else ('iron', 7), pad=1)
            alpha_over(out, lab.a, x, base + 262)
            x += s + 22
        # zoomed small sizes for inspection
        zx = W - 3 * (32 * 4 + 16) - 8
        for s in (16, 24, 32):
            z = np.repeat(np.repeat(ic[s].a, 4, 0), 4, 1)
            alpha_over(out, z, zx, y0 + 20 + (128 - z.shape[0]))
            zx += 32 * 4 + 16
    title = styled(text_mask(STEEL7, 'AVARNETH ICON - ACTUAL SIZE 1:1 ON DARK AND LIGHT - SMALL SIZES ALSO 4X ZOOM', tracking=1,
                             space=3), ('gold', 7), edge=('iron', 0), shadow=('iron', 1), pad=1)
    alpha_over(out, title.a, 24, 8)
    save(out, path)


def stage_guides():
    """Construction / clear-space sheet for BRAND_GUIDELINES.md."""
    assets = brand_assets()
    logo = assets['AVARNETH_Complete_Logo']
    k = 3
    X = 32                      # unit = wordmark cap height (art px)
    cs = X // 2                 # clear space = X/2
    big = np.repeat(np.repeat(logo.a, k, 0), k, 1)
    pad = 40
    W = big.shape[1] + 2 * (cs * k + pad) + 380
    H = big.shape[0] + 2 * (cs * k + pad) + 60
    out = np.zeros((H, W, 4), np.uint8)
    out[..., :3] = (12, 13, 19)
    out[..., 3] = 255
    ox, oy = cs * k + pad, cs * k + pad + 30
    # art-pixel grid (every 4 art px) behind the logo area
    for gx in range(ox, ox + big.shape[1] + 1, 4 * k):
        out[oy:oy + big.shape[0], gx, :3] = (24, 26, 34)
    for gy in range(oy, oy + big.shape[0] + 1, 4 * k):
        out[gy, ox:ox + big.shape[1], :3] = (24, 26, 34)
    alpha_over(out, big, ox, oy)
    # content box (trimmed) and clear-space box (dashed)
    a = logo.a[..., 3] > 0
    ys, xs = np.where(a)
    bx0, by0, bx1, by1 = ox + xs.min() * k, oy + ys.min() * k, ox + (xs.max() + 1) * k, oy + (ys.max() + 1) * k
    def dashed(x0, y0, x1, y1, colr):
        for x in range(x0, x1):
            if (x // 6) % 2 == 0:
                out[y0, x, :3] = colr; out[y1, x, :3] = colr
        for y in range(y0, y1 + 1):
            if (y // 6) % 2 == 0:
                out[y, x0, :3] = colr; out[y, x1, :3] = colr
    dashed(bx0, by0, bx1, by1, (110, 115, 130))
    dashed(bx0 - cs * k, by0 - cs * k, bx1 + cs * k, by1 + cs * k, tuple(RAMPS['gold'][6]))
    def label(text, x, y, ramp=('iron', 7), z=2):
        t = styled(text_mask(STEEL7, text, tracking=1, space=3), ramp, edge=('iron', 0), shadow=('iron', 1), pad=1)
        alpha_over(out, np.repeat(np.repeat(t.a, z, 0), z, 1), x, y)
    label('AVARNETH - CONSTRUCTION AND CLEAR SPACE - SHOWN AT 3X', 12, 10, ('gold', 7))
    lx = bx1 + cs * k + 24
    label('X = 32 ART PX = CAP HEIGHT', lx, by0 + 10)
    label('CLEAR SPACE = X/2 = 16 ART PX', lx, by0 + 40, ('gold', 7))
    label('GRID = 4 ART PX', lx, by0 + 70)
    label('LIGHT: TOP LEFT', lx, by0 + 100)
    label('SCALE: INTEGER NEAREST ONLY', lx, by0 + 130)
    # X marker next to the wordmark cap
    save(out, P('07_Documentation', 'images', 'AVARNETH_Construction_ClearSpace.png'))


def stage_sources():
    src = mkdir(P('01_Brand_Identity', 'Source_Files'))
    gen = mkdir(os.path.join(src, 'generator'))
    for fn in sorted(os.listdir(HERE)):
        if fn.endswith('.py') and fn not in ('viewer.py',):
            shutil.copy2(os.path.join(HERE, fn), os.path.join(gen, fn))
    pal = mkdir(os.path.join(src, 'palette'))
    lines = ['GIMP Palette', 'Name: AVARNETH Master Palette', 'Columns: 10', '#']
    txt = ['# AVARNETH master palette - cell code, ramp, index, hex', '# cell codes: i=iron g=gold s=stone e=ember a=arcane']
    hexes = []
    for ramp, cols in RAMPS.items():
        for i, c in enumerate(cols):
            lines.append(f'{c[0]:3d} {c[1]:3d} {c[2]:3d}\t{ramp}{i}')
            code = {'iron': 'i', 'gold': 'g', 'stone': 's', 'ember': 'e', 'arcane': 'a'}[ramp] + str(i)
            hx = '#%02x%02x%02x' % tuple(c)
            txt.append(f'{code}\t{ramp}\t{i}\t{hx}')
            hexes.append(hx[1:])
    with open(os.path.join(pal, 'AVARNETH_Palette.gpl'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    with open(os.path.join(pal, 'AVARNETH_Palette.hex'), 'w') as f:
        f.write('\n'.join(hexes) + '\n')
    with open(os.path.join(pal, 'AVARNETH_Palette.txt'), 'w') as f:
        f.write('\n'.join(txt) + '\n')
    # swatch
    sw = 24
    rows = len(RAMPS)
    mx = max(len(v) for v in RAMPS.values())
    a = np.zeros((rows * sw, mx * sw, 4), np.uint8)
    for r, (ramp, cols) in enumerate(RAMPS.items()):
        for i, c in enumerate(cols):
            a[r * sw:(r + 1) * sw, i * sw:(i + 1) * sw] = (*c, 255)
    save(a, os.path.join(pal, 'AVARNETH_Palette_Swatch.png'))
    with open(os.path.join(src, 'README_SOURCE_FILES.txt'), 'w') as f:
        f.write(
            'AVARNETH source data\n'
            '====================\n'
            'native_1x/   Master pixel art at native resolution (1 art pixel = 1 image pixel), as generated.\n'
            '             Use these as the reference for any manual retouching; note that re-running the generator\n'
            '             recreates all files from code (edit generator/*.py to change the art permanently).\n'
            'exports_2x/  Integer nearest-neighbour upscales x2.\n'
            'exports_8x/  Integer nearest-neighbour upscales x8 (4K / print).\n'
            '             (The x4 exports - 1080p - are in the parent folder.)\n'
            'palette/     Master palette (GIMP .gpl, .hex, code table, swatch). All brand pixels use only these colours.\n'
            'pixelmaps/   Generated text dumps (palette cell codes) of the per-size icon drawings 16-42 px and the\n'
            '             48/64 px icon masters - for review and manual pixel edits; they are output, not input.\n'
            'generator/   Python 3 sources that generate every asset deterministically\n'
            '             (numpy, pillow, scipy; ffmpeg for previews):\n'
            '               AVARNETH_PACKAGE_DIR=/path/to/output python3 build_all.py\n'
            '             Without AVARNETH_PACKAGE_DIR the output goes to ../package/AVARNETH_Complete_Branding_Startup_V1.0\n'
            '             relative to the generator folder (copy generator/ to a work folder first).\n'
            '             qa.py / crosscheck.py / qa_report.py / finalize.py are the QA tools used for this delivery; the C#\n'
            '             checks additionally need the compile harness described in 07_Documentation/UNITY_COMPILE_EVIDENCE.md\n'
            '             (not shipped: it contains signatures copied from Unity\'s reference-only source).\n'
            'Never scale these images with bilinear/bicubic filtering - integer nearest-neighbour only.\n')


def main(stages):
    allst = ['brand', 'variants', 'icons', 'startup', 'sheets', 'frames', 'previews', 'guides', 'sources']
    stages = stages or allst
    tl = sprites = None
    for st in allst:
        if st not in stages:
            continue
        print('==>', st, flush=True)
        if st == 'brand':
            stage_brand()
        elif st == 'variants':
            stage_variants()
        elif st == 'icons':
            stage_icons()
        elif st == 'startup':
            tl, sprites = stage_startup()
        elif st in ('sheets', 'frames', 'previews'):
            if tl is None:
                tl, sprites, _ = startup.build()
            {'sheets': stage_sheets, 'frames': stage_frames, 'previews': stage_previews}[st](tl, sprites)
        elif st == 'guides':
            stage_guides()
        elif st == 'sources':
            stage_sources()


if __name__ == '__main__':
    main(sys.argv[1:])
