# AVARNETH: VEIL OF EMBERS – Bootstrap Visual Match V1.1

Gezielte Nachbesserung des V1.0-Brandings an den **echten** Login-Bootstrap (Bergfestung, linkes Login-Panel).
Dies ist ein **Delta-Paket**: Es enthält nur geänderte bzw. zusätzliche Dateien. Basis bleibt
`AVARNETH_Complete_Branding_Startup_V1.0.zip` (Unity-Skripte, Installer, Icons, Designrichtungen, V1.0-Doku).
Die Dateien des Referenzpakets `AVARNETH_Bootstrap_Claude_Reference` wurden nicht verändert (SHA-256 geprüft) und
sind nicht in diesem Paket enthalten. Nur die Vorschaubilder/-videos verwenden Pixel der Original-Capture.

## 1. Visueller Abgleich (Vorher → Nachher)

Grundlage: `Existing_Previews/Unity_Capture/Login.png`, `Login-20s_COMPRESSED_REFERENCE.mp4`,
`LoginArtworkPrototype1/login_base_clean.png`, `SCENE_VISUAL_REFERENCE_LOGIN_ONLY.json`,
`WoeBootstrapArtworkPrototype.cs` (Skalierung), `WoeUiDesignTokens.asset` (UI-Farben).

| Frage | Befund V1.0 | Anpassung V1.1 |
|---|---|---|
| Passt die Detailstufe? | Die Festung (879 × 510 px) wird mit Point-Filter auf ca. **2,18 Bildschirmpixel pro Kunstpixel** skaliert (`WoeBootstrapArtworkPrototype.UpdateArtworkScale`: max(1920/879, 1080/510)). Das V1.0-Logo nutzt **4** – es wirkt fast doppelt so grob. | Gleiche Entwürfe auf **doppelt feinem Raster** neu berechnet: **2 Bildschirmpixel pro Kunstpixel** bei 1080p (Canvas 960 × 540 statt 480 × 270). Konturen, Kanten und Diagonalen werden dadurch halb so dick bzw. glatter. |
| Farben & Lichtwirkung harmonisch? | Das neutrale Dunkeleisen des Wappens (#262833) wirkt in der hellen Tagesszene wie ein schwarzes Loch. Die Festung trägt navyblaue Banner mit Goldborte (#303d60/#425072), das Panel ist #1f314b. | Eisen-Rampe → **Heraldik-Navy** (aus Bannern/Panel abgetastet), Stein-Rampe → **Festungsstein** (violettgraue Schatten, cremefarbene Lichter). Feld mit dezentem Rautenmuster und Lichtschimmer oben links wie bei den Bannern; Turm im A sonnenbeschienen. Gold, Glut und Arkan unverändert (UI-Gold #d8b867 liegt zwischen gold6 und gold7). Schleierfarbe Schwarz → Panel-Navy. |
| Goldener Schriftzug lesbar? | Ja, aber grob. Die Stufen der Diagonalen sind auf 4 px deutlich sichtbar. | Gleiche Glyphen-Polygone in doppelter Auflösung abgetastet, Metallverlauf auf den Flächen, 1-px-Kontur + 4-px-Extrusion in Navy. Großbuchstaben 64 Kunstpixel = 128 Bildschirmpixel hoch (1080p, wie V1.0), Header: 21 Kunstpixel = 42 px. |
| Wappen zu grobpixelig? | Ja (siehe `04_Previews/Before_After/Pixel_Density_1to1.png`). | `AVE_Emblem.png` 127 × 144 statt 63 × 72 Kunstpixel, Darstellung in derselben Bildschirmgröße. |
| Konturen & Schatten passend? | Die 4 px breiten Konturen sind dicker als die Linien der Festung. | Die Kontur ist jetzt 2 Bildschirmpixel breit und damit so fein wie die dunklen Linien der Festung. Die Schatten liegen in Navy statt Schwarz. |
| Größe & Position im Login? | Das Startup-Logo liegt mittig über allen 1920 px, der alte WOE-Titel steht links. | Startup weiterhin bildschirmmittig (Inhalt 447 × 321 Kunstpixel = 894 × 642 px bei 1080p). **Statischer Header** 408 × 104 px exakt im Rechteck von `LogoAreaTopLeft/LogoText`. |

Unverändert gelassen (bewusst): Markenidentität (AVARNETH / VEIL OF EMBERS / ECKERTENGINEERING), Aufbau von Wappen
(Schild, A als Festung, Turm, Tor mit Glut, Glutstein) und Schriftzug, Timing aller Ebenen (Phasen 0–0,35 / 0,35–1,15 /
1,15–1,60 / 1,60–2,00 s), Windows-Icon/ICO (keine echten Gestaltungsprobleme gefunden), die drei Designrichtungen,
alle Unity-C#-Dateien und der Installer, die Bergfestung und die Login-UI-Struktur.

Hinweis zur Bildschirmgröße: Die V1.0-Runtime wählt die Ganzzahl-Skalierung über `Snap(Bildschirmhöhe / 540)`.
Bei 1280 × 720 und 1366 × 768 ergibt das **1 Bildschirmpixel pro Kunstpixel**. Das Logo ist dort also relativ kleiner
(ca. 35 % der Bildschirmbreite statt 47 % bei 1080p), aber pixelgenau. Diese Werte stammen aus dem C#-Harness, siehe QA-Bericht.

## 2. Inhalt

| Ordner | Inhalt |
|---|---|
| `01_Logo_Assets/` | Überarbeitete transparente Logo-Assets V1.1: `native/` (1 Datei-Pixel = 1 Kunstpixel) und `1080p_2x/` (Bildschirmgröße bei 1080p, Nearest ×2) – Wappen, Schriftzug, VEIL OF EMBERS (mit/ohne Ornament), ECKERTENGINEERING (PRESENTS), Logo mit Wappen, Komplettlogo. |
| `02_Login_Header/` | Statischer Login-Header `AVARNETH_Login_Header@2x.png` (408 × 104, ersetzt den Titel „World of Eckertengineering“), native Fassung 204 × 52, `Header_Layout.json` (Ziel-RectTransform, Importeinstellungen). |
| `03_Startup_Animation/Importable_Assets/` | Angepasste Animationsebenen + `Animation_Timeline.json` (Version 1.1). Gleiche Dateinamen wie in V1.0 → ersetzt deren `Importable_Assets/Layers|Frames|Particles` + Timeline. `Icons/` bleibt aus V1.0. |
| `04_Previews/` | `AVARNETH_Bootstrap_Matched_Preview.mp4` (visuelles Mockup auf der Original-Capture), Standbilder, Keyframe-Bogen, `Before_After/` (Startup, Login-Header, Pixeldichte 1:1). |
| `05_Documentation/` | Diese Datei, `CODEX_INTEGRATION_V1.1.md`, `TEXT_CHANGES.md`, `CHANGED_FILES.md`, `QA_REPORT_V1.1.md`. |
| `06_Source_Generator/` | Geänderte/neue Generator-Skripte (V1.0-kompatibel: Dichte 1 erzeugt V1.0 bitgleich). |
| `SHA256SUMS.txt` | Tatsächliche SHA-256 aller Dateien des Pakets. |

## 3. Vorschau = Mockup

`AVARNETH_Bootstrap_Matched_Preview.mp4` ist **keine Unity-Aufnahme**. Hintergrund und Login-UI sind Bilder der
Original-Capture (12 fps; der FPS-Zähler oben rechts stammt aus der Capture). Die alten WOE-Texte (Titel, Begrüßung, Hinweis, Footer)
wurden für das Mockup per Diffusionsfüllung entfernt. Die vorgeschlagenen Ersatztexte sind in Liberation Sans gesetzt (Schrift
der vorhandenen TMP-Materialien). Der Header ist an der Position von `LogoText` eingesetzt. Ablauf: 0–2,0 s Startup über dem Bootstrap.
Währenddessen ist `LogoAreaTopLeft` ausgeblendet und blendet in den letzten 0,4 s ein (empfohlene Einrichtung, siehe Codex-Hinweise).
Bis 4,5 s folgt der Login mit Header. Im Bild steht ein Mockup-Hinweis.

## 4. Kosten/Budget

Ich kann die tatsächlichen Nutzungskosten dieser Sitzung weder messen noch begrenzen. Ob das Zielbudget von
20–30 USD eingehalten wurde, kann ich daher **nicht garantieren**. Sparmaßnahmen: keine Multi-Agent-Workflows,
kein neues Design, keine Varianten, ein einziger Vorschau-Renderlauf pro Fassung, Wiederverwendung der V1.0-Generatoren.
