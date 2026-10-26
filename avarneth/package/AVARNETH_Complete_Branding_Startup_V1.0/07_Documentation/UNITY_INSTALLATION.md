# AVARNETH: VEIL OF EMBERS – Startup-Overlay in Unity installieren

> **Prüfstatus:** in Unity 6000.6 **NICHT getestet** – nur Compile-Check mit dem .NET-SDK gegen ältere
> Unity-Referenz-DLLs (UnityEngine 2021.3, uGUI 2020.3, UnityEditor 2021.1) plus Stub für neuere Editor-APIs
> und Signaturabgleich mit der 6000.6-C#-Quelle (siehe `README.md` und `QA_REPORT.md`). Alle Aussagen zum
> Verhalten in Unity unten beschreiben, was der Code tun **soll**, und müssen lokal geprüft werden.

Gilt für Unity **6000.6.0f1** (URP 2D, Windows x64) mit dem mitgelieferten uGUI-Paket (`com.unity.ugui`).

Das Overlay ist eine ca. 2 s lange Branding-Animation, die **über** der bereits vorhandenen, animierten
Bootstrap-/Login-Szene läuft. Es wird **keine** Szene, kein Login, kein zweiter Bootstrap, kein Netzwerk-
oder Authentifizierungs-Code angelegt oder verändert. Kein VideoPlayer, keine eigenen Shader (Standard-Material
`UI/Default`), keine Zusatz-Frameworks.

## Installation

1. Den kompletten Ordner `05_Unity_Integration` in das Projekt kopieren, z. B. nach
   `Assets/AVARNETH/Startup/`. `Importable_Assets/` (Layers/, Frames/, Particles/, Icons/,
   `Animation_Timeline.json`) muss mitkopiert werden. Der Ordner mit `Animation_Timeline.json` muss ein
   **Unterordner** von `Assets/` sein (nicht `Assets/` selbst, nicht `Packages/`), sonst verweigert das Tool die Arbeit.
2. Unity kompilieren lassen. Es entstehen die Assemblies `Eckertengineering.Avarneth.Startup` (Runtime) und
   `Eckertengineering.Avarneth.Startup.Editor` (nur Editor). Die Konsole muss fehlerfrei sein.
3. **Tools > AVARNETH > Startup > Configure Sprite Import Settings**
   Zeigt zuerst einen Bestätigungsdialog (Ordner + Anzahl der zu ändernden Dateien); erst nach *Apply* wird etwas
   geändert. Betroffen sind **nur** die Vertragsdateien: `AVE_*.png` direkt in `Layers/`, `Frames/`, `Particles/`
   (plus die in `Animation_Timeline.json` genannten PNGs) und `Icons/AVE_Icon_<Größe>.png`. Unterordner und
   andere Dateien werden nicht angefasst.
   Sprites: Sprite (2D and UI), Single, Point, keine Mipmaps, Compression None, Clamp, Non-Power of 2 = None,
   sRGB an, Alpha Is Transparency an, 100 PPU, Full Rect, Max Size ≥ 2048. **Ausnahme:** Sprites von
   Vollbild-Ebenen (`"fullscreen": true` in der Timeline, aktuell nur `Layers/AVE_Veil.png`) erhalten
   **Bilinear**, weil sie als weicher Verlauf über den ganzen Bildschirm gestreckt werden. Icons: Default, Point,
   keine Mipmaps, Compression None, Non-Power of 2 = None. Ein Standalone-Override wird entfernt.
   Import-Einstellungen lassen sich nicht mit *Edit > Undo* zurücknehmen.
4. **Tools > AVARNETH > Startup > Create or Update Startup Prefab**
   Erzeugt `<Zielordner>/Prefabs/AvarnethStartup.prefab` (hier `Assets/AVARNETH/Startup/Prefabs/`).
   Fehlt ein Sprite oder ist die Timeline ungültig, bricht das Tool mit Dialog ab und schreibt nichts.
   Ein erneuter Aufruf aktualisiert das vorhandene Prefab an Ort und Stelle (Root und Komponenten behalten ihre
   IDs); Szenen-Overrides wie die zugewiesene Login-CanvasGroup sollen dadurch erhalten bleiben.
   Das Prefab wird **neutral** gespeichert (alle Bilder und der Raycast-Blocker aus): im Edit Mode ist darum
   nichts zu sehen, sichtbar wird das Overlay erst mit `Play()`.
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
richtige Timeline mit *Use* wählen (wird pro Projekt in den EditorPrefs gespeichert). Heißt der gefundene
Ordner nicht `Importable_Assets`, warnen das Installer-Fenster und *Validate Installation*.

Dialoge bleiben kurz: Unity 6000.6 kürzt Dialogtexte über 512 Zeichen selbst. Lange Listen (fehlende Sprites,
Import-Probleme, Warnungen) zeigt der Dialog daher nur als Auszug („… and N more (see Console)“); der
vollständige Bericht steht immer in der Konsole.

## Aufbau des Prefabs

```
AvarnethStartup   Canvas (Screen Space - Overlay, Sort Order 1000), CanvasScaler (Constant Pixel Size, 1, 100 PPU),
                  GraphicRaycaster, Image (transparent, Raycast-Blocker, nur während des Abspielens an),
                  AvarnethStartupAnimation
  Backdrop        über den ganzen Bildschirm gestreckt (Anker 0..1), vor dem ArtRoot
    veil          Vollbild-Ebene (AVE_Veil, Bilinear), nur Alpha animiert
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
| Scale Mode | IntegerNearest | `round(Screen.height/270)`, verkleinert bis die Content Bounds passen, min. 1; `IntegerFloor`; `Continuous` (ohne Ganzzahl) |
| Completion Action | DisableGameObject | alternativ `DestroyGameObject` |
| Block Input While Playing | an | transparentes Vollbild-Image blockt Klicks |
| Skip On Click | aus | Klick überspringt (über `IPointerClickHandler`, keine Input-Manager-/Input-System-API). Benötigt zur Laufzeit ein EventSystem mit dem zur *Active Input Handling* passenden Input-Modul (`StandaloneInputModule` bzw. `InputSystemUIInputModule`); das Paket prüft oder erzeugt keines. |
| Login Canvas Group | leer | `interactable`/`blocksRaycasts` während des Overlays aus. Am Ende, in `OnDisable` und `OnDestroy` wird zurückgesetzt, was das Overlay geändert hat; hat der Login-Code einen Wert inzwischen selbst eingeschaltet, bleibt dieser erhalten. |
| Reveal Login During Fade Out | aus | Login-Alpha zuerst 0, in den letzten *Reveal Seconds* (0,4 s) auf den Originalwert. Nur in diesem Modus schreibt (und restauriert) das Overlay `alpha`; ohne Reveal bleibt `alpha` unberührt. |
| On Completed | – | UnityEvent, genau einmal pro Durchlauf |

Integer-Skalierung (`IntegerNearest`) für die **Content Bounds der mitgelieferten Timeline**
(`contentBounds` 126, 47, 227 × 168 Art-px; berechnet mit `AvarnethStartupMath.ComputePixelScale`):
1920×1080 → 4, 2560×1440 → 5, 3840×2160 → 8, 1600×900 → 3, 1366×768 → 3, 1280×720 → 3, 1680×1050 → 4.
Der Faktor wird nur verkleinert, solange die Content Bounds den Bildschirm verlassen würden; Teile des
480 × 270-Canvas außerhalb der Content Bounds dürfen daher abgeschnitten werden (z. B. 1280×720: Canvas
1440 × 810 px). Ändert die Art-Pipeline `contentBounds`, ändern sich auch diese Werte.

Script-API: `Play()`, `Skip()`, `IsPlaying`, `IsFinished`, `event Action Completed`, `OnCompleted`.

```csharp
overlay.Completed += () => Debug.Log("Startup overlay done");
```

Verhalten laut Code (nicht in Unity getestet):

- Das Overlay wartet auf nichts, simuliert keinen Ladezustand und verzögert keine Login-Logik. Nach dem Ende
  deaktiviert sich die Komponente (kein `Update` mehr) und das GameObject wird deaktiviert bzw. zerstört.
- Bis `Play()` läuft, und immer wenn die Komponente deaktiviert wird, ist nichts sichtbar und keine Eingabe
  blockiert (auch wenn die Komponente schon vor `Start()` ausgeschaltet ist). Zum Abbrechen trotzdem `Skip()`
  verwenden: nur dann werden das Ende gemeldet und die Completion Action ausgeführt.
- `Play()` bei inaktivem Eltern-Objekt: Fehlermeldung in der Konsole, das Overlay endet sofort (Completion
  wird ausgelöst), die Login-CanvasGroup wird nicht gesperrt.

**Login-CanvasGroup:** Eine CanvasGroup verwenden, die der Login-Code nicht selbst umschaltet (bei Bedarf eine
eigene CanvasGroup auf das Login-Root-Objekt legen). CanvasGroups wirken verschachtelt, eine zusätzliche Gruppe
ist daher unschädlich.

## Abdunklung (`AVE_Veil`) als Vollbild-Ebene

`AVE_Veil` ist in der Timeline als `"fullscreen": true` markiert. Sie liegt deshalb nicht im pixelskalierten
ArtRoot, sondern im gestreckten `Backdrop` und deckt jede Bildschirmgröße vollständig ab – auch Auflösungen,
die kein ganzzahliges Vielfaches von 480 × 270 sind (z. B. 2560×1440, 1920×1200, 2560×1080, 3440×1440).
Ihr Verlauf ist bewusst weich (Bilinear-Filter), die äußerste Pixelreihe hat einen konstanten Alpha-Wert, damit
der Clamp-Rand unsichtbar bleibt. Alle anderen Ebenen bleiben pixelgenau auf dem Art-Raster.

## Fehlerbehebung

| Symptom | Ursache / Lösung |
|---|---|
| „No TextAsset named 'Animation_Timeline' …“ | `Importable_Assets/Animation_Timeline.json` fehlt oder `schema` ≠ `avarneth.startup.timeline/1`. |
| „… only found in an unusable folder“ | Die Timeline liegt direkt in `Assets/` oder außerhalb von `Assets/`; Ordner in einen Unterordner verschieben (Schritt 1). |
| „Several AVARNETH timelines were found“ | Im *Installer...*-Fenster die gewünschte Timeline mit *Use* wählen. |
| „sprite(s) are missing … not imported as Sprite“ | Schritt 3 ausführen, danach Schritt 4 wiederholen. Nicht konfigurierte Dateien heißen nicht `AVE_*.png` oder liegen in einem Unterordner. |
| Dialog zeigt nur einen Teil („… more (see Console)“) | Vollständige Liste in der Konsole. |
| Pixel unscharf / ungleich breit | Import Settings prüfen (*Validate Installation*), Scale Mode `IntegerNearest`, Game-View-Scale 1x. |
| Overlay liegt hinter dem Login | Sort Order des Canvas auf `AvarnethStartup` erhöhen (Standard 1000). |
| Klick überspringt nicht | *Skip On Click* aktivieren; zur Laufzeit muss ein EventSystem mit passendem Input-Modul existieren. |
| Konsole: „[AVARNETH Startup] … The overlay is skipped.“ | Referenzen im Prefab fehlen oder `Play()` wurde bei inaktivem Eltern-Objekt aufgerufen. Schritt 4 wiederholen bzw. Hierarchie prüfen. Das Overlay beendet sich sofort, der Login bleibt bedienbar. |
| Login bleibt gesperrt | Prüfen, ob der Login-Code dieselbe CanvasGroup umschaltet (siehe oben). |
| Unabgedunkelte Ränder während des Overlays | Prefab mit *Create or Update Startup Prefab* neu erzeugen (ältere Prefabs ohne `Backdrop`); *Validate Installation* prüft den Bilinear-Import von `AVE_Veil`. |

## Entfernen

1. Das GameObject `AvarnethStartup` aus der Szene löschen und die Szene speichern.
2. Den Ordner (z. B. `Assets/AVARNETH/Startup/`) löschen.
3. Optional: In *Project Settings > Player* zugewiesene Icons bzw. Splash-Einstellungen manuell zurücksetzen
   (siehe `PLAYER_SETTINGS.md`). Weitere Projekteinstellungen werden vom Paket nicht verändert.
