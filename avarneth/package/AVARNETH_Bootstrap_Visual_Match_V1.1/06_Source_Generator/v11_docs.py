"""Generate the V1.1 documentation (German) from the built package and the QA results."""
from __future__ import annotations

import glob
import json
import os

from PIL import Image

NAME = 'AVARNETH_Bootstrap_Visual_Match_V1.1'


def _size(path):
    with Image.open(path) as im:
        return f'{im.width} × {im.height}'


def _w(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write('\n'.join(lines).rstrip() + '\n')


def write(pkg, work, v10):
    doc = os.path.join(pkg, '05_Documentation')
    qa = json.load(open(os.path.join(work, 'qa_v11.json')))
    tl = json.load(open(os.path.join(pkg, '03_Startup_Animation', 'Importable_Assets', 'Animation_Timeline.json')))
    hl = json.load(open(os.path.join(pkg, '02_Login_Header', 'Header_Layout.json')))
    scales = open(os.path.join(work, 'scales_v11.txt')).read().strip().splitlines()
    ver_path = os.path.join(os.path.dirname(pkg), NAME + '_VERIFICATION.txt')
    ver = open(ver_path).read().strip().splitlines() if os.path.exists(ver_path) else []
    cb = tl['contentBounds']
    counts = {s: sum(1 for r in qa if r['status'] == s) for s in ('PASS', 'FAIL', 'NOT TESTED')}
    em10 = _size(os.path.join(v10, '05_Unity_Integration', 'Importable_Assets', 'Layers', 'AVE_Emblem.png'))
    em11 = _size(os.path.join(pkg, '03_Startup_Animation', 'Importable_Assets', 'Layers', 'AVE_Emblem.png'))

    # ------------------------------------------------------------ README
    _w(os.path.join(doc, 'README_V1.1.md'), [
        '# AVARNETH: VEIL OF EMBERS – Bootstrap Visual Match V1.1',
        '',
        'Gezielte Nachbesserung des V1.0-Brandings an den **echten** Login-Bootstrap (Bergfestung, linkes Login-Panel).',
        'Dies ist ein **Delta-Paket**: Es enthält nur geänderte bzw. zusätzliche Dateien. Basis bleibt',
        '`AVARNETH_Complete_Branding_Startup_V1.0.zip` (Unity-Skripte, Installer, Icons, Designrichtungen, V1.0-Doku).',
        'Die Dateien des Referenzpakets `AVARNETH_Bootstrap_Claude_Reference` wurden nicht verändert (SHA-256 geprüft) und',
        'sind nicht in diesem Paket enthalten. Nur die Vorschaubilder/-videos verwenden Pixel der Original-Capture.',
        '',
        '## 1. Visueller Abgleich (Vorher → Nachher)',
        '',
        'Grundlage: `Existing_Previews/Unity_Capture/Login.png`, `Login-20s_COMPRESSED_REFERENCE.mp4`,',
        '`LoginArtworkPrototype1/login_base_clean.png`, `SCENE_VISUAL_REFERENCE_LOGIN_ONLY.json`,',
        '`WoeBootstrapArtworkPrototype.cs` (Skalierung), `WoeUiDesignTokens.asset` (UI-Farben).',
        '',
        '| Frage | Befund V1.0 | Anpassung V1.1 |',
        '|---|---|---|',
        '| Passt die Detailstufe? | Die Festung (879 × 510 px) wird mit Point-Filter auf ca. **2,18 Bildschirmpixel pro Kunstpixel** skaliert '
        '(`WoeBootstrapArtworkPrototype.UpdateArtworkScale`: max(1920/879, 1080/510)). Das V1.0-Logo nutzt **4** – es wirkt fast doppelt so grob. '
        '| Gleiche Entwürfe auf **doppelt feinem Raster** neu berechnet: **2 Bildschirmpixel pro Kunstpixel** bei 1080p '
        '(Canvas 960 × 540 statt 480 × 270). Konturen, Kanten und Diagonalen werden dadurch halb so dick bzw. glatter. |',
        '| Farben & Lichtwirkung harmonisch? | Das neutrale Dunkeleisen des Wappens (#262833) wirkt in der hellen Tagesszene wie ein schwarzes Loch. '
        'Die Festung trägt navyblaue Banner mit Goldborte (#303d60/#425072), das Panel ist #1f314b. '
        '| Eisen-Rampe → **Heraldik-Navy** (aus Bannern/Panel abgetastet), Stein-Rampe → **Festungsstein** (violettgraue Schatten, '
        'cremefarbene Lichter). Feld mit dezentem Rautenmuster und Lichtschimmer oben links wie bei den Bannern; Turm im A sonnenbeschienen. '
        'Gold, Glut und Arkan unverändert (UI-Gold #d8b867 liegt zwischen gold6 und gold7). Schleierfarbe Schwarz → Panel-Navy. |',
        '| Goldener Schriftzug lesbar? | Ja, aber grob. Die Stufen der Diagonalen sind auf 4 px deutlich sichtbar. '
        '| Gleiche Glyphen-Polygone in doppelter Auflösung abgetastet, Metallverlauf auf den Flächen, 1-px-Kontur + 4-px-Extrusion '
        'in Navy. Großbuchstaben 64 Kunstpixel = 128 Bildschirmpixel hoch (1080p, wie V1.0), Header: 21 Kunstpixel = 42 px. |',
        f'| Wappen zu grobpixelig? | Ja (siehe `04_Previews/Before_After/Pixel_Density_1to1.png`). | `AVE_Emblem.png` {em11} statt {em10} Kunstpixel, '
        'Darstellung in derselben Bildschirmgröße. |',
        '| Konturen & Schatten passend? | Die 4 px breiten Konturen sind dicker als die Linien der Festung. | Die Kontur ist jetzt 2 Bildschirmpixel breit und damit so '
        'fein wie die dunklen Linien der Festung. Die Schatten liegen in Navy statt Schwarz. |',
        f'| Größe & Position im Login? | Das Startup-Logo liegt mittig über allen 1920 px, der alte WOE-Titel steht links. | Startup weiterhin bildschirmmittig '
        f'(Inhalt {cb["width"]} × {cb["height"]} Kunstpixel = {cb["width"] * 2} × {cb["height"] * 2} px bei 1080p). '
        f'**Statischer Header** {hl["size"][0]} × {hl["size"][1]} px exakt im Rechteck von `LogoAreaTopLeft/LogoText`. |',
        '',
        'Unverändert gelassen (bewusst): Markenidentität (AVARNETH / VEIL OF EMBERS / ECKERTENGINEERING), Aufbau von Wappen',
        '(Schild, A als Festung, Turm, Tor mit Glut, Glutstein) und Schriftzug, Timing aller Ebenen (Phasen 0–0,35 / 0,35–1,15 /',
        '1,15–1,60 / 1,60–2,00 s), Windows-Icon/ICO (keine echten Gestaltungsprobleme gefunden), die drei Designrichtungen,',
        'alle Unity-C#-Dateien und der Installer, die Bergfestung und die Login-UI-Struktur.',
        '',
        'Hinweis zur Bildschirmgröße: Die V1.0-Runtime wählt die Ganzzahl-Skalierung über `Snap(Bildschirmhöhe / 540)`.',
        'Bei 1280 × 720 und 1366 × 768 ergibt das **1 Bildschirmpixel pro Kunstpixel**. Das Logo ist dort also relativ kleiner',
        '(ca. 35 % der Bildschirmbreite statt 47 % bei 1080p), aber pixelgenau. Diese Werte stammen aus dem C#-Harness, siehe QA-Bericht.',
        '',
        '## 2. Inhalt',
        '',
        '| Ordner | Inhalt |',
        '|---|---|',
        '| `01_Logo_Assets/` | Überarbeitete transparente Logo-Assets V1.1: `native/` (1 Datei-Pixel = 1 Kunstpixel) und `1080p_2x/` '
        '(Bildschirmgröße bei 1080p, Nearest ×2) – Wappen, Schriftzug, VEIL OF EMBERS (mit/ohne Ornament), '
        'ECKERTENGINEERING (PRESENTS), Logo mit Wappen, Komplettlogo. |',
        '| `02_Login_Header/` | Statischer Login-Header `AVARNETH_Login_Header@2x.png` (408 × 104, ersetzt den Titel „World of '
        'Eckertengineering“), native Fassung 204 × 52, `Header_Layout.json` (Ziel-RectTransform, Importeinstellungen). |',
        '| `03_Startup_Animation/Importable_Assets/` | Angepasste Animationsebenen + `Animation_Timeline.json` (Version 1.1). '
        'Gleiche Dateinamen wie in V1.0 → ersetzt deren `Importable_Assets/Layers|Frames|Particles` + Timeline. `Icons/` bleibt aus V1.0. |',
        '| `04_Previews/` | `AVARNETH_Bootstrap_Matched_Preview.mp4` (visuelles Mockup auf der Original-Capture), Standbilder, '
        'Keyframe-Bogen, `Before_After/` (Startup, Login-Header, Pixeldichte 1:1). |',
        '| `05_Documentation/` | Diese Datei, `CODEX_INTEGRATION_V1.1.md`, `TEXT_CHANGES.md`, `CHANGED_FILES.md`, `QA_REPORT_V1.1.md`. |',
        '| `06_Source_Generator/` | Geänderte/neue Generator-Skripte (V1.0-kompatibel: Dichte 1 erzeugt V1.0 bitgleich). |',
        '| `SHA256SUMS.txt` | Tatsächliche SHA-256 aller Dateien des Pakets. |',
        '',
        '## 3. Vorschau = Mockup',
        '',
        '`AVARNETH_Bootstrap_Matched_Preview.mp4` ist **keine Unity-Aufnahme**. Hintergrund und Login-UI sind Bilder der',
        'Original-Capture (12 fps; der FPS-Zähler oben rechts stammt aus der Capture). Die alten WOE-Texte (Titel, Begrüßung, Hinweis, Footer)',
        'wurden für das Mockup per Diffusionsfüllung entfernt. Die vorgeschlagenen Ersatztexte sind in Liberation Sans gesetzt (Schrift',
        'der vorhandenen TMP-Materialien). Der Header ist an der Position von `LogoText` eingesetzt. Ablauf: 0–2,0 s Startup über dem Bootstrap.',
        'Währenddessen ist `LogoAreaTopLeft` ausgeblendet und blendet in den letzten 0,4 s ein (empfohlene Einrichtung, siehe Codex-Hinweise).',
        'Bis 4,5 s folgt der Login mit Header. Im Bild steht ein Mockup-Hinweis.',
        '',
        '## 4. Kosten/Budget',
        '',
        'Ich kann die tatsächlichen Nutzungskosten dieser Sitzung weder messen noch begrenzen. Ob das Zielbudget von',
        '20–30 USD eingehalten wurde, kann ich daher **nicht garantieren**. Sparmaßnahmen: keine Multi-Agent-Workflows,',
        'kein neues Design, keine Varianten, ein einziger Vorschau-Renderlauf pro Fassung, Wiederverwendung der V1.0-Generatoren.',
    ])

    # ------------------------------------------------------------ Codex integration
    _w(os.path.join(doc, 'CODEX_INTEGRATION_V1.1.md'), [
        '# Integrationshinweise für Codex (V1.1)',
        '',
        '> Nur in einer **isolierten Projektkopie** arbeiten. Keine Änderungen an Nakama, Login-Logik, Server-Konfiguration,',
        '> Namespaces, Szenennamen, der Bergfestung (`LoginAmbient`) oder den PlayerSettings (Company/Product Name).',
        '> Nichts davon wurde in Unity getestet (siehe `QA_REPORT_V1.1.md`).',
        '',
        '## A. Startup-Animation aktualisieren (kein C#-Code nötig)',
        '',
        '1. Voraussetzung: Die V1.0-Integration ist installiert (`05_Unity_Integration` aus V1.0, z. B. unter',
        '   `Assets/AVARNETH/Startup/`, Anleitung `UNITY_INSTALLATION.md` aus V1.0).',
        '2. In `…/Importable_Assets/` die Ordner `Layers/`, `Frames/`, `Particles/` und `Animation_Timeline.json` durch die Dateien aus',
        '   `03_Startup_Animation/Importable_Assets/` **überschreiben** (gleiche Dateinamen; die vorhandenen `.meta`-Dateien bleiben',
        '   liegen → GUIDs bleiben gleich). `Icons/` nicht anfassen.',
        '3. `Tools > AVARNETH > Startup > Configure Sprite Import Settings` → *Apply*.',
        '4. `Tools > AVARNETH > Startup > Create or Update Startup Prefab` (liest Canvas 960 × 540 und contentBounds aus der Timeline).',
        '5. `Tools > AVARNETH > Startup > Validate Installation` – erwartet: keine Fehler.',
        '',
        '## B. Statischer Header im Login (ersetzt „World of Eckertengineering“)',
        '',
        '1. `02_Login_Header/AVARNETH_Login_Header@2x.png` ins Projekt kopieren (z. B. `Assets/AVARNETH/Branding/`).',
        '   Import: Sprite (2D and UI), Single, **Point**, keine Mipmaps, Compression None, Alpha Is Transparency, 100 PPU.',
        '2. Bootstrap-Szene öffnen: `Canvas/UIRoot/LoginScreen/LogoAreaTopLeft/LogoText` **deaktivieren** (nicht löschen).',
        '3. Unter `LogoAreaTopLeft` ein neues UI-Image `AvarnethHeader` direkt nach `LogoText` anlegen. RectTransform wie `LogoText`:',
        '   Anchor Min (0, 1), Anchor Max (1, 1), Pivot (0.5, 1), Position (0, 0), Size Delta (0, 104).',
        '   Sprite = Header, *Preserve Aspect* an, *Raycast Target* aus, Farbe Weiß.',
        '4. `Accent` und `SubtitleText` („PRIVATE ENTWICKLUNGSWELT“) bleiben unverändert.',
        '5. Prüfen, ob ein Skript `LogoText` zur Laufzeit beschreibt oder aktiviert (Szene und Login-Skripte waren nicht im',
        '   Referenzpaket). Falls ja, dort nur die Text-/Aktivierungszeile anpassen, keine Logik.',
        '',
        '## C. Übergabe Startup → Header (empfohlen)',
        '',
        '1. Auf `LogoAreaTopLeft` eine `CanvasGroup` hinzufügen (Alpha 1).',
        '2. Am Overlay `AvarnethStartup` (Komponente `AvarnethStartupAnimation`): *Login Canvas Group* = diese CanvasGroup,',
        '   *Reveal Login During Fade Out* = an, *Reveal Seconds* = 0,4, *Block Input While Playing* = an (Standard).',
        '3. Ergebnis laut Runtime-Code: Header ausgeblendet, solange das große Logo läuft. In den letzten 0,4 s blendet er ein, während das Overlay',
        '   ausblendet. Das Login-Formular bleibt unter dem Schleier sichtbar. Mausklicks fängt der Raycast-Blocker ab,',
        '   **Tastatureingaben ins Formular werden mit dieser Einrichtung nicht gesperrt** (ungetestet).',
        '   Alternative ohne Übergabe: *Login Canvas Group* leer lassen → der Header ist während der 2 s gedimmt sichtbar.',
        '',
        '## D. Sichtbare Texte',
        '',
        'Siehe `TEXT_CHANGES.md` (Begrüßung, Hinweistext, Footer). Nur Texte ändern, keine Objekte umbauen.',
        '',
        '## E. Abnahme in Unity',
        '',
        '1. Play: Startup läuft ca. 2 s, danach Login mit AVARNETH-Header. Es darf kein WOE-Titel aufblitzen.',
        '2. 1920 × 1080: Logo-Pixel 2 × 2 Bildschirmpixel, Header 408 × 104 deckungsgleich mit dem alten Titelbereich.',
        '3. 1280 × 720 / 2560 × 1440 / 3840 × 2160 prüfen (erwartete Skalierung 1 / 3 / 4, siehe QA-Bericht).',
        '4. Login wie bisher möglich. Konsole fehlerfrei. Danach `QA_REPORT_V1.1.md` (NOT TESTED) mit Ergebnissen ergänzen.',
    ])

    # ------------------------------------------------------------ text changes
    _w(os.path.join(doc, 'TEXT_CHANGES.md'), [
        '# Sichtbare Texte, die lokal angepasst werden müssen',
        '',
        'Quelle: `Existing_Previews/Unity_Capture/Login.png` und die 20-s-Capture. Die Herkunft der Strings (Szene `Bootstrap.unity`,',
        'Login-Skripte, Lokalisierung) ist im Referenzpaket **nicht enthalten**. Codex sucht im Projekt nach',
        '`World of Eckertengineering`, `WOE-Nakama`, `Willkommen in`, `Private Entwicklungswelt`.',
        'Die Vorschläge sind im Mockup-Video zu sehen und müssen vom Projektinhaber freigegeben werden.',
        '',
        '| # | Objekt (Hierarchie laut Referenz-JSON) | Aktuell sichtbar | Vorschlag V1.1 | Hinweis |',
        '|---|---|---|---|---|',
        '| 1 | `LoginScreen/LogoAreaTopLeft/LogoText` | „World of“ / „Eckertengineering“ | – (Objekt deaktivieren) | ersetzt durch Header-Bild, siehe CODEX_INTEGRATION B |',
        '| 2 | `LoginScreen/BreakingNewsPanelLeft/NewsBody` (Zeile 1) | „Willkommen in World of Eckertengineering.“ | „Willkommen in AVARNETH: Veil of Embers.“ | |',
        '| 3 | `LoginScreen/BreakingNewsPanelLeft/NewsBody` (Zeilen 2–3) | „Login, Charakterverwaltung und Welteintritt werden weiterhin über den WOE-Nakama-Server ausgeführt.“ '
        '| „Login, Charakterverwaltung und Welteintritt werden weiterhin über den bestehenden Nakama-Server ausgeführt.“ | nur Anzeigetext; Server, Keys, IDs bleiben unverändert |',
        '| 4 | `LoginScreen/BottomCenterCopyright` | „© World of Eckertengineering · Private Entwicklungswelt ™“ | „© Eckertengineering · AVARNETH: Veil of Embers“ '
        '| ™ entfernt, weil kein Markenrecht bekannt. Ob ™ wieder aufgenommen wird, entscheidet der Inhaber. Breite ≤ 408 px eingehalten (15 pt). |',
        '| 5 | `LoginScreen/LogoAreaTopLeft/SubtitleText` | „PRIVATE ENTWICKLUNGSWELT“ | unverändert | enthält keinen WOE-Namen |',
        '| 6 | `LoginScreen/BottomRightVersion` | „Alpha Version 0.1“ | unverändert | |',
        '| 7 | FPS-Anzeige oben rechts („12 FPS“) | Zähler aus der Capture | unverändert | nicht Teil der Login-Hierarchie im Referenz-JSON |',
        '',
        'Nicht sichtbar im Login, aber zu prüfen (nicht geändert): Fenstertitel/Product Name in den PlayerSettings (siehe V1.0',
        '`PLAYER_SETTINGS.md`, keine blinde Änderung). Interne Namen (Namespaces `Woe…`, Nakama-IDs, Ordner) bleiben **WOE**.',
    ])

    # ------------------------------------------------------------ changed files
    ia10 = os.path.join(v10, '05_Unity_Integration', 'Importable_Assets')
    ia11 = os.path.join(pkg, '03_Startup_Animation', 'Importable_Assets')
    rows = []
    for f in sorted(glob.glob(os.path.join(ia11, '**', '*'), recursive=True)):
        if not os.path.isfile(f):
            continue
        rel = os.path.relpath(f, ia11).replace(os.sep, '/')
        old = os.path.join(ia10, rel)
        if rel.endswith('.png'):
            rows.append(f'| `{rel}` | {"ersetzt" if os.path.exists(old) else "NEU"} | {_size(old) if os.path.exists(old) else "–"} | {_size(f)} |')
        else:
            rows.append(f'| `{rel}` | {"ersetzt" if os.path.exists(old) else "NEU"} | Version {json.load(open(old))["version"] if os.path.exists(old) else "–"} | Version {tl["version"]} |')
    removed = sorted(set(os.path.relpath(f, ia10).replace(os.sep, '/') for f in glob.glob(os.path.join(ia10, '**', '*'), recursive=True)
                         if os.path.isfile(f) and not f.endswith('.meta') and '/Icons/' not in f.replace(os.sep, '/'))
                     - set(os.path.relpath(f, ia11).replace(os.sep, '/') for f in glob.glob(os.path.join(ia11, '**', '*'), recursive=True)))
    n_pkg = sum(len(fs) for _, _, fs in os.walk(pkg))
    _w(os.path.join(doc, 'CHANGED_FILES.md'), [
        '# Übersicht der tatsächlich geänderten Dateien (V1.0 → V1.1)',
        '',
        f'Das Paket enthält {n_pkg} Dateien (inkl. `SHA256SUMS.txt`). Prüfsummen jeder Datei: `SHA256SUMS.txt`.',
        '',
        '## Unity: ersetzt Dateien aus V1.0 `05_Unity_Integration/Importable_Assets/`',
        '',
        '| Datei | Status | V1.0 | V1.1 |',
        '|---|---|---|---|',
        *rows,
        '',
        f'V1.0-Dateien ohne V1.1-Gegenstück (außer `Icons/`): {", ".join(removed) if removed else "keine"}.',
        '',
        '## Neu (keine V1.0-Datei wird überschrieben)',
        '',
        '* `01_Logo_Assets/` – Logo-Assets V1.1 (Ergänzung zu V1.0 `01_Brand_Identity/`, V1.0-Dateien bleiben gültig als Archiv).',
        '* `02_Login_Header/` – statischer Login-Header.',
        '* `04_Previews/` – Vorschau auf dem Original-Bootstrap (Mockup), Vorher/Nachher.',
        '* `05_Documentation/` – V1.1-Dokumentation.',
        '',
        '## Generator (`06_Source_Generator/`)',
        '',
        '| Datei | Status | Änderung |',
        '|---|---|---|',
        '| `match_v11.py` | NEU | Heraldik-/Festungsstein-Rampen, Scale2x, feine Assets, Header |',
        '| `preview_v11.py` | NEU | Mockup-Vorschau auf der Original-Capture |',
        '| `v11_build.py`, `v11_docs.py` | NEU | Paketbau, QA, Doku |',
        '| `emblem.py` | geändert | Detailstufe `fine` (Rautenmuster, Lichtschimmer, heller Turm); andere Stufen unverändert |',
        '| `wordmark.py` | geändert | Dichteparameter `kd` (Standard 1 = V1.0 bitgleich), Metallverlauf nur bei `kd > 1` |',
        '| `effects.py` | geändert | Schleierfarbe, Lichtstreif/Glint mit Dichteparameter (Standard = V1.0) |',
        '| `startup.py` | geändert | `build(density=…)`; Dichte 1 = V1.0 bitgleich (Hash-Regression im QA-Bericht) |',
        '',
        'Alle übrigen Generator-Dateien sind unverändert in V1.0 `01_Brand_Identity/Source_Files/generator/` enthalten.',
        '',
        '## Unverändert (nicht im Delta)',
        '',
        '* Unity-C#: `AvarnethStartupAnimation.cs`, `AvarnethStartupTimelineMath.cs`, `AvarnethStartupInstaller.cs`, asmdefs.',
        '* Windows-Icons und `AVARNETH.ico`, die drei Designrichtungen, V1.0-Dokumentation und V1.0-Vorschauen.',
    ])

    # ------------------------------------------------------------ QA report
    def esc(s):
        return str(s).replace('|', '\\|').replace('\n', ' ')
    lines = [
        '# QA-Bericht V1.1 – Bootstrap Visual Match',
        '',
        'Statuswerte: **PASS** = tatsächlich geprüft und bestanden · **FAIL** = geprüft und fehlgeschlagen · **NOT TESTED** =',
        'nicht geprüft. Grundsatz: *No evidence = no pass.* Alle Prüfungen laufen automatisch in `v11_build.py qa`.',
        '',
        f'**Zusammenfassung:** {counts["PASS"]} PASS · {counts["FAIL"]} FAIL · {counts["NOT TESTED"]} NOT TESTED',
        '',
        '| Status | Bereich | Prüfung | Nachweis |',
        '|---|---|---|---|',
    ]
    for r in qa:
        lines.append(f'| **{r["status"]}** | {esc(r["area"])} | {esc(r["check"])} | {esc(r["evidence"])} |')
    lines += ['', '## Pixel-Skalierung je Auflösung (C#-Harness, `ComputePixelScale`, IntegerNearest)', '', '```', *scales, '```', '',
              'Negative Ränder bedeuten: Die Canvas ist größer als der Bildschirm, der Inhalt (contentBounds) passt aber. Der Schleier ist',
              'eine Vollbild-Ebene außerhalb der ArtRoot und deckt den Bildschirm immer ganz ab.', '',
              '## Paketprüfung', '']
    if ver:
        lines += ['Ergebnis des vorherigen Packlaufs (das ZIP kann seinen eigenen Prüfbericht nicht enthalten; die endgültige',
                  f'Prüfung steht in `{NAME}_VERIFICATION.txt` neben dem ZIP):', '', '```', *ver, '```']
    else:
        lines += [f'Siehe `{NAME}_VERIFICATION.txt` neben dem ZIP.']
    lines += ['', '## Grenzen', '',
              '* Nichts wurde in Unity ausgeführt. Die Unity-Mathematik wurde mit dem unveränderten V1.0-C#-Code in einem .NET-Konsolen-Harness geprüft.',
              '* Die Vorschau ist ein Mockup (Original-Capture + Compositing). Sie ist kein Beleg für das Laufzeitverhalten.',
              '* Die Textquellen und die Original-Szene lagen nicht vor. Header-Position und Rect stammen aus dem minimierten Referenz-JSON.']
    _w(os.path.join(doc, 'QA_REPORT_V1.1.md'), lines)
