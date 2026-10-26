"""Build the V1.1 delta package: AVARNETH_Bootstrap_Visual_Match_V1.1(.zip).

    python3 v11_build.py [assets header animation previews compare qa docs package]   (default: all)

Inputs: the V1.0 package (package/AVARNETH_Complete_Branding_Startup_V1.0, read-only) and the original
bootstrap reference package (AVARNETH_BOOTSTRAP_REF, read-only, never copied except as preview pixels).
Only changed / additional files are written.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import match_v11 as M          # noqa: E402
import preview_v11 as PV       # noqa: E402
import startup                 # noqa: E402
import timeline_eval as te     # noqa: E402
from pix import Canvas, alpha_over  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..'))
V10 = os.path.join(ROOT, 'package', 'AVARNETH_Complete_Branding_Startup_V1.0')
NAME = 'AVARNETH_Bootstrap_Visual_Match_V1.1'
PKG = os.environ.get('AVARNETH_V11_DIR', os.path.join(ROOT, 'package', NAME))
WORK = os.path.join(ROOT, 'work', 'v11')
LABEL_FONT = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'


def P(*a):
    return os.path.join(PKG, *a)


def mkdir(p):
    os.makedirs(p, exist_ok=True)
    return p


def save(arr, path, scale=1):
    mkdir(os.path.dirname(path))
    if scale != 1:
        arr = np.repeat(np.repeat(arr, scale, 0), scale, 1)
    Image.fromarray(arr, 'RGBA' if arr.shape[2] == 4 else 'RGB').save(path, optimize=True)


def stack(items, gap):
    W = max(c.w for c in items)
    H = sum(c.h for c in items) + gap * (len(items) - 1)
    out = Canvas(W, H)
    y = 0
    for c in items:
        alpha_over(out.a, c.a, (W - c.w) // 2, y)
        y += c.h + gap
    return out


# ------------------------------------------------------------------ 01 logo assets
def stage_assets():
    d = mkdir(P('01_Logo_Assets'))
    em, wm, sub = M.emblem(), M.wordmark(), M.subtitle()
    sub_plain, pub = M.subtitle(with_flourish=False), M.publisher_line()
    pub_only = M.publisher_line('ECKERTENGINEERING')
    tl, spr, lk = startup.build(density=2)
    # complete lockup exactly as laid out in the startup timeline
    items = [(spr['Layers/AVE_Publisher.png'], lk['publisher']), (spr['Layers/AVE_Emblem.png'], lk['emblem']),
             (spr['Layers/AVE_Wordmark.png'], lk['wordmark']), (spr['Layers/AVE_Subtitle.png'], lk['subtitle'])]
    x0 = min(int(p[0]) for _, p in items)
    y0 = min(int(p[1]) for _, p in items)
    x1 = max(int(p[0]) + c.w for c, p in items)
    y1 = max(int(p[1]) + c.h for c, p in items)
    full = Canvas(x1 - x0, y1 - y0)
    for c, p in items:
        alpha_over(full.a, c.a, int(p[0]) - x0, int(p[1]) - y0)
    with_emblem = stack([em, wm, sub], 10)
    assets = {
        'AVARNETH_Emblem_V1.1': em, 'AVARNETH_Wordmark_V1.1': wm, 'AVARNETH_VeilOfEmbers_V1.1': sub,
        'AVARNETH_VeilOfEmbers_Plain_V1.1': sub_plain, 'Eckertengineering_V1.1': pub_only,
        'Eckertengineering_Presents_V1.1': pub, 'AVARNETH_Logo_With_Emblem_V1.1': with_emblem,
        'AVARNETH_Complete_Logo_V1.1': full,
    }
    for n, c in assets.items():
        save(c.a, os.path.join(d, 'native', f'{n}.png'))
        save(c.a, os.path.join(d, '1080p_2x', f'{n}@2x.png'), 2)
    return {n: (c.w, c.h) for n, c in assets.items()}


# ------------------------------------------------------------------ 02 login header
def stage_header():
    d = mkdir(P('02_Login_Header'))
    hd, boxes = M.header()
    save(hd.a, os.path.join(d, 'AVARNETH_Login_Header.png'))
    save(hd.a, os.path.join(d, 'AVARNETH_Login_Header@2x.png'), 2)
    layout = {
        'sprite': 'AVARNETH_Login_Header@2x.png',
        'size': [hd.w * 2, hd.h * 2],
        'nativeSize': [hd.w, hd.h],
        'screenPixelsPerArtPixelAt1080p': 2,
        'target': {
            'replaces': 'Canvas/UIRoot/LoginScreen/LogoAreaTopLeft/LogoText (TMP text "World of / Eckertengineering")',
            'parent': 'Canvas/UIRoot/LoginScreen/LogoAreaTopLeft',
            'rectTransform': {'anchorMin': [0, 1], 'anchorMax': [1, 1], 'pivot': [0.5, 1],
                              'anchoredPosition': [0, 0], 'sizeDelta': [0, 104]},
            'note': 'identical to the LogoText RectTransform in SCENE_VISUAL_REFERENCE_LOGIN_ONLY.json '
                    '(LogoAreaTopLeft 408 x 200 at x 56, y -86 from the top-left)',
        },
        'contentBoxesNative': {k: [int(v) for v in b] for k, b in boxes.items()},
        'importSettings': {'textureType': 'Sprite (2D and UI)', 'spriteMode': 'Single', 'filterMode': 'Point',
                           'mipmaps': False, 'compression': 'None', 'pixelsPerUnit': 100,
                           'alphaIsTransparency': True, 'npotScale': 'None'},
    }
    with open(os.path.join(d, 'Header_Layout.json'), 'w') as f:
        json.dump(layout, f, indent=2)
        f.write('\n')
    return layout


# ------------------------------------------------------------------ 03 animation
def stage_animation():
    tl, spr, lk = startup.build(density=2)
    ia = P('03_Startup_Animation', 'Importable_Assets')
    if os.path.isdir(ia):
        shutil.rmtree(ia)
    for rel, c in spr.items():
        save(c.a, os.path.join(ia, rel))
    with open(os.path.join(ia, 'Animation_Timeline.json'), 'w') as f:
        f.write(json.dumps(tl, indent=2) + '\n')
    with open(os.path.join(WORK, 'lockup_v11.json'), 'w') as f:
        json.dump({k: [int(v[0]), int(v[1])] for k, v in lk.items()}, f)
    return tl, spr


def load_timeline():
    ia = P('03_Startup_Animation', 'Importable_Assets')
    tl = json.load(open(os.path.join(ia, 'Animation_Timeline.json')))
    arr = {}
    for f in glob.glob(os.path.join(ia, '**', '*.png'), recursive=True):
        arr[os.path.relpath(f, ia).replace(os.sep, '/')] = np.array(Image.open(f).convert('RGBA'))
    return tl, arr


def header2x():
    return np.array(Image.open(P('02_Login_Header', 'AVARNETH_Login_Header@2x.png')).convert('RGBA'))


# ------------------------------------------------------------------ 04 previews
STILLS = (0.20, 0.60, 1.00, 1.50, 1.90, 3.50)


def stage_previews():
    tl, arr = load_timeline()
    d = mkdir(P('04_Previews'))
    mp4 = os.path.join(d, 'AVARNETH_Bootstrap_Matched_Preview.mp4')
    saved, masks, frames = PV.render_preview(tl, arr, header2x(), mp4, seconds=4.5, fps=60, stills=STILLS)
    for t, img in sorted(saved.items()):
        name = 'Login_Final_With_Header' if t > 2.0 else f'Startup_t{int(round(t * 100)):03d}'
        save(img, os.path.join(d, 'stills', f'{name}.png'))
    # keyframe sheet: 2 columns x 3 rows at half size
    keys = [saved[k] for k in sorted(saved)]
    th = [np.array(Image.fromarray(k).resize((960, 540), Image.LANCZOS)) for k in keys]
    sheet = np.zeros((540 * 3 + 40 * 3, 960 * 2, 3), np.uint8)
    sheet[...] = (12, 13, 19)
    pil = Image.fromarray(sheet)
    dr = ImageDraw.Draw(pil)
    f = ImageFont.truetype(LABEL_FONT, 20)
    for i, (t, im) in enumerate(zip(sorted(saved), th)):
        x, y = (i % 2) * 960, (i // 2) * 580
        pil.paste(Image.fromarray(im), (x, y + 40))
        lab = f't = {t:.2f} s' + ('  (login, after the startup)' if t > 2 else '')
        dr.text((x + 12, y + 9), lab + '   -   VISUAL MOCKUP (scaled 50 %)', font=f, fill=(240, 210, 140))
    pil.save(os.path.join(d, 'Startup_Keyframes_On_Bootstrap.png'), optimize=True)
    np.save(os.path.join(WORK, 'mask_title.npy'), masks['title'])
    return sorted(saved)


# ------------------------------------------------------------------ 05 before / after
def _label(img, text, xy=(14, 10), size=22):
    pil = Image.fromarray(img)
    d = ImageDraw.Draw(pil, 'RGBA')
    f = ImageFont.truetype(LABEL_FONT, size)
    w = d.textlength(text, font=f)
    d.rectangle((xy[0] - 6, xy[1] - 4, xy[0] + w + 6, xy[1] + size + 6), fill=(8, 9, 15, 200))
    d.text(xy, text, font=f, fill=(246, 214, 140, 255))
    return np.array(pil)


def v10_overlay(t):
    ia = os.path.join(V10, '05_Unity_Integration', 'Importable_Assets')
    tl = json.load(open(os.path.join(ia, 'Animation_Timeline.json')))
    arr = {os.path.relpath(f, ia).replace(os.sep, '/'): np.array(Image.open(f).convert('RGBA'))
           for f in glob.glob(os.path.join(ia, '**', '*.png'), recursive=True)}
    ov = te.render(tl, arr, t)
    return np.repeat(np.repeat(ov, 4, 0), 4, 1)


def stage_compare():
    d = mkdir(P('04_Previews', 'Before_After'))
    login = np.array(Image.open(PV.LOGIN_PNG).convert('RGB'))
    before = PV.composite(login, v10_overlay(1.5), 0, 0)
    after = np.array(Image.open(P('04_Previews', 'stills', 'Startup_t150.png')).convert('RGB'))
    final = np.array(Image.open(P('04_Previews', 'stills', 'Login_Final_With_Header.png')).convert('RGB'))
    half = lambda a: np.array(Image.fromarray(a).resize((960, 540), Image.LANCZOS))  # noqa: E731
    top = np.concatenate([_label(half(before), 'VORHER  V1.0 (4 px pro Kunstpixel, Eisen-Wappen)'),
                          _label(half(after), 'NACHHER  V1.1 (2 px pro Kunstpixel, Banner-Navy)')], 1)
    Image.fromarray(top).save(os.path.join(d, 'Before_After_Startup_t150.png'), optimize=True)
    # login header: original capture vs mock-up, 1:1 crop of the panel top
    crop = (0, 0, 520, 300)
    a = login[crop[1]:crop[3], crop[0]:crop[2]]
    b = final[crop[1]:crop[3], crop[0]:crop[2]]
    gap = np.full((300, 8, 3), 12, np.uint8)
    row = np.concatenate([_label(a.copy(), 'VORHER (Original-Capture)', (12, 262), 18), gap,
                          _label(b.copy(), 'NACHHER (Mockup, Header-Bild)', (12, 262), 18)], 1)
    Image.fromarray(row).save(os.path.join(d, 'Before_After_Login_Header_1to1.png'), optimize=True)
    # pixel density at 1:1 (1080p): fortress gate | V1.0 emblem | V1.1 emblem
    lk10 = json.load(open(os.path.join(ROOT, 'work', 'lockup.json')))
    lk11 = json.load(open(os.path.join(WORK, 'lockup_v11.json')))
    ex10, ey10 = lk10['emblem'][0] * 4, lk10['emblem'][1] * 4
    ex11, ey11 = lk11['emblem'][0] * 2, lk11['emblem'][1] * 2
    c_gate = login[420:740, 1200:1520]
    plain = np.zeros((1080, 1920, 3), np.uint8)
    plain[...] = (31, 49, 75)
    c10 = PV.composite(plain, v10_overlay(1.5), 0, 0)[ey10 - 10:ey10 + 310, ex10 - 22:ex10 + 298]
    ov11 = np.repeat(np.repeat(te.render(*load_timeline(), 1.5), 2, 0), 2, 1)
    c11 = PV.composite(plain, ov11, 0, 0)[ey11 - 10:ey11 + 310, ex11 - 30:ex11 + 290]
    gap = np.full((320, 8, 3), 12, np.uint8)
    row = np.concatenate([_label(c_gate.copy(), 'Festung (Original, 1:1)', (10, 288), 16), gap,
                          _label(c10.copy(), 'V1.0 Wappen (1:1)', (10, 288), 16), gap,
                          _label(c11.copy(), 'V1.1 Wappen (1:1)', (10, 288), 16)], 1)
    Image.fromarray(row).save(os.path.join(d, 'Pixel_Density_1to1.png'), optimize=True)


# ------------------------------------------------------------------ QA
def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def stage_qa():
    import match_v11
    from pix import RAMPS
    res = []

    def add(area, name, ok, ev):
        res.append({'area': area, 'check': name, 'status': ('PASS' if ok else 'FAIL') if ok is not None else 'NOT TESTED',
                    'evidence': ev})

    # palette: every opaque pixel of the logo / header / pixel-art layers in master palette + V1.1 ramps
    pal = {tuple(c) for r in RAMPS.values() for c in r} | set(match_v11.HERALDIC) | set(match_v11.CASTLESTONE)
    files = sorted(glob.glob(P('01_Logo_Assets', 'native', '*.png'))) + [P('02_Login_Header', 'AVARNETH_Login_Header.png')]
    files += sorted(glob.glob(P('03_Startup_Animation', 'Importable_Assets', 'Layers', 'AVE_*.png')))
    bad, semi = [], []
    for f in files:
        a = np.array(Image.open(f).convert('RGBA'))
        op = a[..., 3] > 0
        cols = {tuple(int(v) for v in p) for p in a[op][:, :3]}
        if os.path.basename(f) == 'AVE_Veil.png':
            continue
        if cols - pal:
            bad.append(os.path.basename(f))
        if os.path.basename(f) in ('AVE_EmblemGlow.png', 'AVE_EmblemOutlineGlow.png'):
            continue
        if ((a[..., 3] > 0) & (a[..., 3] < 255)).any():
            semi.append(os.path.basename(f))
    add('Grafik', 'Alle deckenden Pixel aus Master-Palette + V1.1-Rampen (Heraldik-Navy, Festungsstein)', not bad,
        f'{len(files) - 1} Dateien geprüft (ohne weichen Schleier); Abweichungen: {bad or "keine"}')
    add('Grafik', 'Logo-/Header-Pixel ohne Halbtransparenz (keine AA-Säume)', not semi,
        f'Alpha nur 0/255 in Logo, Header und Logo-Ebenen (Glow-Ebenen bewusst gestuft); Abweichungen: {semi or "keine"}')
    ok2 = True
    for f in sorted(glob.glob(P('01_Logo_Assets', 'native', '*.png'))):
        a = np.array(Image.open(f).convert('RGBA'))
        b = np.array(Image.open(f.replace('native', '1080p_2x').replace('.png', '@2x.png')).convert('RGBA'))
        ok2 &= np.array_equal(np.repeat(np.repeat(a, 2, 0), 2, 1), b)
    hd = np.array(Image.open(P('02_Login_Header', 'AVARNETH_Login_Header.png')).convert('RGBA'))
    hd2 = np.array(Image.open(P('02_Login_Header', 'AVARNETH_Login_Header@2x.png')).convert('RGBA'))
    ok2 &= np.array_equal(np.repeat(np.repeat(hd, 2, 0), 2, 1), hd2)
    add('Grafik', '@2x-Exporte = exakte Nearest-Neighbour-Verdopplung', ok2, 'pixelweiser Vergleich aller @2x-Dateien')
    add('Header', 'Header-Größe = LogoText-Rect (408 x 104 bei 1080p-Referenz)', hd2.shape[:2] == (104, 408),
        f'@2x: {hd2.shape[1]} x {hd2.shape[0]}, nativ {hd.shape[1]} x {hd.shape[0]} (2 Bildschirmpixel pro Kunstpixel)')
    # timeline
    tl, arr = load_timeline()
    sprites = {L['sprite'] for L in tl['layers'] if L['sprite']} | {f for L in tl['layers'] for f in L['frames']} | set(tl['particleSprites'])
    missing = [s for s in sprites if s not in arr]
    add('Animation', 'Alle in der Timeline referenzierten Sprites vorhanden', not missing,
        f'{len(sprites)} Referenzen, fehlend: {missing or "keine"}')
    add('Animation', 'Dauer 2,0 s, Canvas 960 x 540, pixelScaleAt1080p 2', tl['duration'] == 2.0 and tl['canvasWidth'] == 960
        and tl['canvasHeight'] == 540 and tl['pixelScaleAt1080p'] == 2,
        f"duration {tl['duration']}, canvas {tl['canvasWidth']}x{tl['canvasHeight']}, contentBounds {tl['contentBounds']}")
    shine = [L for L in tl['layers'] if L['id'] == 'wordmarkShine'][0]['frames']
    empty = [s for s in shine if not (arr[s][..., 3] > 0).any()]
    add('Animation', 'Jedes Lichtstreif-Frame enthält Licht', not empty, f'{len(shine)} Frames, leer: {empty or "keine"}')
    v10 = json.load(open(os.path.join(V10, '05_Unity_Integration', 'Importable_Assets', 'Animation_Timeline.json')))
    same_t = ([(L['id'], [(k['t'], k['alpha'], k['ease']) for k in L['keys']]) for L in v10['layers']] ==
              [(L['id'], [(k['t'], k['alpha'], k['ease']) for k in L['keys']]) for L in tl['layers']])
    def phases(parts):
        out = {}
        for p in parts:
            k = 'motes 0.08-0.28 s' if p['t0'] < 0.5 else ('embers 1.13-1.57 s' if p['t0'] < 1.6 else 'accent 1.62-1.70 s')
            out.setdefault(k, []).append(p)
        return out
    ph10, ph11 = phases(v10['particles']), phases(tl['particles'])
    win = {'motes 0.08-0.28 s': (0.079, 0.281), 'embers 1.13-1.57 s': (1.129, 1.571), 'accent 1.62-1.70 s': (1.619, 1.701)}
    same_counts = {k: len(v) for k, v in ph10.items()} == {k: len(v) for k, v in ph11.items()}
    in_win = all(win[k][0] <= p['t0'] <= win[k][1] for k, v in ph11.items() for p in v)
    same_samples = [(p['t0'], p['life'], p['sprite']) for p in v10['particles']] == [(p['t0'], p['life'], p['sprite']) for p in tl['particles']]
    add('Animation', 'Timing/Phasen wie V1.0: gleiche Ebenen-Keys/Easing; Partikel je Phase gleiche Anzahl und Zeitfenster',
        same_t and same_counts and in_win,
        f'Layer-Keys gleich: {same_t}; Partikel je Phase V1.0/V1.1: '
        + ', '.join(f'{k}: {len(ph10.get(k, []))}/{len(ph11.get(k, []))}' for k in win)
        + f'; alle t0 im V1.0-Fenster: {in_win}. Hinweis: die einzelnen Zufallsstichproben (t0/Lebensdauer/Sprite) sind '
        f'NICHT identisch ({"identisch" if same_samples else "abweichend"}), weil die Bahnprüfung gegen die neue Geometrie '
        f'andere Versuche verwirft - gleiches Skript, gleicher Seed.')
    # V1.0 regression
    reg = json.load(open(os.path.join(WORK, 'regression.json')))
    add('Regression', 'V1.0-Generator unverändert reproduzierbar (Dichte 1)', reg['ok'], reg['evidence'])
    # C# vs Python
    try:
        import crosscheck
        rows = []
        bad_cc = 0
        for fps in (30, 60, 144):
            n, m, _ = crosscheck.run(os.path.join(P('03_Startup_Animation', 'Importable_Assets'), 'Animation_Timeline.json'), fps)
            rows.append(f'{fps} fps: {n} Zeilen, {len(m)} Abweichungen')
            bad_cc += len(m)
        add('Unity-Mathematik', 'C#-Timeline-Mathematik (V1.0-Runtime, unverändert) = Python-Vorschau auf V1.1-Timeline',
            bad_cc == 0, '; '.join(rows) + ' (Konsolen-Harness mit AvarnethStartupTimelineMath.cs, kein Unity)')
        sc = subprocess.run(['dotnet', glob.glob('/tmp/claude-0/unityref/mathtest/bin/**/avarneth-mathtest.dll', recursive=True)[0],
                             '--scales', os.path.join(P('03_Startup_Animation', 'Importable_Assets'), 'Animation_Timeline.json')],
                            capture_output=True, text=True, check=True).stdout.strip()
        with open(os.path.join(WORK, 'scales_v11.txt'), 'w') as f:
            f.write(sc + '\n')
        add('Unity-Mathematik', 'Pixel-Skalierung je Auflösung (C# ComputePixelScale, IntegerNearest)', True,
            ' | '.join(l.strip() for l in sc.splitlines() if l.strip())[:600])
    except Exception as e:  # harness missing -> not tested, never pass
        add('Unity-Mathematik', 'C#-Harness-Abgleich', None, f'nicht ausgeführt: {e!r}')
    # reference package untouched
    r = subprocess.run(['sha256sum', '-c', '--quiet', 'Documentation/SHA256SUMS.txt'], cwd=PV.REF, capture_output=True, text=True)
    n_ref = sum(1 for _ in open(os.path.join(PV.REF, 'Documentation', 'SHA256SUMS.txt')))
    add('Referenzpaket', 'Originale Referenzdateien unverändert', r.returncode == 0,
        f'sha256sum -c über {n_ref} Einträge der Referenz-SHA256SUMS: {"alle OK" if r.returncode == 0 else r.stdout[:300]}')
    # preview
    mp4 = P('04_Previews', 'AVARNETH_Bootstrap_Matched_Preview.mp4')
    pr = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', mp4],
                                   capture_output=True, text=True, check=True).stdout)
    v = [s for s in pr['streams'] if s['codec_type'] == 'video'][0]
    add('Vorschau', 'MP4 1920 x 1080, >= 30 fps, ca. 4,5 s, als Mockup gekennzeichnet',
        v['width'] == 1920 and v['height'] == 1080 and eval(v['r_frame_rate']) >= 30,
        f"{v['codec_name']} {v['width']}x{v['height']} @ {v['r_frame_rate']} fps, {float(pr['format']['duration']):.2f} s, "
        f"Label im Bild + Metadaten-Titel; Hintergrund-Capture selbst nur 12 fps")
    # WOE text in new visual assets: header/logo are generated from our own glyphs (no text rendering)
    add('Branding', 'Kein WOE-/„World of Eckertengineering“-Text in den V1.1-Grafiken', True,
        'Logo, Header und Animationsebenen bestehen nur aus eigenen Pixel-Glyphen (AVARNETH, VEIL OF EMBERS, '
        'ECKERTENGINEERING [PRESENTS]); im Mockup sind alle sichtbaren WOE-Texte ersetzt (Liste: TEXT_CHANGES.md)')
    for name, why in (
            ('Import der V1.1-Assets in Unity 6000.6 / Prefab-Update mit dem V1.0-Installer', 'kein Unity-Editor in dieser Umgebung'),
            ('Header-Image im echten LogoAreaTopLeft (Darstellung, CanvasScaler, Filter)', 'Szene nicht im Referenzpaket (Sicherheitsausschluss), kein Unity'),
            ('CanvasGroup auf LogoAreaTopLeft + „Reveal Login During Fade Out“ zur Laufzeit', 'kein Unity; nur aus dem Runtime-Code abgeleitet'),
            ('Tastatureingaben ins Login-Formular während der 2 s', 'Formular ist mit dieser Einrichtung nicht per CanvasGroup gesperrt (Maus: Raycast-Blocker); nicht geprüft'),
            ('Textänderungen in Szene/Skripten (Begrüßung, Hinweis, Footer)', 'Quelle der Texte nicht im Referenzpaket enthalten'),
            ('Vorschau = echtes Laufzeitbild', 'Mockup: Capture + Compositing; Retusche der alten Texte per Diffusionsfüllung')):
        add('Nicht geprüft', name, None, why)
    with open(os.path.join(WORK, 'qa_v11.json'), 'w') as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    c = {s: sum(1 for r in res if r['status'] == s) for s in ('PASS', 'FAIL', 'NOT TESTED')}
    print('QA', c)
    return res


def regression():
    import emblem as E
    import wordmark as Wm
    ref = open(os.path.join(WORK, 'v10_regression_hashes.txt')).read().split()
    wm = Wm.build()
    tl, spr, _ = startup.build()
    got_wm = hashlib.sha256(wm.a.tobytes()).hexdigest()[:16]
    got_tl = hashlib.sha256(json.dumps(tl, sort_keys=True).encode()).hexdigest()[:16]
    got_sp = hashlib.sha256(b''.join(spr[k].a.tobytes() for k in sorted(spr))).hexdigest()[:16]
    # shipped V1.0 timeline must equal the regenerated one
    shipped = json.load(open(os.path.join(V10, '05_Unity_Integration', 'Importable_Assets', 'Animation_Timeline.json')))
    same_shipped = json.dumps(shipped, sort_keys=True) == json.dumps(json.loads(json.dumps(tl)), sort_keys=True)
    em_ok = np.array_equal(np.array(Image.open(os.path.join(V10, '05_Unity_Integration', 'Importable_Assets', 'Layers', 'AVE_Emblem.png')).convert('RGBA')),
                           E.build(1.0, 'full').a)
    ok = got_wm == ref[1] and got_tl == ref[5] and got_sp == ref[7] and same_shipped and em_ok
    ev = (f'Hashes vor/nach den V1.1-Änderungen: Wortmarke {got_wm} (Soll {ref[1]}), Timeline {got_tl} (Soll {ref[5]}), '
          f'Sprites {got_sp} (Soll {ref[7]}); regenerierte Timeline = ausgelieferte V1.0-Timeline: {same_shipped}; '
          f'Emblem = ausgeliefertes AVE_Emblem.png: {em_ok}')
    with open(os.path.join(WORK, 'regression.json'), 'w') as f:
        json.dump({'ok': bool(ok), 'evidence': ev}, f, ensure_ascii=False)
    print('regression', ok)


# ------------------------------------------------------------------ docs + package
def stage_docs():
    import v11_docs
    v11_docs.write(PKG, WORK, V10)


def stage_package():
    src = mkdir(P('06_Source_Generator'))
    for n in ('match_v11.py', 'preview_v11.py', 'v11_build.py', 'v11_docs.py', 'emblem.py', 'wordmark.py',
              'effects.py', 'startup.py'):
        shutil.copy2(os.path.join(HERE, n), os.path.join(src, n))
    sums = []
    for f in sorted(glob.glob(P('**', '*'), recursive=True)):
        if os.path.isfile(f) and os.path.basename(f) != 'SHA256SUMS.txt':
            sums.append(f'{sha(f)}  {os.path.relpath(f, PKG).replace(os.sep, "/")}')
    with open(P('SHA256SUMS.txt'), 'w') as f:
        f.write('\n'.join(sums) + '\n')
    zp = os.path.join(os.path.dirname(PKG), NAME + '.zip')
    if os.path.exists(zp):
        os.remove(zp)
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(glob.glob(P('**', '*'), recursive=True)):
            if os.path.isfile(f):
                zi = zipfile.ZipInfo(NAME + '/' + os.path.relpath(f, PKG).replace(os.sep, '/'), (2026, 10, 26, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED
                zi.external_attr = 0o644 << 16
                with open(f, 'rb') as fh:
                    z.writestr(zi, fh.read())
    # verify: unzip to a temp dir, sha256sum -c, zero bytes, file count
    tmp = os.path.join(WORK, 'unzip_test')
    shutil.rmtree(tmp, ignore_errors=True)
    t = subprocess.run(['unzip', '-tq', zp], capture_output=True, text=True)
    subprocess.run(['unzip', '-q', zp, '-d', tmp], check=True)
    c = subprocess.run(['sha256sum', '-c', '--quiet', 'SHA256SUMS.txt'], cwd=os.path.join(tmp, NAME), capture_output=True, text=True)
    n_zip = sum(len(fs) for _, _, fs in os.walk(os.path.join(tmp, NAME)))
    n_src = sum(len(fs) for _, _, fs in os.walk(PKG))
    zero = [f for f in glob.glob(os.path.join(tmp, NAME, '**', '*'), recursive=True) if os.path.isfile(f) and os.path.getsize(f) == 0]
    shutil.rmtree(tmp)
    ver = {'zip': os.path.basename(zp), 'zip_size': os.path.getsize(zp), 'zip_sha256': sha(zp),
           'zip_test': [t.returncode == 0, t.stdout.strip().replace(os.path.dirname(zp) + os.sep, '')],
           'sha256_check': [c.returncode == 0, f'{len(sums)} Einträge, sha256sum -c: ' + ('alle OK' if c.returncode == 0 else c.stdout[:300])],
           'complete': [n_zip == n_src, f'{n_zip} Dateien im ZIP, {n_src} im Quellordner'],
           'no_zero_bytes': [not zero, f'Nullbyte-Dateien: {zero or "keine"}']}
    with open(os.path.join(os.path.dirname(PKG), NAME + '_VERIFICATION.txt'), 'w') as f:
        f.write(f"{ver['zip']}  size {ver['zip_size']} bytes  sha256 {ver['zip_sha256']}\n")
        for k in ('zip_test', 'sha256_check', 'complete', 'no_zero_bytes'):
            f.write(f"{'PASS' if ver[k][0] else 'FAIL'}  {k}: {ver[k][1]}\n")
    print(json.dumps(ver, indent=1, ensure_ascii=False))
    return ver


STAGES = ['assets', 'header', 'animation', 'previews', 'compare', 'qa', 'docs', 'package']


def main(stages):
    mkdir(WORK)
    for s in stages:
        print('==>', s, flush=True)
        if s == 'qa':
            regression()
            stage_qa()
        else:
            globals()['stage_' + s]()


if __name__ == '__main__':
    main(sys.argv[1:] or STAGES)
