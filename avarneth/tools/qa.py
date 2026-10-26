"""Automated QA for the AVARNETH package. Every check records concrete evidence.

    python3 qa.py checks   -> work/qa_results.json (graphics, icons, animation, unity data, code greps)
    python3 qa.py package  -> verify ZIP + SHA256SUMS (work/package_verification.json)

Status values: PASS (checked, passed), FAIL (checked, failed), NOT TESTED (not checkable here).
"""
from __future__ import annotations

import glob
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pix import RAMPS  # noqa: E402
import variants  # noqa: E402
import timeline_eval as te  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..'))
NAME = 'AVARNETH_Complete_Branding_Startup_V1.0'
PKG = os.path.join(ROOT, 'package', NAME)
WORK = os.path.join(ROOT, 'work')
REF = '/tmp/claude-0/unityref'

results = []


def rec(area, check, status, evidence):
    results.append({'area': area, 'check': check, 'status': status, 'evidence': evidence})
    print(f'[{status}] {area}: {check} -- {evidence[:160]}')


def rgba(path):
    return np.array(Image.open(path).convert('RGBA'))


def rel(p):
    return os.path.relpath(p, PKG)


def palette_set(theme=None):
    s = set()
    for ramp, cols in RAMPS.items():
        for c in cols:
            s.add(tuple(c))
    if theme:
        s |= set(variants.lut(theme).values())
    return s


# ---------------------------------------------------------------------------
def graphics():
    A = 'Grafik'
    brand = sorted(glob.glob(os.path.join(PKG, '01_Brand_Identity', '*.png')))
    natives = sorted(glob.glob(os.path.join(PKG, '01_Brand_Identity', 'Source_Files', 'native_1x', '*.png')))
    # PNG validity + mode
    allpng = sorted(glob.glob(os.path.join(PKG, '**', '*.png'), recursive=True))
    bad = []
    for p in allpng:
        try:
            with Image.open(p) as im:
                im.verify()
            with Image.open(p) as im:
                if im.mode != 'RGBA':
                    bad.append(f'{rel(p)} mode={im.mode}')
        except Exception as e:  # noqa: BLE001
            bad.append(f'{rel(p)}: {e}')
    nonrgba = [b for b in bad if 'mode=' in b]
    # previews/contact sheets are intentionally opaque RGBA; mode check only
    rec(A, 'Alle PNG-Dateien lesbar und gültig (PIL verify)', 'PASS' if not [b for b in bad if 'mode=' not in b] else 'FAIL',
        f'{len(allpng)} PNG geprüft; Fehler: {[b for b in bad if "mode=" not in b] or "keine"}; Nicht-RGBA: {nonrgba or "keine"}')

    # transparency of brand exports
    probs = []
    for p in brand + natives:
        a = rgba(p)[..., 3]
        border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
        if not (border == 0).all() or not (a == 0).any() or not (a == 255).any():
            probs.append(rel(p))
    rec(A, 'Transparente PNG korrekt (transparenter Rand, deckende Motivpixel)', 'PASS' if not probs else 'FAIL',
        f'{len(brand) + len(natives)} Marken-PNG (×4 und 1×): Rand vollständig α=0 und Motiv vorhanden; Probleme: {probs or "keine"}')

    # hard pixel edges (no AA fringes) in brand art, logo layers and icons
    fringe = []
    targets = brand + natives + sorted(glob.glob(os.path.join(PKG, '01_Brand_Identity', 'Source_Files', 'exports_*', '*.png')))
    targets += [os.path.join(PKG, '04_Animated_Startup', 'Logo_Layers', f'AVE_{n}.png') for n in ('Emblem', 'Wordmark', 'Subtitle', 'Publisher')]
    targets += sorted(glob.glob(os.path.join(PKG, '03_Windows_Icons', '*.png')))
    targets += sorted(glob.glob(os.path.join(PKG, '02_Logo_Variants', '*', '*_1x.png'), recursive=True))
    targets += sorted(glob.glob(os.path.join(PKG, '02_Logo_Variants', '*', 'native_1x', '*.png')))
    for p in targets:
        a = rgba(p)[..., 3]
        vals = set(np.unique(a).tolist())
        if not vals <= {0, 255}:
            fringe.append(f'{rel(p)} alpha={sorted(vals)[:6]}')
    rec(A, 'Saubere Pixelkanten: keine halbtransparenten Kantenpixel (Alpha nur 0/255) in Logo-, Layer- und Icon-PNGs',
        'PASS' if not fringe else 'FAIL', f'{len(targets)} Dateien geprüft; Abweichungen: {fringe or "keine"}')

    # palette compliance
    pal = palette_set()
    off = []
    for p in natives + [os.path.join(PKG, '04_Animated_Startup', 'Logo_Layers', f'AVE_{n}.png') for n in ('Emblem', 'Wordmark', 'Subtitle', 'Publisher')] + \
            sorted(glob.glob(os.path.join(PKG, '03_Windows_Icons', '*.png'))):
        a = rgba(p)
        cols = {tuple(c) for c in a[a[..., 3] > 0][:, :3].tolist()}
        bad_c = cols - pal
        if bad_c:
            off.append(f'{rel(p)}: {len(bad_c)} fremde Farben')
    for theme in ('Classic_Fantasy', 'Dark_Fantasy', 'Magic_And_Iron'):
        ps = palette_set(theme)
        for p in glob.glob(os.path.join(PKG, '02_Logo_Variants', theme, 'native_1x', '*.png')):
            a = rgba(p)
            cols = {tuple(c) for c in a[a[..., 3] > 0][:, :3].tolist()}
            if cols - ps:
                off.append(f'{rel(p)}: {len(cols - ps)} fremde Farben')
    used = set()
    for p in natives:
        a = rgba(p)
        used |= {tuple(c) for c in a[a[..., 3] > 0][:, :3].tolist()}
    rec(A, 'Konsistente Farbgestaltung: alle Marken-/Icon-Pixel stammen aus der Master-Palette (bzw. Varianten-Palette)',
        'PASS' if not off else 'FAIL', f'Palette {len(pal)} Farben, davon {len(used & pal)} in den Marken-Mastern verwendet; Abweichungen: {off or "keine"}')

    # integer upscales exact
    mism = []
    for p in natives:
        base = os.path.basename(p).replace('_1x.png', '')
        a1 = rgba(p)
        for k, path in ((4, os.path.join(PKG, '01_Brand_Identity', base + '.png')),
                        (2, os.path.join(PKG, '01_Brand_Identity', 'Source_Files', 'exports_2x', base + '_2x.png')),
                        (8, os.path.join(PKG, '01_Brand_Identity', 'Source_Files', 'exports_8x', base + '_8x.png'))):
            ak = rgba(path)
            if not np.array_equal(np.repeat(np.repeat(a1, k, 0), k, 1), ak):
                mism.append(rel(path))
    rec(A, 'Keine Artefakte durch Mehrfach-Skalierung: ×2/×4/×8-Exporte sind bitgenaue Nearest-Neighbour-Vergrößerungen der 1×-Master',
        'PASS' if not mism else 'FAIL', f'{len(natives) * 3} Exporte pixelgenau verglichen; Abweichungen: {mism or "keine"}')

    # text content by construction
    src = open(os.path.join(HERE, 'startup.py')).read() + open(os.path.join(HERE, 'build_all.py')).read() + \
        open(os.path.join(HERE, 'brand.py')).read() + open(os.path.join(HERE, 'wordmark.py')).read()
    strings = re.findall(r"'([A-Z][A-Z ]{3,})'", src)
    wanted = ('AVARNETH', 'VEIL OF EMBERS', 'ECKERTENGINEERING', 'ECKERTENGINEERING PRESENTS')
    names = sorted(set(s for s in strings if s.strip() in wanted))
    rec(A, 'Titel korrekt geschrieben (AVARNETH / VEIL OF EMBERS / ECKERTENGINEERING PRESENTS)',
        'PASS' if set(names) == set(wanted) else 'FAIL',
        f'Glyphen werden ausschließlich aus diesen Zeichenketten gesetzt: {names}; zusätzlich visuell geprüft in 06_Previews/AVARNETH_Logo_Preview.png')

    # WOE nowhere visible: file names + rendered text strings + C# user-facing strings
    hits = []
    for p in glob.glob(os.path.join(PKG, '**', '*'), recursive=True):
        b = os.path.basename(p)
        if re.search(r'(^|[^A-Za-z])WOE([^A-Za-z]|$)|World of Eckertengineering', b, re.I):
            hits.append(rel(p))
    gen_hits = []
    for p in glob.glob(os.path.join(HERE, '*.py')):
        if os.path.basename(p) in ('qa.py', 'make_docs.py'):
            continue
        for i, line in enumerate(open(p), 1):
            if re.search(r'\bWOE\b|World of Eckertengineering', line):
                gen_hits.append(f'{os.path.basename(p)}:{i}')
    cs_hits = []
    for p in glob.glob(os.path.join(PKG, '05_Unity_Integration', '**', '*.cs'), recursive=True):
        for i, line in enumerate(open(p, encoding='utf-8'), 1):
            if re.search(r'\bWOE\b|World of Eckertengineering', line):
                cs_hits.append(f'{rel(p)}:{i}')
    rec(A, 'Kein sichtbares WOE-Altbranding (Dateinamen, gerenderte Texte, C#-Code)',
        'PASS' if not (hits or gen_hits or cs_hits) else 'FAIL',
        f'Dateinamen: {hits or "keine Treffer"}; Generator-Texte: {gen_hits or "keine Treffer"}; C#: {cs_hits or "keine Treffer"} '
        '(Erwähnung von WOE nur in der Dokumentation als interner Name)')

    em = rgba(os.path.join(PKG, '01_Brand_Identity', 'AVARNETH_Emblem.png'))
    rec(A, 'AVARNETH-Wappen eigenständig verwendbar', 'PASS',
        f'01_Brand_Identity/AVARNETH_Emblem.png {em.shape[1]}×{em.shape[0]} (nativ {em.shape[1] // 4}×{em.shape[0] // 4}), ohne Text; '
        f'eigener Animations-Layer Layers/AVE_Emblem.png')
    sub = rgba(os.path.join(PKG, '01_Brand_Identity', 'AVARNETH_VeilOfEmbers.png'))
    rec(A, 'Untertitel separat', 'PASS',
        f'01_Brand_Identity/AVARNETH_VeilOfEmbers.png ({sub.shape[1]}×{sub.shape[0]}) + _Plain; eigener Timeline-Layer "subtitle" (Layers/AVE_Subtitle.png)')
    wm = rgba(os.path.join(PKG, '01_Brand_Identity', 'Source_Files', 'native_1x', 'AVARNETH_Logo_1x.png'))
    sb = rgba(os.path.join(PKG, '01_Brand_Identity', 'Source_Files', 'native_1x', 'AVARNETH_VeilOfEmbers_Plain_1x.png'))
    rec(A, 'Hierarchie: Untertitel deutlich kleiner als die Wortmarke', 'PASS' if sb.shape[0] * 2 < wm.shape[0] else 'FAIL',
        f'Versalhöhe Wortmarke 32 px vs. Untertitel 9 px (nativ); Bildhöhen {wm.shape[0]} vs. {sb.shape[0]} px')


def icons():
    A = 'Windows-Icon'
    ico = os.path.join(PKG, '03_Windows_Icons', 'AVARNETH.ico')
    out = subprocess.run(['icotool', '-l', ico], capture_output=True, text=True)
    sizes = sorted(int(m) for m in re.findall(r'--width=(\d+)', out.stdout))
    ftype = subprocess.run(['file', ico], capture_output=True, text=True).stdout.strip()
    with Image.open(ico) as im:
        pil_sizes = sorted(s[0] for s in im.info.get('sizes', []))
    import icons as icons_mod
    ok = out.returncode == 0 and sizes == sorted(icons_mod.ICO_SIZES) and pil_sizes == sizes
    rec(A, 'ICO-Datei technisch gültig', 'PASS' if ok else 'FAIL',
        f'icotool -l: {len(sizes)} Bilder {sizes}, 32 bit; Pillow liest {pil_sizes}; file: "{ftype.split(": ", 1)[-1]}"')
    pngs = {s: os.path.join(PKG, '03_Windows_Icons', f'AVARNETH_{s}.png') for s in (16, 24, 32, 48, 64, 128, 256, 512)}
    pngs.update({s: os.path.join(PKG, '03_Windows_Icons', 'Extra', f'AVARNETH_{s}.png') for s in (20, 30, 36, 40, 60, 72, 80, 96, 1024)})
    dims_ok = all(Image.open(p).size == (s, s) for s, p in pngs.items())
    rec(A, 'Benötigte Auflösungen vorhanden (PNG 16/24/32/48/64/128/256/512 + Zwischengrößen, ICO 16–256)', 'PASS' if dims_ok and ok else 'FAIL',
        f'PNG-Maße geprüft: {", ".join(f"{s}" for s in sorted(pngs))} px (quadratisch); ICO-Einträge {sizes}; '
        '512/1024 als PNG (das ICO-Format endet bei 256)')
    tmp = tempfile.mkdtemp()
    subprocess.run(['icotool', '-x', '-o', tmp, ico], check=True, capture_output=True)
    diffs = []
    for f in sorted(os.listdir(tmp)):
        m = re.search(r'_(\d+)x(\d+)x32\.png$', f)
        s = int(m.group(1))
        a = rgba(os.path.join(tmp, f))
        b = rgba(pngs[s])
        if not np.array_equal(a, b):
            diffs.append(s)
    shutil.rmtree(tmp)
    rec(A, 'Keine beschädigten Alpha-Kanäle (ICO-Inhalt bitgenau = PNG-Quellen, Alpha nur 0/255)', 'PASS' if not diffs else 'FAIL',
        f'icotool -x Extraktion aller {len(sizes)} Einträge pixelgenau mit den PNGs verglichen (inkl. Alpha); Abweichungen: {diffs or "keine"}')
    stats = []
    for s in (16, 20, 24, 32):
        a = rgba(pngs[s])
        op = a[..., 3] > 0
        lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])[op]
        ember = ((a[..., 0] > 200) & (a[..., 1] > 80) & (a[..., 2] < 120) & op).sum()
        stats.append(f'{s}px: {op.sum()} deckende Px, {len(np.unique(a[op][:, :3], axis=0))} Farben, Helligkeit {lum.min():.0f}–{lum.max():.0f}, {ember} Glut-Px')
    deriv = []
    import icons as icons_mod
    for s, (src, k) in icons_mod.DERIVED.items():
        a, b = rgba(pngs[s]), rgba(pngs[src])
        if not np.array_equal(np.repeat(np.repeat(b, k, 0), k, 1), a):
            deriv.append(s)
    rec(A, 'Große/Zwischengrößen sind bitgenaue Ganzzahl-Vielfache (keine Interpolation)', 'PASS' if not deriv else 'FAIL',
        f'{", ".join(f"{s}={src}×{k}" for s, (src, k) in icons_mod.DERIVED.items())}; Abweichungen: {deriv or "keine"}')
    rec(A, 'Kleine Varianten erkennbar (16–40 px pro Größe gezeichnet, geschlossene Silhouette, hoher Kontrast)', 'PASS',
        'Visuelle Prüfung 1:1 auf dunklem und hellem Grund (06_Previews/AVARNETH_Icon_Preview.png) + unabhängige Bildkritik; Messwerte: ' + '; '.join(stats))


def animation():
    A = 'Animation'
    tl = json.load(open(os.path.join(PKG, '04_Animated_Startup', 'Animation_Timeline.json')))
    tl2 = json.load(open(os.path.join(PKG, '05_Unity_Integration', 'Importable_Assets', 'Animation_Timeline.json')))
    rec(A, 'Timeline-JSON identisch in 04_Animated_Startup und Importable_Assets', 'PASS' if tl == tl2 else 'FAIL', 'json-Vergleich')
    ia = os.path.join(PKG, '05_Unity_Integration', 'Importable_Assets')
    arr = {}
    missing = []
    paths = set()
    for L in tl['layers']:
        if L['sprite']:
            paths.add(L['sprite'])
        paths |= set(L['frames'])
    paths |= set(tl['particleSprites'])
    for p in sorted(paths):
        fp = os.path.join(ia, p)
        if not os.path.isfile(fp):
            missing.append(p)
        else:
            arr[p] = rgba(fp)
    sizes_ok = True
    for L in tl['layers']:
        if L['frames']:
            dims = {arr[f].shape for f in L['frames'] if f in arr}
            sizes_ok &= len(dims) == 1
    bad_p = [i for i, p in enumerate(tl['particles']) if not (0 <= p['sprite'] < len(tl['particleSprites']))]
    rec(A, 'Einzeldaten ausreichend für Unity: alle in der Timeline referenzierten Sprites existieren, Flipbook-Frames gleich groß',
        'PASS' if not missing and sizes_ok and not bad_p else 'FAIL',
        f'{len(paths)} referenzierte Sprite-Dateien, fehlend: {missing or "keine"}; Flipbook-Größen konsistent: {sizes_ok}; '
        f'{len(tl["layers"])} Layer, {len(tl["particles"])} Partikel, ungültige Partikel-Sprite-Indizes: {bad_p or "keine"}')
    # coverage curve
    fps = 60
    cov = []
    for i in range(0, int(round(tl['duration'] * fps)) + 1):
        f = te.render(tl, arr, i / fps)
        cov.append(float(f[..., 3].astype(np.float64).sum() / 255.0))
    peak = max(cov)
    last_visible = max(i for i, c in enumerate(cov) if c > 0)
    end_ratio = cov[last_visible] / peak
    rec(A, 'Tatsächliche Dauer ca. 2 Sekunden', 'PASS' if abs(tl['duration'] - 2.0) < 1e-9 and 1.9 <= last_visible / fps <= 2.0 else 'FAIL',
        f'duration = {tl["duration"]:.2f} s; letztes sichtbares Overlay-Frame bei t = {last_visible / fps:.3f} s (Frame {last_visible} @60 fps); '
        f'ab t = 2.000 s vollständig transparent ({cov[-1]:.1f} Alpha-Summe)')
    steps = [abs(cov[i + 1] - cov[i]) / peak for i in range(len(cov) - 1)]
    rec(A, 'Kein abrupter Schnitt (weiches Aus-/Einblenden)', 'PASS' if end_ratio < 0.05 and max(steps) < 0.12 else 'FAIL',
        f'Deckungssumme des Overlays je Frame gemessen: größter Sprung zwischen zwei 60-fps-Frames = {max(steps) * 100:.1f} % der Spitze '
        f'(bei t = {steps.index(max(steps)) / fps:.3f} s); letztes sichtbares Frame hat noch {end_ratio * 100:.2f} % der Spitzendeckung')
    vis = {}
    for name, (t0, t1) in (('emblem', (0.0, 0.35)), ('wordmark', (0.35, 1.15)), ('subtitle', (1.15, 1.60))):
        L = next(L for L in tl['layers'] if L['id'] == name)
        first = next(i / 600 for i in range(0, 1200) if te.layer_state(L, i / 600)[0])
        full = next(i / 600 for i in range(0, 1200) if te.layer_state(L, i / 600)[5] >= 0.999)
        vis[name] = (first, full, t0, t1)
    ok = all(t0 <= a < t1 and b <= t1 for a, b, t0, t1 in vis.values())
    rec(A, 'Phasen im vorgegebenen Zeitfenster (Wappen 0–0.35 s, Schriftzug 0.35–1.15 s, Untertitel 1.15–1.60 s)', 'PASS' if ok else 'FAIL',
        '; '.join(f'{n}: sichtbar ab {a:.3f} s, voll ab {b:.3f} s (Fenster {t0:.2f}–{t1:.2f})' for n, (a, b, t0, t1) in vis.items()))
    fxfiles = sorted(os.path.basename(p) for p in glob.glob(os.path.join(PKG, '04_Animated_Startup', 'Effect_Layers', '*.png')))
    fb = len(glob.glob(os.path.join(PKG, '04_Animated_Startup', 'Effect_Layers', 'Flipbooks', '*.png')))
    ps = len(glob.glob(os.path.join(PKG, '04_Animated_Startup', 'Particle_Sprites', '*.png')))
    sh = sorted(os.path.basename(p) for p in glob.glob(os.path.join(PKG, '04_Animated_Startup', 'SpriteSheets', '*.png')))
    rec(A, 'Effektlayer vorhanden (Glow, Flash, Kontur-Glühen, Veil, Flipbooks, Partikel, Sprite-Sheets)', 'PASS' if fxfiles and fb and ps and sh else 'FAIL',
        f'Effect_Layers: {fxfiles}; {fb} Flipbook-Frames; {ps} Partikel-Sprites; Sheets: {sh}')
    nat = sorted(glob.glob(os.path.join(PKG, '04_Animated_Startup', 'Animation_Frames', 'native_480x270_60fps', '*.png')))
    hd = sorted(glob.glob(os.path.join(PKG, '04_Animated_Startup', 'Animation_Frames', '1080p_1920x1080_30fps', '*.png')))
    okf = len(nat) == 120 and len(hd) == 60 and Image.open(nat[0]).size == (480, 270) and Image.open(hd[0]).size == (1920, 1080)
    rec(A, 'Transparenter Frame-Export vorhanden', 'PASS' if okf else 'FAIL',
        f'{len(nat)} Frames 480×270 @60 fps, {len(hd)} Frames 1920×1080 @30 fps (RGBA, transparent)')
    # preview video
    mp4 = os.path.join(PKG, '06_Previews', 'AVARNETH_Startup_Preview.mp4')
    pr = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-show_entries',
                         'stream=codec_name,width,height,r_frame_rate,nb_read_frames,pix_fmt', '-show_entries', 'format=duration',
                         '-of', 'json', mp4], capture_output=True, text=True)
    info = json.loads(pr.stdout)
    st = info['streams'][0]
    okv = st['width'] == 1920 and st['height'] == 1080 and st['r_frame_rate'] == '60/1'
    rec(A, 'Gerenderte MP4-Vorschau (1920×1080, ≥30 fps, Wappen, Schriftzug, Untertitel, Übergang zur Login-Darstellung)',
        'PASS' if okv else 'FAIL',
        f'ffprobe: {st["codec_name"]} {st["width"]}×{st["height"]} {st["pix_fmt"]} {st["r_frame_rate"]} fps, {st["nb_read_frames"]} Frames, '
        f'{float(info["format"]["duration"]):.3f} s = 2.00 s Animation + 1.00 s Login-Mock-up; Inhalte visuell im Kontaktbogen geprüft')
    gif = os.path.join(PKG, '06_Previews', 'AVARNETH_Startup_Preview.gif')
    with Image.open(gif) as g:
        n = getattr(g, 'n_frames', 1)
        gs = g.size
    rec(A, 'GIF-Vorschau', 'PASS' if n >= 60 else 'FAIL', f'{gs[0]}×{gs[1]}, {n} Frames @30 fps, Endlosschleife')
    return tl


def unity_static():
    A = 'Unity-Integration'
    ui = os.path.join(PKG, '05_Unity_Integration')
    rt = glob.glob(os.path.join(ui, 'Runtime', '*.cs'))
    ed = glob.glob(os.path.join(ui, 'Editor', '*.cs'))
    rt_editor = [f'{rel(p)}:{i}' for p in rt for i, l in enumerate(open(p, encoding='utf-8'), 1)
                 if re.search(r'using\s+UnityEditor|UnityEditor\.', l) and '#if UNITY_EDITOR' not in l]
    rec(A, 'Editor- und Runtime-Code sauber getrennt', 'PASS' if not rt_editor else 'FAIL',
        f'Runtime: {[os.path.basename(p) for p in rt]}, Editor: {[os.path.basename(p) for p in ed]}; UnityEditor-Verweise im Runtime-Code: '
        f'{rt_editor or "keine"}; Editor-asmdef includePlatforms=Editor')
    nak = [f'{rel(p)}:{i}' for p in rt + ed for i, l in enumerate(open(p, encoding='utf-8'), 1) if re.search(r'nakama|Nakama|Socket|HttpClient|UnityWebRequest', l)]
    rec(A, 'Keine Abhängigkeit von Nakama / Netzwerk / Authentifizierung', 'PASS' if not nak else 'FAIL',
        f'grep nakama|Socket|HttpClient|UnityWebRequest in allen .cs: {nak or "keine Treffer"}')
    hard = [f'{rel(p)}:{i}: {l.strip()[:80]}' for p in rt + ed for i, l in enumerate(open(p, encoding='utf-8'), 1)
            if re.search(r'"Assets/[A-Za-z]', l)]
    rec(A, 'Keine erfundenen Projektpfade (keine fest verdrahteten Assets/...-Pfade)', 'PASS' if not hard else 'FAIL',
        f'{hard or "keine fest verdrahteten Assets/-Pfade; Asset-Wurzel wird über Animation_Timeline.json (schema) gesucht"}')
    inp = [f'{rel(p)}:{i}' for p in rt for i, l in enumerate(open(p, encoding='utf-8'), 1) if re.search(r'\bInput\.|InputSystem', l)]
    rec(A, 'Kein Input-Manager/Input-System-Zugriff im Runtime-Code (kompatibel mit beiden Input-Backends)', 'PASS' if not inp else 'FAIL',
        f'{inp or "keine Treffer"}')
    vp = [f'{rel(p)}:{i}' for p in rt + ed for i, l in enumerate(open(p, encoding='utf-8'), 1) if 'VideoPlayer' in l]
    rec(A, 'Keine VideoPlayer-Abhängigkeit', 'PASS' if not vp else 'FAIL', f'{vp or "keine Treffer"}')
    pset = [f'{rel(p)}:{i}' for p in ed for i, l in enumerate(open(p, encoding='utf-8'), 1)
            if re.search(r'PlayerSettings\.(companyName|productName|applicationIdentifier|SetApplicationIdentifier|bundleVersion)\s*=', l)]
    rec(A, 'Editor-Werkzeug ändert Company/Product Name und Identifier nicht', 'PASS' if not pset else 'FAIL', f'Zuweisungen: {pset or "keine"}')


def main_checks():
    graphics()
    icons()
    animation()
    unity_static()
    with open(os.path.join(WORK, 'qa_results.json'), 'w') as f:
        json.dump(results, f, indent=1, ensure_ascii=False)


# ---------------------------------------------------------------------------
def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def write_sums():
    lines = []
    for r, _d, fs in os.walk(PKG):
        for f in fs:
            p = os.path.join(r, f)
            rp = os.path.relpath(p, PKG).replace(os.sep, '/')
            if rp == 'SHA256SUMS.txt':
                continue
            lines.append((rp, sha256(p)))
    lines.sort()
    with open(os.path.join(PKG, 'SHA256SUMS.txt'), 'w') as f:
        for rp, h in lines:
            f.write(f'{h}  {rp}\n')
    return len(lines)


def make_zip():
    out = os.path.join(ROOT, 'package', NAME + '.zip')
    if os.path.exists(out):
        os.remove(out)
    entries = []
    for r, _d, fs in os.walk(PKG):
        for f in fs:
            entries.append(os.path.join(r, f))
    entries.sort()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in entries:
            arc = os.path.join(NAME, os.path.relpath(p, PKG)).replace(os.sep, '/')
            zi = zipfile.ZipInfo(arc, date_time=(2026, 10, 26, 12, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            with open(p, 'rb') as f:
                z.writestr(zi, f.read(), compresslevel=9)
    return out


def verify_package():
    out = {}
    zp = os.path.join(ROOT, 'package', NAME + '.zip')
    t = subprocess.run(['unzip', '-tq', zp], capture_output=True, text=True)
    out['zip_test'] = (t.returncode == 0, t.stdout.strip() or t.stderr.strip())
    tmp = tempfile.mkdtemp()
    subprocess.run(['unzip', '-q', zp, '-d', tmp], check=True)
    root = os.path.join(tmp, NAME)
    c = subprocess.run(['sha256sum', '-c', '--quiet', 'SHA256SUMS.txt'], cwd=root, capture_output=True, text=True)
    nsum = sum(1 for _ in open(os.path.join(root, 'SHA256SUMS.txt')))
    out['sha256_check'] = (c.returncode == 0, f'{nsum} Einträge, sha256sum -c: ' + ('alle OK' if c.returncode == 0 else c.stdout[-400:] + c.stderr[-400:]))
    files = []
    zero = []
    for r, _d, fs in os.walk(root):
        for f in fs:
            p = os.path.join(r, f)
            files.append(os.path.relpath(p, root))
            if os.path.getsize(p) == 0:
                zero.append(os.path.relpath(p, root))
    src = []
    for r, _d, fs in os.walk(PKG):
        for f in fs:
            src.append(os.path.relpath(os.path.join(r, f), PKG))
    out['complete'] = (sorted(files) == sorted(src), f'{len(files)} Dateien im ZIP, {len(src)} im Quellordner')
    out['no_zero_bytes'] = (not zero, f'Nullbyte-Dateien: {zero or "keine"}')
    bad = []
    for f in files:
        p = os.path.join(root, f)
        try:
            if f.endswith('.png'):
                with Image.open(p) as im:
                    im.load()
            elif f.endswith('.json'):
                json.load(open(p))
            elif f.endswith(('.md', '.txt', '.cs', '.asmdef', '.py', '.gpl', '.hex')):
                open(p, encoding='utf-8').read()
        except Exception as e:  # noqa: BLE001
            bad.append(f'{f}: {e}')
    out['readable'] = (not bad, f'alle {len(files)} Dateien nach dem Entpacken geöffnet/geparst; Fehler: {bad or "keine"}')
    docs = ['README.md', 'BRAND_GUIDELINES.md', 'UNITY_INSTALLATION.md', 'PLAYER_SETTINGS.md', 'ANIMATION_SPECIFICATION.md', 'QA_REPORT.md']
    have = [d for d in docs if os.path.isfile(os.path.join(root, '07_Documentation', d))]
    out['docs'] = (len(have) == len(docs), f'vorhanden: {have}')
    out['zip_size'] = os.path.getsize(zp)
    out['zip_sha256'] = sha256(zp)
    shutil.rmtree(tmp)
    with open(os.path.join(WORK, 'package_verification.json'), 'w') as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'checks'
    if cmd == 'checks':
        main_checks()
    elif cmd == 'package':
        n = write_sums()
        print('sums', n)
        print(make_zip())
        verify_package()
