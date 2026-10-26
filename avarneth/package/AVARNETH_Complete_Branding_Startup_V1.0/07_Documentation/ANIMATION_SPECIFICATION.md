# AVARNETH Startup – Animationsspezifikation V1.0

Kurze Branding-Animation als **Overlay** über den bestehenden animierten Login-Bootstrap.
Dauer **2.00 s** (konfigurierbar 1–3 s, gleichmäßige Zeitskalierung). Keine Szene, kein Video,
kein Ladebildschirm – nur Sprites, die per Code animiert werden.

## 1. Raster und Skalierung

* Kompositions-Raster: **480 × 270 Kunst-Pixel**; bei 1920×1080 ist 1 Kunst-Pixel = **4×4 Bildschirm-Pixel**.
* Koordinaten: Ursprung oben links, x nach rechts, y nach unten, ganze Kunst-Pixel. Positionen werden mit
  `floor(v + 0.5)` auf ganze Kunst-Pixel gerastet (kein Sub-Pixel-Zittern zwischen Ebenen).
* Inhaltsbereich (für die Passend-Prüfung bei kleinen Auflösungen): x=127, y=48, 225×165.
* **Vollbild-Ebene:** `veil` hat `"fullscreen": true` – sie liegt nicht auf dem Pixelraster, sondern wird in Unity
  über den ganzen Bildschirm gestreckt (auch 16:10 und 21:9) und mit Bilinear-Filter importiert (weicher Verlauf).
* Unity-Skalierungsmodi (`AvarnethStartupAnimation`): **IntegerNearest** (Standard: round(Screen.height/270), reduziert
  bis der Inhaltsbereich passt, min. 1), IntegerFloor, Continuous (stufenlos, nicht pixel-perfekt).
  Beispiele IntegerNearest: 1280×720 → 3 (Inhaltsbereich 675×495 px), 1920×1080 → 4, 2560×1440 → 5,
  3840×2160 → 8 (vollständige Tabelle in `UNITY_INSTALLATION.md`).

## 2. Phasen

| Zeit | Phase | Inhalt |
|---|---|---|
| 0.00–0.35 s | 1 – Wappen | Eine goldene Lichtlinie zeichnet in 12 Frames (je 1/60 s) die Wappen-Silhouette von der Turmspitze beidseitig bis zur Schildspitze, danach in 4 Frames die A-Schenkel und den Querbalken; das letzte Bild bleibt stehen und löst sich bis 0.36 s weich auf. Die Füllung blendet erst ab 0.16 s ein; kurzes Aufleuchten (helle Flächen 2 Rampenstufen heller), warmes Kontur-Glühen außerhalb der Kontur, 8 Goldfunken lösen sich vom Rand. |
| 0.35–1.15 s | 2 – Wortmarke | Licht führt: Die Goldflächen leuchten 0.38–0.60 s über ihren Endzustand hinaus, während AVARNETH in einer einzigen weichen Kurve einblendet (keine Positionssprünge). Goldener Lichtstreif 0.63–1.10 s (28 Frames à 1/60 s, jeder Frame trifft die Schrift; hebt die Goldflächen um 1–2 Rampenstufen an, nie dunkler). Publisher-Zeile blendet dezent auf 65 % ein (0.30–0.60 s). |
| 1.15–1.60 s | 3 – Untertitel | VEIL OF EMBERS blendet in einer weichen Kurve ein; 12 Glutpartikel lösen sich von den Enden der Ornament-Linien bzw. glimmen unter der Grundlinie – kein Partikel kreuzt Schrift oder Wappen. |
| 1.60–2.00 s | 4 – Akzent & Ausblendung | Gestaffelter Lichtakzent mit Höhepunkt vor dem Ausblenden: Glint an der Turmspitze (1.60–1.73 s), Kontur-Glühen (Spitze 1.68 s), Wappen- und Wortmarken-Glanz (Spitze 1.70 s). Ab 1.76 s blenden die Logo-Ebenen mit inCubic aus (bleiben lange satt und durchlaufen die halbtransparenten Zwischenstufen schnell), die Abdunkelung ab 1.74 s. Der Login-Bootstrap bleibt die ganze Zeit sichtbar. |

## 3. Ebenen (Render-Reihenfolge aufsteigend; Partikel liegen zwischen order < 100 und ≥ 100)

| order | id | Sprite | Position (x, y) | Keys (Zeit: Alpha / dy, Easing des ankommenden Segments) |
|---|---|---|---|---|
| 0 | `veil` | `Layers/AVE_Veil.png` (480×270) | (0, 0) | 0.00s:α0.00, 0.30s:α1.00 smooth, 1.74s:α1.00, 2.00s:α0.00 smooth |
| 10 | `emblemGlow` | `Layers/AVE_EmblemGlow.png` (96×106) | (191, 55) | 0.16s:α0.00, 0.34s:α0.35 smooth, 1.60s:α0.35, 1.70s:α0.55 smooth, 2.00s:α0.00 smooth |
| 20 | `publisher` | `Layers/AVE_Publisher.png` (116×8) | (182, 54) | 0.30s:α0.00, 0.60s:α0.65 smooth, 1.76s:α0.65, 2.00s:α0.00 inCubic |
| 30 | `emblem` | `Layers/AVE_Emblem.png` (63×72) | (208, 72) | 0.16s:α0.00, 0.34s:α1.00 smooth, 1.76s:α1.00, 2.00s:α0.00 inCubic |
| 32 | `emblemFlash` | `Layers/AVE_EmblemFlash.png` (63×72) | (208, 72) | 0.22s:α0.00, 0.30s:α0.60 smooth, 0.46s:α0.00 smooth, 1.62s:α0.00, 1.70s:α0.55 smooth, 1.80s:α0.00 smooth |
| 33 | `emblemOutlineGlow` | `Layers/AVE_EmblemOutlineGlow.png` (67×76) | (206, 70) | 0.24s:α0.00, 0.34s:α0.70 smooth, 0.60s:α0.00 smooth, 1.60s:α0.00, 1.68s:α0.60 smooth, 1.78s:α0.00 smooth |
| 34 | `emblemTrace` | 16 Frames `AVE_EmblemTrace_NN` (0.00–0.27 s, danach hold) | (206, 70) | 0.00s:α0.00, 0.05s:α1.00 outCubic, 0.27s:α1.00, 0.36s:α0.00 smooth |
| 40 | `wordmark` | `Layers/AVE_Wordmark.png` (213×39) | (133, 149) | 0.35s:α0.00, 0.80s:α1.00 outCubic, 1.76s:α1.00, 2.00s:α0.00 inCubic |
| 41 | `wordmarkFlash` | `Layers/AVE_WordmarkFlash.png` (213×39) | (133, 149) | 0.38s:α0.00, 0.45s:α0.65 smooth, 0.60s:α0.00 smooth, 1.62s:α0.00, 1.70s:α0.60 smooth, 1.80s:α0.00 smooth |
| 42 | `wordmarkShine` | 28 Frames `AVE_WordmarkShine_NN` (0.63–1.10 s, danach hide) | (133, 149) | 0.00s:α1.00 |
| 50 | `subtitle` | `Layers/AVE_Subtitle.png` (185×14) | (147, 193) | 1.15s:α0.00, 1.45s:α1.00 outCubic, 1.76s:α1.00, 2.00s:α0.00 inCubic |
| 110 | `glint` | 8 Frames `AVE_Glint_NN` (1.60–1.73 s, danach hide) | (231, 68) | 0.00s:α1.00 |

## 4. Partikel (vorberechnet, deterministisch – identisch in Vorschau und Unity)

| Gruppe | Anzahl | aktiv |
|---|---|---|
| Phase 1 – Goldfunken am Wappen | 8 | 0.08–0.75 s |
| Phase 3 – Glut am Untertitel | 12 | 1.17–1.95 s |
| Phase 4 – Goldfunken Akzent | 4 | 1.62–1.95 s |

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
| `05_Unity_Integration/Importable_Assets/` | **Unity-Quelle:** 67 native Sprites (`Layers/`, `Frames/`, `Particles/`), `Icons/`, `Animation_Timeline.json` |
| `04_Animated_Startup/Logo_Layers/`, `Effect_Layers/` | dieselben Ebenen nativ + `1080p_4x/` Vergrößerungen; `Effect_Layers/Flipbooks/` |
| `04_Animated_Startup/Particle_Sprites/` | Partikel nativ + `preview_8x/` |
| `04_Animated_Startup/SpriteSheets/` | Flipbook-Sheets + JSON-Metadaten (Frame-Rechtecke, Zeitfenster) – Referenz/andere Werkzeuge |
| `04_Animated_Startup/Animation_Frames/` | 120 transparente Vollbilder nativ @60 fps + 60 @1080p/30 fps (Referenz/Fallback) |
| `04_Animated_Startup/Animation_Timeline.json` | Zeitleiste (identisch mit der Kopie in `Importable_Assets/`) |

## 7. Unity-Importeinstellungen (vom Installer automatisch gesetzt)

Texture Type **Sprite (2D and UI)**, Sprite Mode **Single**, Pixels Per Unit 100, Mesh Type **Full Rect**,
Filter **Point (no filter)**, Compression **None**, Generate Mip Maps **aus**, Wrap **Clamp**, Non-Power-of-2 **None**,
sRGB **an**, Alpha Is Transparency **an**, Max Size **≥ 2048**. Ausnahme: Vollbild-Ebenen (`AVE_Veil`) mit **Bilinear**.
Icons (`Icons/`): Texture Type **Default**, Filter **Point**, Mip Maps **aus**, Compression **None**, Non-Power-of-2 **None**,
Max Size **≥ 2048** (Wrap/sRGB/Alpha Is Transparency werden für Icons nicht verändert).

## 8. Laufzeitbudget

* 67 kleine Texturen, unkomprimiert zusammen ca. **1916 KiB** RGBA32 (größte: Veil 480×270).
* Standard-Material `UI/Default`, reines Alpha-Blending, keine Shader, kein Post-Processing, kein VideoPlayer.
  Lichteffekte sind deshalb als „nur helle Flächen aufhellen“-Masken gezeichnet (kein additiver Shader nötig).
* Nach Ende: Komponente deaktiviert, Root-GameObject deaktiviert (oder zerstört, konfigurierbar) – kein Update läuft weiter.
* Hinweis Farbraum: Die Vorschau mischt Alpha im sRGB-Raum. In einem Projekt mit **Linear**-Farbraum wirken
  halbtransparente Übergänge (Veil, Glows, Fades) in Unity minimal anders; die Pixel der deckenden Logo-Ebenen sind identisch.
