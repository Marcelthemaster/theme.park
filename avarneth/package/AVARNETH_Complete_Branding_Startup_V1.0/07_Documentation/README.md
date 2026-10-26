# AVARNETH: VEIL OF EMBERS – Complete Branding & Animated Startup V1.0

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
| `03_Windows_Icons/` | `AVARNETH.ico` (22 Größen 16–256 inkl. aller Windows-Skalierungsgrößen), PNG 16/24/32/48/64/128/256/512, `Extra/` (alle übrigen Größen inkl. 1024) |
| `04_Animated_Startup/` | Logo- und Effekt-Layer, Partikel, Sprite-Sheets (+JSON), transparente Animationsframes, `Animation_Timeline.json` |
| `05_Unity_Integration/` | `Runtime/AvarnethStartupAnimation.cs` (+ `AvarnethStartupTimelineMath.cs`, asmdef), `Editor/AvarnethStartupInstaller.cs` (+ asmdef), `Importable_Assets/` |
| `06_Previews/` | MP4 (1920×1080, 60 fps), GIF, Logo-Standbilder, Icon-Vorschau, Kontaktbogen |
| `07_Documentation/` | README, Brand Guidelines, Unity-Installation, Player Settings, Animationsspezifikation, QA-Bericht, Compile-/API-Nachweis |
| `SHA256SUMS.txt` | SHA-256 jeder Datei im Paket (`sha256sum -c SHA256SUMS.txt`) |

## Bewusst nicht enthalten / Abweichungen von der Zielstruktur

* **`05_Unity_Integration/Prefabs/AvarnethStartup.prefab`** – wird **in Unity** vom Editor-Werkzeug erzeugt
  (*Tools ▸ AVARNETH ▸ Startup ▸ Create or Update Startup Prefab*). Ohne Unity-Editor lässt sich kein verlässlich
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
(Python 3, numpy, Pillow, SciPy; ffmpeg für die Vorschauen). Ausgabeordner per Umgebungsvariable
`AVARNETH_PACKAGE_DIR` wählen (Standard: `../package/AVARNETH_Complete_Branding_Startup_V1.0` relativ zum
Generator-Ordner) – sonst entsteht beim Aufruf direkt in `Source_Files/generator/` eine verschachtelte Kopie.
