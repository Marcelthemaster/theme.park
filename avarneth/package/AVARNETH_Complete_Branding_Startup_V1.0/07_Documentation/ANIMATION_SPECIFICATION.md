# AVARNETH Startup – Animationsspezifikation V1.0

Kurze Branding-Animation als **Overlay** über den bestehenden animierten Login-Bootstrap.
Dauer **2.00 s** (konfigurierbar 1–3 s, gleichmäßige Zeitskalierung). Keine Szene, kein Video,
kein Ladebildschirm – nur Sprites, die per Code animiert werden.

## 1. Raster und Skalierung

* Kompositions-Raster: **480 × 270 Kunst-Pixel**; bei 1920×1080 ist 1 Kunst-Pixel = **4×4 Bildschirm-Pixel**.
* Koordinaten: Ursprung oben links, x nach rechts, y nach unten, ganze Kunst-Pixel. Positionen werden mit
  `floor(v + 0.5)` auf ganze Kunst-Pixel gerastet (kein Sub-Pixel-Zittern zwischen Ebenen).
* Inhaltsbereich (für die Passend-Prüfung bei kleinen Auflösungen): x=126, y=47, 227×168.
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
| 0 | `veil` | `Layers/AVE_Veil.png` (480×270) | (0, 0) | 0.00s:α0.00, 0.30s:α1.00 smooth, 1.70s:α1.00, 2.00s:α0.00 smooth |
| 10 | `emblemGlow` | `Layers/AVE_EmblemGlow.png` (96×106) | (191, 56) | 0.16s:α0.00, 0.34s:α0.35 smooth, 1.60s:α0.35, 1.72s:α0.60 smooth, 2.00s:α0.00 smooth |
| 20 | `publisher` | `Layers/AVE_Publisher.png` (115×10) | (182, 53) | 0.30s:α0.00, 0.60s:α0.65 smooth, 1.74s:α0.65, 2.00s:α0.00 smooth |
| 30 | `emblem` | `Layers/AVE_Emblem.png` (63×72) | (208, 73) | 0.16s:α0.00, 0.34s:α1.00 smooth, 1.74s:α1.00, 2.00s:α0.00 smooth |
| 32 | `emblemFlash` | `Layers/AVE_EmblemFlash.png` (63×72) | (208, 73) | 0.22s:α0.00, 0.32s:α0.55 smooth, 0.50s:α0.00 smooth, 1.64s:α0.00, 1.76s:α0.40 smooth, 1.90s:α0.00 smooth |
| 33 | `emblemOutlineGlow` | `Layers/AVE_EmblemOutlineGlow.png` (67×76) | (206, 71) | 0.24s:α0.00, 0.34s:α0.90 smooth, 0.60s:α0.00 smooth, 1.62s:α0.00, 1.72s:α0.60 smooth, 1.86s:α0.00 smooth |
| 34 | `emblemTrace` | 16 Frames `AVE_EmblemTrace_NN` (0.00–0.27 s, danach hide) | (206, 71) | 0.00s:α0.00, 0.05s:α1.00 outCubic |
| 40 | `wordmark` | `Layers/AVE_Wordmark.png` (215×40) | (132, 150) | 0.35s:α0.00/dy+1, 0.44s:α0.25/dy+1, 0.45s:α0.27 step, 0.80s:α1.00 outCubic, 1.74s:α1.00, 2.00s:α0.00 smooth |
| 41 | `wordmarkFlash` | `Layers/AVE_WordmarkFlash.png` (215×40) | (132, 150) | 0.36s:α0.00/dy+1, 0.44s:α0.50/dy+1 smooth, 0.45s:α0.50 step, 0.62s:α0.00 smooth, 1.66s:α0.00, 1.78s:α0.40 smooth, 1.92s:α0.00 smooth |
| 42 | `wordmarkShine` | 28 Frames `AVE_WordmarkShine_NN` (0.63–1.10 s, danach hide) | (132, 150) | 0.00s:α1.00 |
| 50 | `subtitle` | `Layers/AVE_Subtitle.png` (185×14) | (147, 195) | 1.15s:α0.00/dy+1, 1.22s:α0.22/dy+1, 1.23s:α0.24 step, 1.45s:α1.00 outCubic, 1.74s:α1.00, 2.00s:α0.00 smooth |
| 110 | `glint` | 10 Frames `AVE_Glint_NN` (1.58–1.75 s, danach hide) | (231, 69) | 0.00s:α1.00 |

## 4. Partikel (vorberechnet, deterministisch – identisch in Vorschau und Unity)

| Gruppe | Anzahl | aktiv |
|---|---|---|
| Phase 1 – Goldfunken am Wappen | 8 | 0.08–0.75 s |
| Phase 3 – Glut am Untertitel | 12 | 1.13–1.97 s |
| Phase 4 – Goldfunken Akzent | 4 | 1.62–1.96 s |

Je Partikel: `sprite, t0, life, x, y, vx, vy, ay, alpha, fadeIn, fadeOut` (Zentrum in Kunst-Pixeln).
Position `x + vx·τ`, `y + vy·τ + ½·ay·τ²`; Alpha `alpha · fadeIn-Rampe · fadeOut-Rampe`. 6 Partikel-Sprites
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
| `05_Unity_Integration/Importable_Assets/` | **Unity-Quelle:** 69 native Sprites (`Layers/`, `Frames/`, `Particles/`), `Icons/`, `Animation_Timeline.json` |
| `04_Animated_Startup/Logo_Layers/`, `Effect_Layers/` | dieselben Ebenen nativ + `1080p_4x/` Vergrößerungen; `Effect_Layers/Flipbooks/` |
| `04_Animated_Startup/Particle_Sprites/` | Partikel nativ + `preview_8x/` |
| `04_Animated_Startup/SpriteSheets/` | Flipbook-Sheets + JSON-Metadaten (Frame-Rechtecke, Zeitfenster) – Referenz/andere Werkzeuge |
| `04_Animated_Startup/Animation_Frames/` | 120 transparente Vollbilder nativ @60 fps + 60 @1080p/30 fps (Referenz/Fallback) |
| `04_Animated_Startup/Animation_Timeline.json` | Zeitleiste (identisch mit der Kopie in `Importable_Assets/`) |

## 7. Unity-Importeinstellungen (vom Installer automatisch gesetzt)

Texture Type **Sprite (2D and UI)**, Sprite Mode **Single**, Pixels Per Unit 100, Mesh Type **Full Rect**,
Filter **Point (no filter)**, Compression **None**, Generate Mip Maps **aus**, Wrap **Clamp**, Non-Power-of-2 **None**,
sRGB **an**, Alpha Is Transparency **an**, Max Size 2048. Ausnahme: Vollbild-Ebenen (`AVE_Veil`) mit **Bilinear**.
Icons (`Icons/`): Texture Type Default, sonst identisch.

## 8. Laufzeitbudget

* 69 kleine Texturen, unkomprimiert zusammen ca. **1953 KiB** RGBA32 (größte: Veil 480×270).
* Standard-Material `UI/Default`, reines Alpha-Blending, keine Shader, kein Post-Processing, kein VideoPlayer.
  Lichteffekte sind deshalb als „nur helle Flächen aufhellen“-Masken gezeichnet (kein additiver Shader nötig).
* Nach Ende: Komponente deaktiviert, Root-GameObject deaktiviert (oder zerstört, konfigurierbar) – kein Update läuft weiter.
* Hinweis Farbraum: Die Vorschau mischt Alpha im sRGB-Raum. In einem Projekt mit **Linear**-Farbraum wirken
  halbtransparente Übergänge (Veil, Glows, Fades) in Unity minimal anders; die Pixel der deckenden Logo-Ebenen sind identisch.
