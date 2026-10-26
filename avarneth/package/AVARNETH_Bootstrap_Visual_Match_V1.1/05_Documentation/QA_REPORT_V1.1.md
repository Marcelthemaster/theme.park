# QA-Bericht V1.1 – Bootstrap Visual Match

Statuswerte: **PASS** = tatsächlich geprüft und bestanden · **FAIL** = geprüft und fehlgeschlagen · **NOT TESTED** =
nicht geprüft. Grundsatz: *No evidence = no pass.* Alle Prüfungen laufen automatisch in `v11_build.py qa`.

**Zusammenfassung:** 14 PASS · 0 FAIL · 6 NOT TESTED

| Status | Bereich | Prüfung | Nachweis |
|---|---|---|---|
| **PASS** | Grafik | Alle deckenden Pixel aus Master-Palette + V1.1-Rampen (Heraldik-Navy, Festungsstein) | 17 Dateien geprüft (ohne weichen Schleier); Abweichungen: keine |
| **PASS** | Grafik | Logo-/Header-Pixel ohne Halbtransparenz (keine AA-Säume) | Alpha nur 0/255 in Logo, Header und Logo-Ebenen (Glow-Ebenen bewusst gestuft); Abweichungen: keine |
| **PASS** | Grafik | @2x-Exporte = exakte Nearest-Neighbour-Verdopplung | pixelweiser Vergleich aller @2x-Dateien |
| **PASS** | Header | Header-Größe = LogoText-Rect (408 x 104 bei 1080p-Referenz) | @2x: 408 x 104, nativ 204 x 52 (2 Bildschirmpixel pro Kunstpixel) |
| **PASS** | Animation | Alle in der Timeline referenzierten Sprites vorhanden | 67 Referenzen, fehlend: keine |
| **PASS** | Animation | Dauer 2,0 s, Canvas 960 x 540, pixelScaleAt1080p 2 | duration 2.0, canvas 960x540, contentBounds {'x': 256, 'y': 101, 'width': 447, 'height': 321} |
| **PASS** | Animation | Jedes Lichtstreif-Frame enthält Licht | 28 Frames, leer: keine |
| **PASS** | Animation | Timing/Phasen wie V1.0: gleiche Ebenen-Keys/Easing; Partikel je Phase gleiche Anzahl und Zeitfenster | Layer-Keys gleich: True; Partikel je Phase V1.0/V1.1: motes 0.08-0.28 s: 8/8, embers 1.13-1.57 s: 12/12, accent 1.62-1.70 s: 4/4; alle t0 im V1.0-Fenster: True. Hinweis: die einzelnen Zufallsstichproben (t0/Lebensdauer/Sprite) sind NICHT identisch (abweichend), weil die Bahnprüfung gegen die neue Geometrie andere Versuche verwirft - gleiches Skript, gleicher Seed. |
| **PASS** | Regression | V1.0-Generator unverändert reproduzierbar (Dichte 1) | Hashes vor/nach den V1.1-Änderungen: Wortmarke 60ee1e1f36ee807d (Soll 60ee1e1f36ee807d), Timeline 107d85d68d7ee0ff (Soll 107d85d68d7ee0ff), Sprites 0479ce805f56f0e9 (Soll 0479ce805f56f0e9); regenerierte Timeline = ausgelieferte V1.0-Timeline: True; Emblem = ausgeliefertes AVE_Emblem.png: True |
| **PASS** | Unity-Mathematik | C#-Timeline-Mathematik (V1.0-Runtime, unverändert) = Python-Vorschau auf V1.1-Timeline | 30 fps: 2196 Zeilen, 0 Abweichungen; 60 fps: 4356 Zeilen, 0 Abweichungen; 144 fps: 10404 Zeilen, 0 Abweichungen (Konsolen-Harness mit AvarnethStartupTimelineMath.cs, kein Unity) |
| **PASS** | Unity-Mathematik | Pixel-Skalierung je Auflösung (C# ComputePixelScale, IntegerNearest) | canvas 960x540, contentBounds 256,101 447x321 \| screen,scale,art_w,art_h,margin_x,margin_y \| 1920x1080,2,1920,1080,0,0 \| 2560x1440,3,2880,1620,-160,-90 \| 3840x2160,4,3840,2160,0,0 \| 1600x900,2,1920,1080,-160,-90 \| 1366x768,1,960,540,203,114 \| 1280x720,1,960,540,160,90 \| 1280x800,1,960,540,160,130 \| 1680x1050,2,1920,1080,-120,-15 \| 1920x1200,2,1920,1080,0,60 \| 1440x900,2,1920,1080,-240,-90 \| 1536x864,2,1920,1080,-192,-108 \| 2560x1080,2,1920,1080,320,0 \| 3440x1440,3,2880,1620,280,-90 |
| **PASS** | Referenzpaket | Originale Referenzdateien unverändert | sha256sum -c über 151 Einträge der Referenz-SHA256SUMS: alle OK |
| **PASS** | Vorschau | MP4 1920 x 1080, >= 30 fps, ca. 4,5 s, als Mockup gekennzeichnet | h264 1920x1080 @ 60/1 fps, 4.50 s, Label im Bild + Metadaten-Titel; Hintergrund-Capture selbst nur 12 fps |
| **PASS** | Branding | Kein WOE-/„World of Eckertengineering“-Text in den V1.1-Grafiken | Logo, Header und Animationsebenen bestehen nur aus eigenen Pixel-Glyphen (AVARNETH, VEIL OF EMBERS, ECKERTENGINEERING [PRESENTS]); im Mockup sind alle sichtbaren WOE-Texte ersetzt (Liste: TEXT_CHANGES.md) |
| **NOT TESTED** | Nicht geprüft | Import der V1.1-Assets in Unity 6000.6 / Prefab-Update mit dem V1.0-Installer | kein Unity-Editor in dieser Umgebung |
| **NOT TESTED** | Nicht geprüft | Header-Image im echten LogoAreaTopLeft (Darstellung, CanvasScaler, Filter) | Szene nicht im Referenzpaket (Sicherheitsausschluss), kein Unity |
| **NOT TESTED** | Nicht geprüft | CanvasGroup auf LogoAreaTopLeft + „Reveal Login During Fade Out“ zur Laufzeit | kein Unity; nur aus dem Runtime-Code abgeleitet |
| **NOT TESTED** | Nicht geprüft | Tastatureingaben ins Login-Formular während der 2 s | Formular ist mit dieser Einrichtung nicht per CanvasGroup gesperrt (Maus: Raycast-Blocker); nicht geprüft |
| **NOT TESTED** | Nicht geprüft | Textänderungen in Szene/Skripten (Begrüßung, Hinweis, Footer) | Quelle der Texte nicht im Referenzpaket enthalten |
| **NOT TESTED** | Nicht geprüft | Vorschau = echtes Laufzeitbild | Mockup: Capture + Compositing; Retusche der alten Texte per Diffusionsfüllung |

## Pixel-Skalierung je Auflösung (C#-Harness, `ComputePixelScale`, IntegerNearest)

```
canvas 960x540, contentBounds 256,101 447x321
screen,scale,art_w,art_h,margin_x,margin_y
1920x1080,2,1920,1080,0,0
2560x1440,3,2880,1620,-160,-90
3840x2160,4,3840,2160,0,0
1600x900,2,1920,1080,-160,-90
1366x768,1,960,540,203,114
1280x720,1,960,540,160,90
1280x800,1,960,540,160,130
1680x1050,2,1920,1080,-120,-15
1920x1200,2,1920,1080,0,60
1440x900,2,1920,1080,-240,-90
1536x864,2,1920,1080,-192,-108
2560x1080,2,1920,1080,320,0
3440x1440,3,2880,1620,280,-90
```

Negative Ränder bedeuten: Die Canvas ist größer als der Bildschirm, der Inhalt (contentBounds) passt aber. Der Schleier ist
eine Vollbild-Ebene außerhalb der ArtRoot und deckt den Bildschirm immer ganz ab.

## Paketprüfung

Ergebnis des vorherigen Packlaufs (das ZIP kann seinen eigenen Prüfbericht nicht enthalten; die endgültige
Prüfung steht in `AVARNETH_Bootstrap_Visual_Match_V1.1_VERIFICATION.txt` neben dem ZIP):

```
AVARNETH_Bootstrap_Visual_Match_V1.1.zip  size 22832966 bytes  sha256 0046160d00d1d4a68acc8526fa5a4be8212a385967c42df7c6fc7842c6d00585
PASS  zip_test: No errors detected in compressed data of AVARNETH_Bootstrap_Visual_Match_V1.1.zip.
PASS  sha256_check: 111 Einträge, sha256sum -c: alle OK
PASS  complete: 112 Dateien im ZIP, 112 im Quellordner
PASS  no_zero_bytes: Nullbyte-Dateien: keine
```

## Grenzen

* Nichts wurde in Unity ausgeführt. Die Unity-Mathematik wurde mit dem unveränderten V1.0-C#-Code in einem .NET-Konsolen-Harness geprüft.
* Die Vorschau ist ein Mockup (Original-Capture + Compositing). Sie ist kein Beleg für das Laufzeitverhalten.
* Die Textquellen und die Original-Szene lagen nicht vor. Header-Position und Rect stammen aus dem minimierten Referenz-JSON.
