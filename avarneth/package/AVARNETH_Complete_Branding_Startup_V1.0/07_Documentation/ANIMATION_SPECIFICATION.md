# AVARNETH Startup – Animationsspezifikation V1.0

Kurze Branding-Animation als **Overlay** über den bestehenden animierten Login-Bootstrap.
Dauer **2.00 s** (konfigurierbar 1–3 s, gleichmäßige Zeitskalierung). Keine Szene, kein Video,
kein Ladebildschirm – nur Sprites, die per Code animiert werden.

## 1. Raster und Skalierung

* Kompositions-Raster: **480 × 270 Kunst-Pixel**; bei 1920×1080 ist 1 Kunst-Pixel = **4×4 Bildschirm-Pixel**.
* Koordinaten: Ursprung oben links, x nach rechts, y nach unten, ganze Kunst-Pixel. Positionen werden mit
  `floor(v + 0.5)` auf ganze Kunst-Pixel gerastet (kein Sub-Pixel-Zittern zwischen Ebenen).
* Inhaltsbereich (für die Passend-Prüfung bei kleinen Auflösungen): x=120, y=46, 240×170.
* Unity-Skalierungsmodi (`AvarnethStartupAnimation`): **IntegerNearest** (Standard: round(Screen.height/270), reduziert
  bis der Inhaltsbereich passt, min. 1), IntegerFloor, Continuous (stufenlos, nicht pixel-perfekt).
  Beispiele IntegerNearest: 1280×720 → 3 (Inhalt 720×510 px), 1920×1080 → 4, 2560×1440 → 5, 3840×2160 → 8.

## 2. Phasen

| Zeit | Phase | Inhalt |
|---|---|---|
| 0.00–0.35 s | 1 – Wappen | Goldene Lichtlinie zeichnet die Wappen-Silhouette von der Turmspitze beidseitig bis zur Schildspitze (14 Frames), Wappen blendet ein, kurzes Schmiede-Aufleuchten, Kontur-Glühen, Goldfunken, warmer Glow dahinter. Publisher-Zeile blendet dezent ein. |
| 0.35–1.15 s | 2 – Wortmarke | AVARNETH blendet ein und steigt 3 Kunst-Pixel (12 px @1080p) auf; goldener Lichtstreif läuft 0.64–1.12 s über die Buchstaben (16 Frames, auf die Goldfläche maskiert). |
| 1.15–1.60 s | 3 – Untertitel | VEIL OF EMBERS blendet ein (2 Kunst-Pixel Aufstieg), 24 Glutpartikel steigen auf. |
| 1.60–2.00 s | 4 – Akzent & Ausblendung | Glint an der Turmspitze, kurzes Aufleuchten von Wappen-Kontur, Wappen und Wortmarke; ab 1.72 s weiches Ausblenden aller Ebenen bis 2.00 s. Der Login-Bootstrap bleibt die ganze Zeit sichtbar (nur abgedunkelt durch `AVE_Veil`). |

## 3. Ebenen (Render-Reihenfolge aufsteigend; Partikel liegen zwischen order < 100 und ≥ 100)

| order | id | Sprite | Position (x, y) | Keys (Zeit: Alpha / dy, Easing des ankommenden Segments) |
|---|---|---|---|---|
| 0 | `veil` | `Layers/AVE_Veil.png` (480×270) | (0, 0) | 0.00s:α0.00, 0.22s:α1.00 outCubic, 1.68s:α1.00, 2.00s:α0.00 smooth |
| 10 | `emblemGlow` | `Layers/AVE_EmblemGlow.png` (128×136) | (175, 45) | 0.00s:α0.00, 0.32s:α1.00 outCubic, 0.70s:α0.55 smooth, 1.58s:α0.55, 1.68s:α1.00 outCubic, 2.00s:α0.00 smooth |
| 20 | `publisher` | `Layers/AVE_Publisher.png` (178×12) | (151, 52) | 0.05s:α0.00, 0.40s:α0.90 outCubic, 1.72s:α0.90, 2.00s:α0.00 smooth |
| 30 | `emblem` | `Layers/AVE_Emblem.png` (63×72) | (208, 73) | 0.08s:α0.00, 0.34s:α1.00 outCubic, 1.72s:α1.00, 2.00s:α0.00 smooth |
| 32 | `emblemFlash` | `Layers/AVE_EmblemFlash.png` (63×72) | (208, 73) | 0.18s:α0.00, 0.30s:α0.40 outCubic, 0.50s:α0.00 smooth, 1.60s:α0.00, 1.66s:α0.25 outCubic, 1.80s:α0.00 smooth |
| 33 | `emblemOutlineGlow` | `Layers/AVE_EmblemOutlineGlow.png` (67×76) | (206, 71) | 0.30s:α0.00, 0.34s:α1.00 outCubic, 0.64s:α0.00 outCubic, 1.60s:α0.00, 1.66s:α0.80 outCubic, 1.86s:α0.00 smooth |
| 34 | `emblemTrace` | 14 Frames `AVE_EmblemTrace_NN` (0.00–0.34 s, danach hide) | (206, 71) | 0.00s:α1.00 |
| 40 | `wordmark` | `Layers/AVE_Wordmark.png` (228×43) | (126, 149) | 0.35s:α0.00/dy+3, 0.80s:α1.00 outCubic, 1.72s:α1.00, 2.00s:α0.00 smooth |
| 42 | `wordmarkShine` | 16 Frames `AVE_WordmarkShine_NN` (0.64–1.12 s, danach hide) | (126, 149) | 0.00s:α1.00 |
| 44 | `wordmarkFlash` | `Layers/AVE_WordmarkFlash.png` (228×43) | (126, 149) | 1.58s:α0.00, 1.66s:α0.40 outCubic, 1.84s:α0.00 smooth |
| 50 | `subtitle` | `Layers/AVE_Subtitle.png` (190×14) | (145, 196) | 1.15s:α0.00/dy+2, 1.45s:α1.00 outCubic, 1.72s:α1.00, 2.00s:α0.00 smooth |
| 110 | `glint` | 10 Frames `AVE_Glint_NN` (1.58–1.82 s, danach hide) | (231, 67) | 0.00s:α1.00 |

## 4. Partikel (vorberechnet, deterministisch – identisch in Vorschau und Unity)

| Gruppe | Anzahl | aktiv |
|---|---|---|
| Phase 1 – Goldfunken am Wappen | 10 | 0.10–0.82 s |
| Phase 3 – Glut am Untertitel | 24 | 1.13–1.97 s |
| Phase 4 – Goldfunken Akzent | 6 | 1.60–1.94 s |

Je Partikel: `sprite, t0, life, x, y, vx, vy, ay, alpha, fadeIn, fadeOut` (Zentrum in Kunst-Pixeln).
Position `x + vx·τ`, `y + vy·τ + ½·ay·τ²`; Alpha `alpha · fadeIn-Rampe · fadeOut-Rampe`. 7 Partikel-Sprites (1×1 bis 3×3).

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
| `05_Unity_Integration/Importable_Assets/` | **Unity-Quelle:** 56 native Sprites (`Layers/`, `Frames/`, `Particles/`), `Icons/`, `Animation_Timeline.json` |
| `04_Animated_Startup/Logo_Layers/`, `Effect_Layers/` | dieselben Ebenen nativ + `1080p_4x/` Vergrößerungen; `Effect_Layers/Flipbooks/` |
| `04_Animated_Startup/Particle_Sprites/` | Partikel nativ + `preview_8x/` |
| `04_Animated_Startup/SpriteSheets/` | Flipbook-Sheets + JSON-Metadaten (Frame-Rechtecke, Zeitfenster) – Referenz/andere Werkzeuge |
| `04_Animated_Startup/Animation_Frames/` | 120 transparente Vollbilder nativ @60 fps + 60 @1080p/30 fps (Referenz/Fallback) |
| `04_Animated_Startup/Animation_Timeline.json` | Zeitleiste (identisch mit der Kopie in `Importable_Assets/`) |

## 7. Unity-Importeinstellungen (vom Installer automatisch gesetzt)

Texture Type **Sprite (2D and UI)**, Sprite Mode **Single**, Pixels Per Unit 100, Mesh Type **Full Rect**,
Filter **Point (no filter)**, Compression **None**, Generate Mip Maps **aus**, Wrap **Clamp**, Non-Power-of-2 **None**,
sRGB **an**, Alpha Is Transparency **an**, Max Size 2048. Icons (`Icons/`): Texture Type Default, sonst identisch.

## 8. Laufzeitbudget

* 56 kleine Texturen, unkomprimiert zusammen ca. **1628 KiB** RGBA32 (größte: Veil 480×270).
* Standard-Material `UI/Default`, reines Alpha-Blending, keine Shader, kein Post-Processing, kein VideoPlayer.
* Nach Ende: Komponente deaktiviert, Root-GameObject deaktiviert (oder zerstört, konfigurierbar) – kein Update läuft weiter.
* Hinweis Farbraum: Die Vorschau mischt Alpha im sRGB-Raum. In einem Projekt mit **Linear**-Farbraum wirken
  halbtransparente Übergänge (Veil, Glows, Fades) in Unity minimal anders; die Pixel der deckenden Logo-Ebenen sind identisch.
