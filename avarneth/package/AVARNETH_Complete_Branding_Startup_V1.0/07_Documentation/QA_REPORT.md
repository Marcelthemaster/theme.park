# AVARNETH Branding & Startup – QA-Bericht V1.0

Erstellt: 2026-10-26 · Umgebung: Linux-Container (Python 3, Pillow, NumPy, SciPy, ffmpeg, icoutils, .NET SDK 8), kein Unity-Editor, kein Windows, kein Zugriff auf das Produktivprojekt.

Statuswerte: **PASS** = tatsächlich geprüft und bestanden · **FAIL** = tatsächlich geprüft und fehlgeschlagen · **NOT TESTED** = nicht geprüft bzw. erforderliche Umgebung nicht vorhanden. Grundsatz: *No evidence = no pass.*

Die Grafik-, Icon-, Animations- und Paketprüfungen sind mit `Source_Files/generator/qa.py` reproduzierbar. Die C#-Prüfungen (Abschnitt 4) liefen in einem Prüfaufbau außerhalb des Pakets (Unity-Referenz-DLLs von NuGet, Harness-Stubs, Konsolen-Harness); er ist in `UNITY_COMPILE_EVIDENCE.md` vollständig beschrieben, wird aber nicht mitgeliefert.

## 1. Grafikprüfung

| Status | Prüfung | Nachweis |
|---|---|---|
| **PASS** | Alle PNG-Dateien lesbar und gültig (PIL verify) | 451 PNG geprüft; Fehler: keine; Nicht-RGBA: keine |
| **PASS** | Transparente PNG korrekt (transparenter Rand, deckende Motivpixel) | 18 Marken-PNG (×4 und 1×): Rand vollständig α=0 und Motiv vorhanden; Probleme: keine |
| **PASS** | Saubere Pixelkanten: keine halbtransparenten Kantenpixel (Alpha nur 0/255) in Logo-, Layer- und Icon-PNGs | 60 Dateien geprüft; Abweichungen: keine |
| **PASS** | Konsistente Farbgestaltung: alle Marken-/Icon-Pixel stammen aus der Master-Palette (bzw. Varianten-Palette) | Palette 45 Farben, davon 32 in den Marken-Mastern verwendet; Abweichungen: keine |
| **PASS** | Keine Artefakte durch Mehrfach-Skalierung: ×2/×4/×8-Exporte sind bitgenaue Nearest-Neighbour-Vergrößerungen der 1×-Master | 27 Exporte pixelgenau verglichen; Abweichungen: keine |
| **PASS** | Titel korrekt geschrieben (AVARNETH / VEIL OF EMBERS / ECKERTENGINEERING PRESENTS) | Glyphen werden ausschließlich aus diesen Zeichenketten gesetzt: ['AVARNETH', 'ECKERTENGINEERING', 'ECKERTENGINEERING PRESENTS', 'VEIL OF EMBERS']; zusätzlich visuell geprüft in 06_Previews/AVARNETH_Logo_Preview.png |
| **PASS** | Kein sichtbares WOE-Altbranding (Dateinamen, gerenderte Texte, C#-Code) | Dateinamen: keine Treffer; Generator-Texte: keine Treffer; C#: keine Treffer (Erwähnung von WOE nur in der Dokumentation als interner Name) |
| **PASS** | Keine Nahtfehler in Glyphen (keine durchgehende Konturlinie ≥ 5 px zwischen Goldflächen, vgl. frühere T/H-Naht) | Wortmarke und Untertitel (1×) Pixel für Pixel geprüft (kurze 1-px-Innenräume wie V-Scheitel/B-Punzen ausgenommen); Funde: keine |
| **PASS** | AVARNETH-Wappen eigenständig verwendbar | 01_Brand_Identity/AVARNETH_Emblem.png 284×320 (nativ 71×80), ohne Text; eigener Animations-Layer Layers/AVE_Emblem.png |
| **PASS** | Untertitel separat | 01_Brand_Identity/AVARNETH_VeilOfEmbers.png (772×88) + _Plain; eigener Timeline-Layer "subtitle" (Layers/AVE_Subtitle.png) |
| **PASS** | Hierarchie: Untertitel deutlich kleiner als die Wortmarke | Versalhöhe Wortmarke 32 px vs. Untertitel 9 px (nativ); Bildhöhen 47 vs. 22 px |

## 2. Windows-Icon-Prüfung

| Status | Prüfung | Nachweis |
|---|---|---|
| **PASS** | ICO-Datei technisch gültig | icotool -l: 22 Bilder [16, 20, 24, 28, 30, 32, 36, 40, 42, 48, 56, 60, 64, 72, 80, 84, 96, 120, 128, 144, 192, 256], 32 bit; Pillow liest [16, 20, 24, 28, 30, 32, 36, 40, 42, 48, 56, 60, 64, 72, 80, 84, 96, 120, 128, 144, 192, 256]; file: "MS Windows icon resource - 22 icons, 16x16, 32 bits/pixel, 20x20, 32 bits/pixel" |
| **PASS** | Benötigte Auflösungen vorhanden (PNG 16/24/32/48/64/128/256/512 + Zwischengrößen, ICO 16–256) | PNG-Maße geprüft: 16, 20, 24, 28, 30, 32, 36, 40, 42, 48, 56, 60, 64, 72, 80, 84, 96, 120, 128, 144, 192, 256, 512, 1024 px (quadratisch); ICO-Einträge [16, 20, 24, 28, 30, 32, 36, 40, 42, 48, 56, 60, 64, 72, 80, 84, 96, 120, 128, 144, 192, 256] (bis 96 px als 32-bit-DIB mit AND-Maske, ab 120 px PNG-komprimiert); 512/1024 nur als PNG (ICO endet bei 256) |
| **PASS** | Keine beschädigten Alpha-Kanäle (ICO-Inhalt bitgenau = PNG-Quellen, Alpha nur 0/255) | icotool -x Extraktion aller 22 Einträge pixelgenau mit den PNGs verglichen (inkl. Alpha); Abweichungen: keine |
| **PASS** | Große/Zwischengrößen sind bitgenaue Ganzzahl-Vielfache (keine Interpolation) | 56=28×2, 60=30×2, 72=36×2, 80=40×2, 84=42×2, 96=48×2, 120=30×4, 144=36×4, 192=48×4, 128=64×2, 256=64×4, 512=64×8, 1024=64×16; Abweichungen: keine |
| **PASS** | Kleine Varianten erkennbar (16–42 px pro Größe gezeichnet, geschlossene Silhouette, hoher Kontrast) | Visuelle Prüfung 1:1 auf dunklem und hellem Grund (06_Previews/AVARNETH_Icon_Preview.png) + unabhängige Bildkritik; Messwerte: 16px: 192 deckende Px, 17 Farben, Helligkeit 7–250, 25 Glut-Px; 20px: 300 deckende Px, 17 Farben, Helligkeit 7–250, 36 Glut-Px; 24px: 424 deckende Px, 18 Farben, Helligkeit 7–250, 61 Glut-Px; 32px: 790 deckende Px, 22 Farben, Helligkeit 7–250, 121 Glut-Px |

## 3. Animationsprüfung

| Status | Prüfung | Nachweis |
|---|---|---|
| **PASS** | Timeline-JSON identisch in 04_Animated_Startup und Importable_Assets | json-Vergleich |
| **PASS** | Einzeldaten ausreichend für Unity: alle in der Timeline referenzierten Sprites existieren, Flipbook-Frames gleich groß | 67 referenzierte Sprite-Dateien, fehlend: keine; Flipbook-Größen konsistent: True; 12 Layer, 24 Partikel, ungültige Partikel-Sprite-Indizes: keine |
| **PASS** | Tatsächliche Dauer ca. 2 Sekunden | duration = 2.00 s; letztes sichtbares Overlay-Frame bei t = 1.983 s (Frame 119 @60 fps); ab t = 2.000 s vollständig transparent (0.0 Alpha-Summe) |
| **PASS** | Kein abrupter Schnitt (weiches Aus-/Einblenden) | Deckungssumme des Overlays je Frame gemessen: größter Sprung zwischen zwei 60-fps-Frames = 8.7 % der Spitze (bei t = 1.883 s); letztes sichtbares Frame hat noch 4.33 % der Spitzendeckung |
| **PASS** | Phasen im vorgegebenen Zeitfenster (Wappen 0–0.35 s, Schriftzug 0.35–1.15 s, Untertitel 1.15–1.60 s) | emblem: sichtbar ab 0.163 s, voll ab 0.338 s (Fenster 0.00–0.35); wordmark: sichtbar ab 0.352 s, voll ab 0.757 s (Fenster 0.35–1.15); subtitle: sichtbar ab 1.152 s, voll ab 1.422 s (Fenster 1.15–1.60) |
| **PASS** | Effektlayer vorhanden (Glow, Flash, Kontur-Glühen, Veil, Flipbooks, Partikel, Sprite-Sheets) | Effect_Layers: ['AVE_EmblemFlash.png', 'AVE_EmblemGlow.png', 'AVE_EmblemOutlineGlow.png', 'AVE_Veil.png', 'AVE_WordmarkFlash.png']; 52 Flipbook-Frames; 6 Partikel-Sprites; Sheets: ['AVE_EmblemTrace_Sheet.png', 'AVE_Glint_Sheet.png', 'AVE_Particles_Sheet.png', 'AVE_WordmarkShine_Sheet.png'] |
| **PASS** | Transparenter Frame-Export vorhanden | 120 Frames 480×270 @60 fps, 60 Frames 1920×1080 @30 fps (RGBA, transparent) |
| **PASS** | Gerenderte MP4-Vorschau (1920×1080, ≥30 fps, Wappen, Schriftzug, Untertitel, Übergang zur Login-Darstellung) | ffprobe: h264 1920×1080 yuv420p 60/1 fps, 180 Frames, 3.000 s = 2.00 s Animation + 1.00 s Login-Mock-up; Inhalte visuell im Kontaktbogen geprüft |
| **PASS** | GIF-Vorschau | 960×540, 90 Frames @30 fps, Endlosschleife |

## 4. Unity-Integrationsprüfung

| Status | Prüfung | Nachweis |
|---|---|---|
| **PASS** | C#-Runtime kompiliert ohne UnityEditor-Referenz (C# 9, netstandard2.1) | dotnet build gegen echte Unity-Referenzassemblies UnityEngine 2021.3.33 (Module) + UnityEngine.UI 2020.3.21: Build OK, 0 Fehler, 0 Warnungen |
| **PASS** | Editor + Runtime kompilieren gemeinsam (Prüfaufbau mit Stubs – kein Unity-Compile) | zusätzlich UnityEditor.dll 2021.1 + Harness-Stubs (nur im Prüfaufbau, nicht im Paket) für die dort fehlenden Unity-6-APIs NamedBuildTarget (Unknown/Standalone/TargetName), PlayerSettings.SetIcons/GetIcons/GetIconSizes(NamedBuildTarget, IconKind), PlayerSettings.SplashScreen.show/showUnityLogo, TextureImporter.GetSourceTextureWidthAndHeight – Signaturen aus dem 6000.6-Quellcode kopiert (Datei:Zeile in UNITY_COMPILE_EVIDENCE.md §5) – Build OK, 0 Fehler, 0 Warnungen |
| **PASS** | Editor-Assembly separat gegen die Runtime-Assembly (asmdef-Aufteilung nachgestellt) | Build OK, 0 Fehler, 0 Warnungen |
| **PASS** | Zeitleisten-Mathematik (Unity-frei) – Selbsttest | Konsolen-Harness net8.0: Build OK, 0 Fehler, 0 Warnungen; --selftest: selftest: 97 passed, 0 failed |
| **PASS** | C#-Laufzeitmathematik = Python-Referenz (Vorschau-Renderer) für die echte Animation_Timeline.json | 16956 CSV-Zeilen (Layer + Partikel je Frame) bei 30 fps, 60 fps, 144 fps verglichen: 0 Abweichungen (Sichtbarkeit, Flipbook-Index, Pixelposition, Alpha ±0.002) |
| **PASS** | Verwendete UnityEngine-/UnityEditor-Member gegen den Unity-6000.6.0f1-Quellcode geprüft (Existenz, Signatur, [Obsolete]) | apicheck_6000_6.py: kuratierte Liste von 185 im Code verwendeten UnityEngine/UnityEditor-Membern gegen die Unity-C#-Reference-Source (Tag 6000.6.0f1): alle gefunden, 0 fehlend, keines [Obsolete]. Ausnahme: uGUI (Image, CanvasScaler, GraphicRaycaster, EventSystem, IPointerClickHandler) ist nicht Teil dieser Quelle und wurde nur gegen uGUI 2020.3.21 kompiliert. Datei:Zeile-Liste in UNITY_COMPILE_EVIDENCE.md |
| **PASS** | Editor- und Runtime-Code sauber getrennt | Runtime: ['AvarnethStartupAnimation.cs', 'AvarnethStartupTimelineMath.cs'], Editor: ['AvarnethStartupInstaller.cs']; UnityEditor-Verweise im Runtime-Code: keine; Editor-asmdef includePlatforms=Editor |
| **PASS** | Keine Abhängigkeit von Nakama / Netzwerk / Authentifizierung | grep nakama\|Socket\|HttpClient\|UnityWebRequest in allen .cs: keine Treffer |
| **PASS** | Keine erfundenen Projektpfade (keine fest verdrahteten Assets/...-Pfade) | keine fest verdrahteten Assets/-Pfade; Asset-Wurzel wird über Animation_Timeline.json (schema) gesucht |
| **PASS** | Kein Input-Manager/Input-System-Zugriff im Runtime-Code (kompatibel mit beiden Input-Backends) | keine Treffer |
| **PASS** | Keine VideoPlayer-Abhängigkeit | keine Treffer |
| **PASS** | Editor-Werkzeug ändert Company/Product Name und Identifier nicht | Zuweisungen: keine |

## 5. Paketprüfung

| Status | Prüfung | Nachweis |
|---|---|---|
| **PASS** | ZIP-Datei vollständig und unbeschädigt (unzip -t) | No errors detected in compressed data of AVARNETH_Complete_Branding_Startup_V1.0.zip. |
| **PASS** | ZIP enthält exakt alle Paketdateien | 512 Dateien im ZIP, 512 im Quellordner |
| **PASS** | Dateien nach dem Entpacken lesbar | alle 512 Dateien nach dem Entpacken geöffnet/geparst; Fehler: keine |
| **PASS** | Keine Nullbyte-Platzhalter | Nullbyte-Dateien: keine |
| **PASS** | Prüfsummen tatsächlich berechnet und nach dem Entpacken verifiziert | 511 Einträge, sha256sum -c: alle OK |
| **PASS** | Dokumentation vorhanden | vorhanden: ['README.md', 'BRAND_GUIDELINES.md', 'UNITY_INSTALLATION.md', 'PLAYER_SETTINGS.md', 'ANIMATION_SPECIFICATION.md', 'QA_REPORT.md', 'UNITY_COMPILE_EVIDENCE.md'] |

Die Paketprüfung wurde am fertig gepackten ZIP ausgeführt (entpacken, `sha256sum -c`, jede Datei öffnen). Da dieser Bericht selbst Teil des Pakets ist, wurde das ZIP nach dem Einfügen des Berichts neu gebaut und mit demselben Skript erneut verifiziert; das Ergebnis dieses letzten Laufs steht in `PACKAGE_VERIFICATION.txt` neben dem ZIP.

## 6. Nicht prüfbar in dieser Umgebung (NOT TESTED)

| Status | Prüfung | Grund / Ersatznachweis |
|---|---|---|
| **NOT TESTED** | Import in Unity 6.6 (6000.6.0f1) / Kompilierung im echten Unity-Editor | kein Unity-Editor in dieser Umgebung; Ersatz: Compile gegen Unity-2021-Referenzassemblies + API-Abgleich mit 6000.6-Quellcode (siehe oben) |
| **NOT TESTED** | Editor-Werkzeug ausführen (Importeinstellungen, Prefab-Erzeugung, Szene, Player-Settings-Helfer) | benötigt Unity-Editor |
| **NOT TESTED** | AvarnethStartup.prefab | nicht geliefert – wird in Unity vom Installer erzeugt (kein ungeprüftes Prefab-YAML) |
| **NOT TESTED** | Play-Mode: Ablauf, Skalierung bei 1280×720 / 1920×1080 / 2560×1440 / 3840×2160, Eingabesperre, Login-CanvasGroup-Wiederherstellung | benötigt Unity-Projekt |
| **NOT TESTED** | Integration in die bestehende Login-/Bootstrap-Szene, Zusammenspiel mit Nakama-Login | kein Zugriff auf Projekt/Server (absichtlich keine Änderungen daran) |
| **NOT TESTED** | EXE-Icon im Windows-Build, Taskleiste, Alt-Tab, Desktop-Verknüpfung | kein Windows-Rechner; ICO technisch geprüft (siehe Abschnitt 2) |
| **NOT TESTED** | Unity-Splashscreen in einem Build tatsächlich deaktiviert | lizenz- und projektabhängig; Schritte in PLAYER_SETTINGS.md |
| **NOT TESTED** | Darstellung im Linear-Farbraum des Projekts | Vorschau mischt Alpha in sRGB; deckende Pixel identisch, Übergänge minimal anders |
| **NOT TESTED** | Performance / Speicher auf dem Zielrechner | Budget dokumentiert (ANIMATION_SPECIFICATION.md §8), nicht gemessen |

## 7. Lokale Abnahme-Checkliste (auf dem Unity-Rechner)

1. Ordner `05_Unity_Integration` nach `Assets/…` kopieren → Console ohne Fehler.
2. *Tools ▸ AVARNETH ▸ Startup ▸ Configure Sprite Import Settings* (Bestätigungsdialog), dann *Create or Update Startup Prefab* → Prefab entsteht ohne Fehlermeldung.
3. *Tools ▸ AVARNETH ▸ Startup ▸ Validate Installation* → keine Fehler.
4. Bestehende Bootstrap-/Login-Szene öffnen, *Add Startup Overlay To Open Scene...*, Login-CanvasGroup zuweisen, Szene speichern.
5. Play: Animation ca. 2 s, danach Overlay deaktiviert, Login bedienbar, keine Fehler/Warnungen; bei 1280×720, 1920×1080, 2560×1440 und einer 21:9-Auflösung prüfen (Abdunklung muss den ganzen Bildschirm decken).
6. Windows-Build mit gesetzten Icons: EXE-, Taskleisten- und Alt-Tab-Symbol prüfen; optional ICO per rcedit ins EXE schreiben (PLAYER_SETTINGS.md); Splash-Einstellungen gemäß PLAYER_SETTINGS.md.
7. Ergebnisse in diesem Bericht von NOT TESTED auf PASS/FAIL setzen.

## 8. Anhang

Vollständiges Compile-/API-Protokoll (englisch, mit allen Befehlen, Datei:Zeile-Nachweisen gegen den Unity-6000.6.0f1-Quellcode, Stub-Liste und Review-Runden): `UNITY_COMPILE_EVIDENCE.md`.

