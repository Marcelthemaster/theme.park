"""Generate README.md, BRAND_GUIDELINES.md and ANIMATION_SPECIFICATION.md from the
actual package data (sizes, palette, timeline) so the documentation never drifts
from the files. UNITY_INSTALLATION.md / PLAYER_SETTINGS.md are written by hand,
QA_REPORT.md by qa.py.
"""
from __future__ import annotations

import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pix import RAMPS  # noqa: E402
import variants  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..'))
PKG = os.path.join(ROOT, 'package', 'AVARNETH_Complete_Branding_Startup_V1.0')
DOC = os.path.join(PKG, '07_Documentation')


def size(rel):
    with Image.open(os.path.join(PKG, rel)) as im:
        return im.size


def count(rel, ext=None):
    n = 0
    for _r, _d, fs in os.walk(os.path.join(PKG, rel)):
        n += sum(1 for f in fs if ext is None or f.endswith(ext))
    return n


ROLES = {
    'iron': 'Dunkles Eisen / Anthrazit – Rahmen, Konturen, Extrusion, Schildfeld',
    'gold': 'Altgold / warmes Metall – Wortmarke, Schildrand, A-Flanken, Untertitel',
    'stone': 'Dunkler Naturstein – Bergfestung, Mauern, Sockel',
    'ember': 'Glut / Funken – Tor-Kern, Glutstein, Partikel, glühende Kanten (sparsam)',
    'arcane': 'Arkanes Blau – Fenster der Festung (sehr sparsam, Kontrastakzent)',
}


def brand_guidelines():
    tl = json.load(open(os.path.join(PKG, '04_Animated_Startup', 'Animation_Timeline.json')))
    nat = '01_Brand_Identity/Source_Files/native_1x/'
    rows = []
    for name, var in (('AVARNETH_Logo', 'A – Hauptlogo (Wortmarke)'), ('AVARNETH_Logo_With_Emblem', 'A – Hauptlogo mit optionalem Wappen'),
                      ('AVARNETH_Complete_Logo', 'B – Vollständiger Titel mit Wappen'),
                      ('AVARNETH_Publisher_Presentation', 'C – Publisher-Präsentation'), ('AVARNETH_Emblem', 'D – Wappen / Emblem'),
                      ('AVARNETH_VeilOfEmbers', 'Untertitel (mit Glut-Ornamenten)'), ('AVARNETH_VeilOfEmbers_Plain', 'Untertitel (ohne Ornamente)'),
                      ('Eckertengineering_Presents', 'Publisher-Zeile'), ('Eckertengineering', 'Publisher-Kennung')):
        w, h = size(nat + name + '_1x.png')
        rows.append(f'| {var} | `01_Brand_Identity/{name}.png` | {w}×{h} | {w * 4}×{h * 4} |')
    pal = []
    for ramp, cols in RAMPS.items():
        sw = ' '.join(f'`#{c[0]:02x}{c[1]:02x}{c[2]:02x}`' for c in cols)
        pal.append(f'| **{ramp}** ({len(cols)}) | {ROLES[ramp]} | {sw} |')
    wm = size(nat + 'AVARNETH_Logo_1x.png')
    em = size(nat + 'AVARNETH_Emblem_1x.png')
    return f"""# AVARNETH: VEIL OF EMBERS – Brand Guidelines V1.0

Entwickler & Publisher: **Eckertengineering** · Spielmarke: **AVARNETH: VEIL OF EMBERS** · Kurzbezeichnung: **AVE**

> Der frühere interne Projektname WOE („World of Eckertengineering“) bleibt ausschließlich interner
> Entwicklungsname (Verzeichnisse, Namespaces, Szenen, Nakama-IDs). Er erscheint in **keinem** der hier
> gelieferten Grafik-Assets und darf nicht als sichtbarer Spieltitel verwendet werden.

## 1. Markenarchitektur

| Ebene | Element | Rolle |
|---|---|---|
| Studio | **ECKERTENGINEERING** / „ECKERTENGINEERING PRESENTS“ | dezent, Stahlgrau, eigene 7-px-Pixel-Versalien; konkurriert nie mit dem Titel |
| Spielmarke | **AVARNETH** | dominante Wortmarke, Altgold mit Eisen-Extrusion |
| Untertitel | **VEIL OF EMBERS** | deutlich kleiner (9-px-Versalien), Gold, flankiert von Glut-Rauten; eigener Layer |
| Bildmarke | **Wappen „Das Glut-Tor“** | eigenständig verwendbar (Icon, Favicon, Siegel, Ladeindikator-Deko) |

Alle Elemente liegen getrennt vor (Wortmarke, Untertitel, Wappen, Publisher) und können frei kombiniert
werden; der Untertitel ist separat ein- und ausblendbar.

## 2. Konzept – „Das Glut-Tor“

* **Schild:** geschmiedeter Wappenschild – Außenrahmen aus dunklem Eisen, Innenrand aus Altgold mit Nieten,
  das Feld eine genietete Eisenplatte mit Plattenfuge und dezent eingeprägtem Gebirgsrelief.
* **Das A als Festung:** Zwei goldene Flanken bilden das **A** von AVARNETH; ihr Gipfel durchbricht den
  Schildrand nach oben. Im oberen Innenraum steht ein **Bergfried mit Zinnen und zwei arkanen Lanzettfenstern**
  (der einzige kühle Magie-Akzent), der goldene Querbalken ist der **Sturz** über dem Tor.
* **Monumentales Tor:** im Quadermauerwerk unter dem Sturz – ein **eisernes Fallgitter vor glühender Glut**
  (sauberer 4-stufiger Glutverlauf, kein Dithering).
* **Glutstein:** klein und bündig in die Schildspitze gesetzt – das Siegel der Marke.

Industrielle Fantasy (Schmiede, Eisen, Nieten, Glut) ohne Science-Fiction-Anmutung; keine Neonfarben.
Licht kommt immer von oben links; alle Flächen sind regionsweise monoton schattiert (kein Pixelrauschen).

## 3. Logo-Varianten

| Variante | Datei (1080p-Export ×4) | nativ (1×) | ×4 |
|---|---|---|---|
{chr(10).join(rows)}

* `Source_Files/native_1x/` = Pixel-Master (1 Kunst-Pixel = 1 Bildpixel), `exports_2x/`, `exports_8x/` für andere Zielgrößen.
* Die Wortmarke ist **keine Schrift**: alle Buchstaben sind eigens konstruiert (3:1-Diagonalen bei A/V, 2:1 bei N/R,
  spitze Sporn-Serifen, Turmspitzen-A als Echo des Wappens). A, V, T und H sind pixelgenau spiegelsymmetrisch;
  die Abstände sind optisch ausgeglichen (mittlerer Buchstabenabstand ≈ 7 Kunst-Pixel). Oberfläche: gemeißelte
  Gold-Facetten, Kantenfarben nach echter Kantennormale (durchgehende Lichtkante links, Schattenkante rechts),
  2-px-Extrusion aus dunklem Eisen, 1-px-Kontur.
* Untertitel: eigene 9-px-Kapitälchen in der Konstruktionslogik der Wortmarke, eine Tonstufe ruhiger als AVARNETH,
  flankiert von einer geschmiedeten Linie mit Glut-Raute.
* Publisher: eigene 5-px-Versalien mit 1-px-Strich in einem einzigen flachen Stahlton – bewusst zurückhaltend.

## 4. Schutzzone und Mindestgrößen

![Konstruktion und Schutzzone](images/AVARNETH_Construction_ClearSpace.png)

* **Maßeinheit X** = Versalhöhe der Wortmarke = 32 Kunst-Pixel (1×).
* **Schutzzone:** mindestens ½ X (16 Kunst-Pixel) rund um jede Logo-Variante frei von anderen Elementen.
* **Wortmarke:** nie kleiner als nativ 1× ({wm[0]}×{wm[1]} px). Für kleinere Flächen das Wappen bzw. die Icons verwenden.
* **Wappen:** nativ {em[0]}×{em[1]} px; für 48/64 px die Icon-Fassung (`03_Windows_Icons/AVARNETH_48/64.png`),
  darunter ausschließlich die pro Größe gezeichneten Kleinst-Fassungen (40, 36, 32, 30, 24, 20, 16 px).
* **Untertitel** nie ohne Wortmarke als Spieltitel verwenden; immer unterhalb und kleiner als AVARNETH.

## 5. Farben

Alle Marken-Pixel verwenden ausschließlich diese Master-Palette (Rampen dunkel → hell). Dateien:
`01_Brand_Identity/Source_Files/palette/` (`.gpl` für Aseprite/GIMP/Krita, `.hex`, Code-Tabelle, Farbfeld-PNG).

| Rampe | Rolle | Farben |
|---|---|---|
{chr(10).join(pal)}

Lichtrichtung in allen Assets: **oben links**. Konturen: `iron0` (#07070b). Keine Verläufe außerhalb der Rampen.

## 6. Pixel-Art-Regeln

1. Skalierung nur ganzzahlig mit Nearest Neighbour (×2, ×3, ×4, ×8 …). Niemals bilinear/bikubisch.
2. Keine Drehung (außer 90°-Schritte), keine Verzerrung, keine nachträglichen Filter, Schlagschatten oder Glows –
   Licht- und Glut-Effekte nur über die gelieferten Effekt-Layer.
3. Hintergründe: bevorzugt dunkel (Anthrazit, Nachtlandschaft). Auf hellen/unruhigen Flächen den mitgelieferten
   Abdunkelungs-Layer (`AVE_Veil`) oder eine dunkle Fläche hinterlegen.
4. Unity-Import: Filter **Point (no filter)**, Kompression **None**, Mip Maps **aus** (Details: `ANIMATION_SPECIFICATION.md`).

## 7. Do & Don’t

| Do | Don’t |
|---|---|
| Wortmarke dominant, Untertitel klein darunter | Untertitel größer oder gleich groß wie AVARNETH |
| Publisher dezent und getrennt | ECKERTENGINEERING in Gold oder größer als der Untertitel |
| Ganzzahlige Skalierung | 150 %-Skalierung mit Glättung |
| Wappen allein als App-/EXE-Icon | Die lange Wortmarke als Icon |
| Dunkler Hintergrund oder Veil-Layer | Logo direkt auf hellem, detailreichem Grund |
| Bezeichnung „AVARNETH: VEIL OF EMBERS“ | „WOE“, „World of Eckertengineering“ als Titel |

## 8. Designrichtungen

Alle drei Richtungen teilen exakt dieselbe Geometrie; nur die Materialien wechseln (exaktes Paletten-Remapping,
jedes Pixel bleibt eine Palettenfarbe). Übersicht: `02_Logo_Variants/Variants_Overview.png`.

![Designrichtungen](../02_Logo_Variants/Variants_Overview.png)

| Richtung | Ordner | Charakter |
|---|---|---|
| **Magic & Iron (Produktionsstandard)** | `02_Logo_Variants/Magic_And_Iron/` | {variants.DESCRIPTIONS['Magic_And_Iron']} |
| Classic Fantasy | `02_Logo_Variants/Classic_Fantasy/` | {variants.DESCRIPTIONS['Classic_Fantasy']} |
| Dark Fantasy | `02_Logo_Variants/Dark_Fantasy/` | {variants.DESCRIPTIONS['Dark_Fantasy']} |

**Produktionsstandard ist „Magic & Iron“** – er ist vollständig animiert, als Unity-Assets exportiert und in allen
Vorschauen verwendet. Die beiden anderen Richtungen liegen als statische Alternativen vor.

## 9. Windows-Icon

`03_Windows_Icons/AVARNETH.ico` enthält **15 Größen**: 16, 20, 24, 30, 32, 36, 40, 48, 60, 64, 72, 80, 96, 128, 256 px
(bis 128 als 32-bit-DIB mit Alpha und AND-Maske, 256 als PNG). Damit muss Windows auch bei 125 %/150 %-Skalierung
(20/30/36/40/60/72 px) nicht weichzeichnen.

* 16, 20, 24, 30, 32, 36, 40 px: pro Größe auf dem Pixelraster gezeichnete Kleinst-Fassung – ein geschlossener Schild
  mit mittelgrauer Eisenplatte (bleibt auf dunkler Taskleiste sichtbar), beide A-Schenkel klar golden, dunkler
  Innenraum mit arkanem Fenster, Tor mit Glutkern; keine Funken, kein Anhänger.
* 48/64 px: Icon-Fassung des Wappens (hellere Platte und rechte Seite).
* Alle übrigen Größen sind exakte Ganzzahl-Vielfache: 60 = 20×3, 72 = 24×3, 80 = 40×2, 96 = 48×2, 128/256/512/1024 = 64×2/4/8/16.
* PNG-Einzeldateien: 16/24/32/48/64/128/256/512 im Hauptordner, alle Zwischengrößen und 1024 in `Extra/`.
"""


def anim_spec():
    tl = json.load(open(os.path.join(PKG, '04_Animated_Startup', 'Animation_Timeline.json')))
    lrows = []
    for L in sorted(tl['layers'], key=lambda L: L['order']):
        src = L['sprite'] if not L['frames'] else f"{len(L['frames'])} Frames `{L['frames'][0].split('/')[-1][:-7]}_NN` ({L['frameStart']:.2f}–{L['frameEnd']:.2f} s, danach {L['afterFrames']})"
        if L['sprite'] and not L['frames']:
            w, h = size(os.path.join('05_Unity_Integration', 'Importable_Assets', L['sprite']))
            src = f"`{L['sprite']}` ({w}×{h})"
        keys = ', '.join(f"{k['t']:.2f}s:α{k['alpha']:.2f}" + (f"/dy{k['dy']:+.0f}" if k['dy'] else '') +
                         (f" {k['ease']}" if k['ease'] != 'linear' else '') for k in L['keys'])
        lrows.append(f"| {L['order']} | `{L['id']}` | {src} | ({L['x']}, {L['y']}) | {keys} |")
    groups = {}
    for p in tl['particles']:
        g = 'Phase 1 – Goldfunken am Wappen' if p['t0'] < 0.5 else ('Phase 3 – Glut am Untertitel' if p['t0'] < 1.58 else 'Phase 4 – Goldfunken Akzent')
        groups.setdefault(g, []).append(p)
    prow = [f"| {g} | {len(ps)} | {min(p['t0'] for p in ps):.2f}–{max(p['t0'] + p['life'] for p in ps):.2f} s |" for g, ps in groups.items()]
    # memory estimate (uncompressed RGBA32 textures)
    total = 0
    nsp = 0
    ia = os.path.join(PKG, '05_Unity_Integration', 'Importable_Assets')
    for sub in ('Layers', 'Frames', 'Particles'):
        for f in os.listdir(os.path.join(ia, sub)):
            w, h = size(os.path.join('05_Unity_Integration', 'Importable_Assets', sub, f))
            total += w * h * 4
            nsp += 1
    cb = tl['contentBounds']
    return f"""# AVARNETH Startup – Animationsspezifikation V1.0

Kurze Branding-Animation als **Overlay** über den bestehenden animierten Login-Bootstrap.
Dauer **{tl['duration']:.2f} s** (konfigurierbar 1–3 s, gleichmäßige Zeitskalierung). Keine Szene, kein Video,
kein Ladebildschirm – nur Sprites, die per Code animiert werden.

## 1. Raster und Skalierung

* Kompositions-Raster: **{tl['canvasWidth']} × {tl['canvasHeight']} Kunst-Pixel**; bei 1920×1080 ist 1 Kunst-Pixel = **{tl['pixelScaleAt1080p']}×{tl['pixelScaleAt1080p']} Bildschirm-Pixel**.
* Koordinaten: Ursprung oben links, x nach rechts, y nach unten, ganze Kunst-Pixel. Positionen werden mit
  `floor(v + 0.5)` auf ganze Kunst-Pixel gerastet (kein Sub-Pixel-Zittern zwischen Ebenen).
* Inhaltsbereich (für die Passend-Prüfung bei kleinen Auflösungen): x={cb['x']}, y={cb['y']}, {cb['width']}×{cb['height']}.
* **Vollbild-Ebene:** `veil` hat `"fullscreen": true` – sie liegt nicht auf dem Pixelraster, sondern wird in Unity
  über den ganzen Bildschirm gestreckt (auch 16:10 und 21:9) und mit Bilinear-Filter importiert (weicher Verlauf).
* Unity-Skalierungsmodi (`AvarnethStartupAnimation`): **IntegerNearest** (Standard: round(Screen.height/270), reduziert
  bis der Inhaltsbereich passt, min. 1), IntegerFloor, Continuous (stufenlos, nicht pixel-perfekt).
  Beispiele IntegerNearest: 1280×720 → 3 (Inhalt 720×510 px), 1920×1080 → 4, 2560×1440 → 5, 3840×2160 → 8.

## 2. Phasen

| Zeit | Phase | Inhalt |
|---|---|---|
| 0.00–0.35 s | 1 – Wappen | Eine goldene Lichtlinie zeichnet in 12 Frames (je 1/60 s) die Wappen-Silhouette von der Turmspitze beidseitig bis zur Schildspitze, danach in 4 Frames die beiden A-Schenkel und den Querbalken. Erst wenn die Linie geschlossen ist, blendet die Füllung ein (0.16–0.34 s); kurzes Aufleuchten nur der hellen Flächen, Kontur-Glühen außerhalb der Kontur, 8 Goldfunken lösen sich vom Rand. |
| 0.35–1.15 s | 2 – Wortmarke | Licht führt: Glanzlicht auf den Goldflächen (0.36–0.62 s) während AVARNETH einblendet; ein einziger 1-Kunst-Pixel-Setzschritt bei geringer Deckkraft (0.445 s); goldener Lichtstreif 0.63–1.10 s (28 Frames à 1/60 s, auf die Goldflächen maskiert). Publisher-Zeile blendet dezent auf 65 % ein (0.30–0.60 s). |
| 1.15–1.60 s | 3 – Untertitel | VEIL OF EMBERS blendet ein (1-px-Setzschritt bei geringer Deckkraft), 12 Glutpartikel steigen seitlich der Schrift auf bzw. glimmen unter dem Untertitel – kein Partikel kreuzt Schrift oder Wappen. |
| 1.60–2.00 s | 4 – Akzent & Ausblendung | Gestaffelter Lichtakzent: Glint an der Turmspitze (1.58 s), Kontur-Glühen (1.62 s), Wappen-Glanz (1.64 s), Wortmarken-Glanz (1.66 s), je ≥ 0.10 s weich an- und abschwellend; ab 1.74 s weiches Ausblenden aller Ebenen bis 2.00 s. Der Login-Bootstrap bleibt die ganze Zeit sichtbar (nur abgedunkelt durch `AVE_Veil`). |

## 3. Ebenen (Render-Reihenfolge aufsteigend; Partikel liegen zwischen order < 100 und ≥ 100)

| order | id | Sprite | Position (x, y) | Keys (Zeit: Alpha / dy, Easing des ankommenden Segments) |
|---|---|---|---|---|
{chr(10).join(lrows)}

## 4. Partikel (vorberechnet, deterministisch – identisch in Vorschau und Unity)

| Gruppe | Anzahl | aktiv |
|---|---|---|
{chr(10).join(prow)}

Je Partikel: `sprite, t0, life, x, y, vx, vy, ay, alpha, fadeIn, fadeOut` (Zentrum in Kunst-Pixeln).
Position `x + vx·τ`, `y + vy·τ + ½·ay·τ²`; Alpha `alpha · fadeIn-Rampe · fadeOut-Rampe`. {len(tl['particleSprites'])} Partikel-Sprites
(1×1 bis 1×3 Glut-/Goldpunkte mit kurzer Schweif-Spur). Die Bahnen wurden beim Erzeugen gegen die Logo-Ebenen
geprüft: kein Partikel überdeckt Wappen, Wortmarke, Untertitel oder Publisher-Zeile (deterministischer Seed).

## 5. Interpolation (verbindlich für Vorschau und Unity)

* Keys pro Ebene: Alpha, dx, dy; vor dem ersten Key gilt der erste, nach dem letzten der letzte.
* Zwischen zwei Keys: `u = (t − t₀)/(t₁ − t₀)`, Easing des **ankommenden** Keys: linear, inCubic `u³`,
  outCubic `1 − (1 − u)³`, inOutCubic, smooth `u²(3 − 2u)`, step.
* Flipbooks: Frame-Index `floor((t − start)/(end − start) · N)`; vor `start` unsichtbar; danach `hold` / `sprite` / `hide`.
* Zeit: `Time.unscaledDeltaTime`, pro Frame auf max. 0.1 s begrenzt (ein Lade-Ruckler überspringt Phase 1 nicht).
* Ab `t ≥ duration` ist das Overlay vollständig unsichtbar; Abschluss wird genau einmal gemeldet.

## 6. Dateien

| Ordner | Inhalt |
|---|---|
| `05_Unity_Integration/Importable_Assets/` | **Unity-Quelle:** {nsp} native Sprites (`Layers/`, `Frames/`, `Particles/`), `Icons/`, `Animation_Timeline.json` |
| `04_Animated_Startup/Logo_Layers/`, `Effect_Layers/` | dieselben Ebenen nativ + `1080p_4x/` Vergrößerungen; `Effect_Layers/Flipbooks/` |
| `04_Animated_Startup/Particle_Sprites/` | Partikel nativ + `preview_8x/` |
| `04_Animated_Startup/SpriteSheets/` | Flipbook-Sheets + JSON-Metadaten (Frame-Rechtecke, Zeitfenster) – Referenz/andere Werkzeuge |
| `04_Animated_Startup/Animation_Frames/` | {count('04_Animated_Startup/Animation_Frames/native_480x270_60fps', '.png')} transparente Vollbilder nativ @60 fps + {count('04_Animated_Startup/Animation_Frames/1080p_1920x1080_30fps', '.png')} @1080p/30 fps (Referenz/Fallback) |
| `04_Animated_Startup/Animation_Timeline.json` | Zeitleiste (identisch mit der Kopie in `Importable_Assets/`) |

## 7. Unity-Importeinstellungen (vom Installer automatisch gesetzt)

Texture Type **Sprite (2D and UI)**, Sprite Mode **Single**, Pixels Per Unit 100, Mesh Type **Full Rect**,
Filter **Point (no filter)**, Compression **None**, Generate Mip Maps **aus**, Wrap **Clamp**, Non-Power-of-2 **None**,
sRGB **an**, Alpha Is Transparency **an**, Max Size 2048. Ausnahme: Vollbild-Ebenen (`AVE_Veil`) mit **Bilinear**.
Icons (`Icons/`): Texture Type Default, sonst identisch.

## 8. Laufzeitbudget

* {nsp} kleine Texturen, unkomprimiert zusammen ca. **{total / 1024:.0f} KiB** RGBA32 (größte: Veil 480×270).
* Standard-Material `UI/Default`, reines Alpha-Blending, keine Shader, kein Post-Processing, kein VideoPlayer.
  Lichteffekte sind deshalb als „nur helle Flächen aufhellen“-Masken gezeichnet (kein additiver Shader nötig).
* Nach Ende: Komponente deaktiviert, Root-GameObject deaktiviert (oder zerstört, konfigurierbar) – kein Update läuft weiter.
* Hinweis Farbraum: Die Vorschau mischt Alpha im sRGB-Raum. In einem Projekt mit **Linear**-Farbraum wirken
  halbtransparente Übergänge (Veil, Glows, Fades) in Unity minimal anders; die Pixel der deckenden Logo-Ebenen sind identisch.
"""


def readme():
    return f"""# AVARNETH: VEIL OF EMBERS – Complete Branding & Animated Startup V1.0

Entwickler & Publisher: **Eckertengineering** · Spiel: **AVARNETH: VEIL OF EMBERS** (AVE) ·
Ziel: Unity 6.6 (6000.6.0f1), URP 2D, Windows x64 · Stil: Fantasy-Pixel-Art (32×32-Tile-Ästhetik)

Dieses Paket enthält die vollständig produzierte Markenidentität, das Windows-Icon, die ca. 2-sekündige
Startanimation als transparente Einzel-Layer und Frames, gerenderte Vorschauen sowie ein Unity-Integrationspaket.
Alle Grafiken sind echte Pixel-Art auf nativem Raster (keine Fotos, keine Filter, keine Schriftdateien).

## Schnellstart

1. **Markendateien:** `01_Brand_Identity/` (1080p-Exporte ×4; Pixel-Master in `Source_Files/native_1x/`).
2. **Windows-Icon:** `03_Windows_Icons/AVARNETH.ico` (+ PNG 16–512).
3. **Vorschau ansehen:** `06_Previews/AVARNETH_Startup_Preview.mp4` (Hintergrund = gekennzeichnetes Mock-up).
4. **In Unity einbauen:** `07_Documentation/UNITY_INSTALLATION.md` (Ordner `05_Unity_Integration` kopieren,
   Menü *Tools ▸ AVARNETH ▸ Startup* verwenden). Player-Settings: `07_Documentation/PLAYER_SETTINGS.md`.
5. **Prüfstatus:** `07_Documentation/QA_REPORT.md` (PASS / FAIL / NOT TESTED mit Nachweis).

## Inhalt

| Ordner | Inhalt |
|---|---|
| `01_Brand_Identity/` | Wortmarke, vollständiger Titel, Publisher-Präsentation, Wappen, Untertitel, Publisher (×4) · `Source_Files/` mit 1×/2×/8×, Palette, Pixelmaps, Generator-Quellcode |
| `02_Logo_Variants/` | 3 Designrichtungen (Classic Fantasy, Dark Fantasy, **Magic & Iron = Produktionsstandard**) inkl. Übersicht |
| `03_Windows_Icons/` | `AVARNETH.ico` (15 Größen 16–256 inkl. Windows-Zwischengrößen), PNG 16/24/32/48/64/128/256/512, `Extra/` (20/30/36/40/60/72/80/96/1024) |
| `04_Animated_Startup/` | Logo- und Effekt-Layer, Partikel, Sprite-Sheets (+JSON), transparente Animationsframes, `Animation_Timeline.json` |
| `05_Unity_Integration/` | `Runtime/AvarnethStartupAnimation.cs` (+ `AvarnethStartupTimelineMath.cs`, asmdef), `Editor/AvarnethStartupInstaller.cs` (+ asmdef), `Importable_Assets/` |
| `06_Previews/` | MP4 (1920×1080, 60 fps), GIF, Logo-Standbilder, Icon-Vorschau, Kontaktbogen |
| `07_Documentation/` | README, Brand Guidelines, Unity-Installation, Player Settings, Animationsspezifikation, QA-Bericht, Compile-/API-Nachweis |
| `SHA256SUMS.txt` | SHA-256 jeder Datei im Paket (`sha256sum -c SHA256SUMS.txt`) |

## Bewusst nicht enthalten / Abweichungen von der Zielstruktur

* **`05_Unity_Integration/Prefabs/AvarnethStartup.prefab`** – wird **in Unity** vom Editor-Werkzeug erzeugt
  (*Tools ▸ AVARNETH ▸ Startup ▸ Create / Update Startup Prefab*). Ohne Unity-Editor lässt sich kein verlässlich
  serialisiertes Prefab erzeugen; eine handgeschriebene Prefab-YAML wird absichtlich **nicht** geliefert.
* **`05_Unity_Integration/Materials/`** – nicht benötigt: Die Animation nutzt das Standardmaterial `UI/Default`
  (reines Alpha-Blending, keine eigenen Shader).
* Zusätzliche Ordner/Dateien gegenüber der Zielstruktur: `Runtime/AvarnethStartupTimelineMath.cs` (Unity-freie,
  testbare Zeitleisten-Mathematik), zwei `.asmdef`, `Importable_Assets/Icons/` (inkl. 1024 px für den Unity-Icon-Slot),
  2×/8×-Exporte, `AVARNETH_Logo_With_Emblem`, `AVARNETH_VeilOfEmbers_Plain`, `Eckertengineering.png`.

## Was in dieser Umgebung nicht geprüft werden konnte

Es gab keinen Zugriff auf den Windows-PC, das Unity-Projekt oder die Nakama-Instanz. Unity-Import,
Kompilierung in Unity 6.6, Play-Mode-Verhalten, das EXE-Icon im Windows-Build und die Einbindung in die
bestehende Login-Szene sind daher **NOT TESTED** und müssen lokal nach `UNITY_INSTALLATION.md` geprüft werden.
Details und alle tatsächlich durchgeführten Prüfungen: `QA_REPORT.md`.

## Reproduzierbarkeit

Alle Assets werden deterministisch von `01_Brand_Identity/Source_Files/generator/build_all.py` erzeugt
(Python 3, numpy, Pillow, SciPy; ffmpeg für die Vorschauen).
"""


def main():
    os.makedirs(DOC, exist_ok=True)
    for name, fn in (('BRAND_GUIDELINES.md', brand_guidelines), ('ANIMATION_SPECIFICATION.md', anim_spec), ('README.md', readme)):
        with open(os.path.join(DOC, name), 'w') as f:
            f.write(fn())
        print('wrote', name)


if __name__ == '__main__':
    main()
