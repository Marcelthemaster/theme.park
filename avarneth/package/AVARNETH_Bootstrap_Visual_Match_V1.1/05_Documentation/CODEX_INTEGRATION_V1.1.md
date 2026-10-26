# Integrationshinweise für Codex (V1.1)

> Nur in einer **isolierten Projektkopie** arbeiten. Keine Änderungen an Nakama, Login-Logik, Server-Konfiguration,
> Namespaces, Szenennamen, der Bergfestung (`LoginAmbient`) oder den PlayerSettings (Company/Product Name).
> Nichts davon wurde in Unity getestet (siehe `QA_REPORT_V1.1.md`).

## A. Startup-Animation aktualisieren (kein C#-Code nötig)

1. Voraussetzung: Die V1.0-Integration ist installiert (`05_Unity_Integration` aus V1.0, z. B. unter
   `Assets/AVARNETH/Startup/`, Anleitung `UNITY_INSTALLATION.md` aus V1.0).
2. In `…/Importable_Assets/` die Ordner `Layers/`, `Frames/`, `Particles/` und `Animation_Timeline.json` durch die Dateien aus
   `03_Startup_Animation/Importable_Assets/` **überschreiben** (gleiche Dateinamen; die vorhandenen `.meta`-Dateien bleiben
   liegen → GUIDs bleiben gleich). `Icons/` nicht anfassen.
3. `Tools > AVARNETH > Startup > Configure Sprite Import Settings` → *Apply*.
4. `Tools > AVARNETH > Startup > Create or Update Startup Prefab` (liest Canvas 960 × 540 und contentBounds aus der Timeline).
5. `Tools > AVARNETH > Startup > Validate Installation` – erwartet: keine Fehler.

## B. Statischer Header im Login (ersetzt „World of Eckertengineering“)

1. `02_Login_Header/AVARNETH_Login_Header@2x.png` ins Projekt kopieren (z. B. `Assets/AVARNETH/Branding/`).
   Import: Sprite (2D and UI), Single, **Point**, keine Mipmaps, Compression None, Alpha Is Transparency, 100 PPU.
2. Bootstrap-Szene öffnen: `Canvas/UIRoot/LoginScreen/LogoAreaTopLeft/LogoText` **deaktivieren** (nicht löschen).
3. Unter `LogoAreaTopLeft` ein neues UI-Image `AvarnethHeader` direkt nach `LogoText` anlegen. RectTransform wie `LogoText`:
   Anchor Min (0, 1), Anchor Max (1, 1), Pivot (0.5, 1), Position (0, 0), Size Delta (0, 104).
   Sprite = Header, *Preserve Aspect* an, *Raycast Target* aus, Farbe Weiß.
4. `Accent` und `SubtitleText` („PRIVATE ENTWICKLUNGSWELT“) bleiben unverändert.
5. Prüfen, ob ein Skript `LogoText` zur Laufzeit beschreibt oder aktiviert (Szene und Login-Skripte waren nicht im
   Referenzpaket). Falls ja, dort nur die Text-/Aktivierungszeile anpassen, keine Logik.

## C. Übergabe Startup → Header (empfohlen)

1. Auf `LogoAreaTopLeft` eine `CanvasGroup` hinzufügen (Alpha 1).
2. Am Overlay `AvarnethStartup` (Komponente `AvarnethStartupAnimation`): *Login Canvas Group* = diese CanvasGroup,
   *Reveal Login During Fade Out* = an, *Reveal Seconds* = 0,4, *Block Input While Playing* = an (Standard).
3. Ergebnis laut Runtime-Code: Header ausgeblendet, solange das große Logo läuft. In den letzten 0,4 s blendet er ein, während das Overlay
   ausblendet. Das Login-Formular bleibt unter dem Schleier sichtbar. Mausklicks fängt der Raycast-Blocker ab,
   **Tastatureingaben ins Formular werden mit dieser Einrichtung nicht gesperrt** (ungetestet).
   Alternative ohne Übergabe: *Login Canvas Group* leer lassen → der Header ist während der 2 s gedimmt sichtbar.

## D. Sichtbare Texte

Siehe `TEXT_CHANGES.md` (Begrüßung, Hinweistext, Footer). Nur Texte ändern, keine Objekte umbauen.

## E. Abnahme in Unity

1. Play: Startup läuft ca. 2 s, danach Login mit AVARNETH-Header. Es darf kein WOE-Titel aufblitzen.
2. 1920 × 1080: Logo-Pixel 2 × 2 Bildschirmpixel, Header 408 × 104 deckungsgleich mit dem alten Titelbereich.
3. 1280 × 720 / 2560 × 1440 / 3840 × 2160 prüfen (erwartete Skalierung 1 / 3 / 4, siehe QA-Bericht).
4. Login wie bisher möglich. Konsole fehlerfrei. Danach `QA_REPORT_V1.1.md` (NOT TESTED) mit Ergebnissen ergänzen.
