# AVARNETH: VEIL OF EMBERS – Startup-Overlay in Unity installieren

Gilt für Unity **6000.6.0f1** (URP 2D, Windows x64) mit dem mitgelieferten uGUI-Paket (`com.unity.ugui`).

Das Overlay ist eine ca. 2 s lange Branding-Animation, die **über** der bereits vorhandenen, animierten
Bootstrap-/Login-Szene läuft. Es wird **keine** Szene, kein Login, kein zweiter Bootstrap, kein Netzwerk-
oder Authentifizierungs-Code angelegt oder verändert. Kein VideoPlayer, keine eigenen Shader (Standard-Material
`UI/Default`), keine Zusatz-Frameworks.

## Installation

1. Den kompletten Ordner `05_Unity_Integration` in das Projekt kopieren, z. B. nach
   `Assets/AVARNETH/Startup/`. `Importable_Assets/` (Layers/, Frames/, Particles/, Icons/,
   `Animation_Timeline.json`) muss mitkopiert werden.
2. Unity kompilieren lassen. Es entstehen die Assemblies `Eckertengineering.Avarneth.Startup` (Runtime) und
   `Eckertengineering.Avarneth.Startup.Editor` (nur Editor). Die Konsole muss fehlerfrei sein.
3. **Tools > AVARNETH > Startup > Configure Sprite Import Settings**
   Setzt für alle PNGs in `Layers/`, `Frames/`, `Particles/`: Sprite (2D and UI), Single, Point, keine Mipmaps,
   Compression None, Clamp, Non-Power of 2 = None, sRGB an, Alpha Is Transparency an, 100 PPU, Full Rect,
   Max Size ≥ 2048. Für `Icons/`: Default, Point, keine Mipmaps, Compression None, Non-Power of 2 = None.
   Ein Standalone-Override wird entfernt. Andere Dateien werden nicht angefasst.
4. **Tools > AVARNETH > Startup > Create or Update Startup Prefab**
   Erzeugt `<Zielordner>/Prefabs/AvarnethStartup.prefab` (hier `Assets/AVARNETH/Startup/Prefabs/`).
   Fehlt ein Sprite oder ist die Timeline ungültig, bricht das Tool mit Dialog ab und schreibt nichts.
   Ein erneuter Aufruf aktualisiert das vorhandene Prefab; Szenen-Overrides (z. B. die zugewiesene
   Login-CanvasGroup) bleiben erhalten.
5. Die **bestehende** Bootstrap-/Login-Szene öffnen.
6. Optional: In der Hierarchy das GameObject mit der Login-`CanvasGroup` markieren.
7. **Tools > AVARNETH > Startup > Add Startup Overlay To Open Scene...** und bestätigen.
   Das Tool fragt nach, ob die markierte CanvasGroup als *Login Canvas Group* zugewiesen werden soll.
   Ist bereits ein Overlay in einer geladenen Szene, wird nichts verändert. Ein EventSystem wird nie
   automatisch angelegt (nur eine Warnung, falls *Skip On Click* aktiv ist und keines gefunden wird).
8. Szene selbst speichern (**Ctrl+S**). Das Tool markiert die Szene nur als geändert und speichert nie.
9. **Play** drücken.
10. Optional: **Tools > AVARNETH > Startup > Validate Installation** (Bericht in Konsole + Dialog).

Mehrere `Animation_Timeline.json` im Projekt: **Tools > AVARNETH > Startup > Installer...** öffnen und die
richtige Timeline mit *Use* wählen (wird pro Projekt in den EditorPrefs gespeichert).

## Aufbau des Prefabs

```
AvarnethStartup   Canvas (Screen Space - Overlay, Sort Order 1000), CanvasScaler (Constant Pixel Size, 1, 100 PPU),
                  GraphicRaycaster, Image (transparent, Raycast-Blocker), AvarnethStartupAnimation
  ArtRoot         480 x 270, zentriert, localScale = Art-Pixelgröße
    <Layer order < 100>     Image, Anker/Pivot oben links, Raycast Target aus
    Particles               ein Image je gebackenem Partikel
    <Layer order >= 100>
```

## Einstellungen (`AvarnethStartupAnimation`)

| Feld | Standard | Bedeutung |
|---|---|---|
| Play On Start | an | startet in `Start()` |
| Duration | 2 s | 1–3 s, streckt die Timeline gleichmäßig |
| Max Delta Time | 0,1 s | max. Zeitfortschritt pro Frame (`Time.unscaledDeltaTime`), ein Lade-Hänger überspringt den Anfang nicht |
| Scale Mode | IntegerNearest | `round(Screen.height/270)`, verkleinert bis Content Bounds passen, min. 1; `IntegerFloor`; `Continuous` (ohne Ganzzahl) |
| Completion Action | DisableGameObject | alternativ `DestroyGameObject` |
| Block Input While Playing | an | transparentes Vollbild-Image blockt Klicks |
| Skip On Click | aus | Klick überspringt (braucht EventSystem; nutzt `IPointerClickHandler`, funktioniert mit altem Input Manager und Input System) |
| Login Canvas Group | leer | `interactable`/`blocksRaycasts` während des Overlays aus, Originalwerte werden immer wiederhergestellt (Ende, `OnDisable`, `OnDestroy`) |
| Reveal Login During Fade Out | aus | Login-Alpha zuerst 0, in den letzten *Reveal Seconds* (0,4 s) auf den Originalwert |
| On Completed | – | UnityEvent, genau einmal pro Durchlauf |

Integer-Skalierung (volle Content Bounds 480 × 270): 1920×1080 → 4, 2560×1440 → 5, 3840×2160 → 8,
1600×900 → 3, 1366×768 → 2, 1280×720 → 2.

Script-API: `Play()`, `Skip()`, `IsPlaying`, `IsFinished`, `event Action Completed`, `OnCompleted`.

```csharp
overlay.Completed += () => Debug.Log("Startup overlay done");
```

Das Overlay wartet auf nichts, simuliert keinen Ladezustand und verzögert keine Login-Logik. Nach dem Ende
läuft kein `Update` mehr (Komponente deaktiviert, GameObject deaktiviert bzw. zerstört).

**Login-CanvasGroup:** Eine CanvasGroup verwenden, die der Login-Code nicht selbst umschaltet (bei Bedarf eine
eigene CanvasGroup auf das Login-Root-Objekt legen). CanvasGroups wirken verschachtelt, eine zusätzliche Gruppe
ist daher unschädlich.

## Fehlerbehebung

| Symptom | Ursache / Lösung |
|---|---|
| „No TextAsset named 'Animation_Timeline' …“ | `Importable_Assets/Animation_Timeline.json` fehlt oder `schema` ≠ `avarneth.startup.timeline/1`. |
| „Several AVARNETH timelines were found“ | Im *Installer...*-Fenster die gewünschte Timeline mit *Use* wählen. |
| „sprite(s) are missing … not imported as Sprite“ | Schritt 3 ausführen, danach Schritt 4 wiederholen. |
| Pixel unscharf / ungleich breit | Import Settings prüfen (*Validate Installation*), Scale Mode `IntegerNearest`, Game-View-Scale 1x. |
| Overlay liegt hinter dem Login | Sort Order des Canvas auf `AvarnethStartup` erhöhen (Standard 1000). |
| Klick überspringt nicht | *Skip On Click* aktivieren; zur Laufzeit muss ein EventSystem existieren. |
| Konsole: „[AVARNETH Startup] … The overlay is skipped.“ | Referenzen im Prefab fehlen. Schritt 4 wiederholen. Das Overlay beendet sich sofort, der Login bleibt bedienbar. |
| Login bleibt gesperrt | Prüfen, ob der Login-Code dieselbe CanvasGroup umschaltet (siehe oben). |

## Entfernen

1. Das GameObject `AvarnethStartup` aus der Szene löschen und die Szene speichern.
2. Den Ordner (z. B. `Assets/AVARNETH/Startup/`) löschen.
3. Optional: In *Project Settings > Player* zugewiesene Icons bzw. Splash-Einstellungen manuell zurücksetzen
   (siehe `PLAYER_SETTINGS.md`). Weitere Projekteinstellungen werden vom Paket nicht verändert.
