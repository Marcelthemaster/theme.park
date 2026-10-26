# AVARNETH: VEIL OF EMBERS – Player Settings (Icons & Splash Screen)

Gilt für Unity **6000.6.0f1**, Zielplattform Windows x64 (*PC, Mac & Linux Standalone*).
Alle Einstellungen liegen unter **Edit > Project Settings > Player**.

> [!WARNING]
> **Company Name und Product Name nicht „nebenbei“ ändern.**
> Unter Windows leiten sich daraus ab:
> - `Application.persistentDataPath` = `%USERPROFILE%\AppData\LocalLow\<Company Name>\<Product Name>`
>   (Saves, Caches, Logs, ggf. Session-Daten),
> - die PlayerPrefs-Registry-Schlüssel `HKCU\Software\<Company Name>\<Product Name>` im Player bzw.
>   `HKCU\Software\Unity\UnityEditor\<Company Name>\<Product Name>` im Editor.
>
> Eine Änderung „verschiebt“ diese Orte: bestehende Spieler verlieren scheinbar Einstellungen und lokal
> gespeicherte Daten (z. B. gemerkte Logins), Pfade in Tools/Launchern stimmen nicht mehr. Eine Umbenennung
> (z. B. des alten internen Projektnamens) nur bewusst und mit Migrationsplan durchführen. Das AVARNETH-Paket und
> sein Helper-Fenster ändern Company Name, Product Name, Identifier, Version, Scripting Backend usw. **nie**.

## 1. Icon (Windows / Standalone)

1. Reiter **PC, Mac & Linux Standalone** (Monitor-Symbol) > Abschnitt **Icon**.
2. **Override for PC, Mac & Linux Standalone** aktivieren.
3. Für jede angezeigte Größe die passende Textur aus `Importable_Assets/Icons/` zuweisen:
   `AVE_Icon_<Größe>.png`; gibt es die Größe nicht, die nächstgrößere Datei.

Welche Größen Unity verlangt, ist in der 6000.6-C#-Quelle **nicht fest codiert**: `PlayerSettings.GetIconSizes`
(`Editor/Mono/PlatformSupport/PlayerSettingsPlatformIcons.bindings.cs:513`) liefert für Standalone die Werte der
nativen Funktion `GetIconWidthsForPlatform` (`Editor/Mono/PlayerSettings.bindings.cs:810`, `extern`). Maßgeblich
sind daher die Größen, **wie sie im Inspector angezeigt werden** (das Helper-Fenster listet sie ebenfalls auf).

Zusätzlich gibt es oben in den Player Settings das **Default Icon**; es wird verwendet, wenn kein
plattformspezifischer Override gesetzt ist. Unity skaliert es auf alle benötigten Größen, daher die größte
verfügbare AVARNETH-Icon-Datei verwenden.

**Hinweis zur `.ico`-Datei:** Das Icon der gebauten `.exe` erzeugt Unity beim Build selbst aus den oben
zugewiesenen Icon-Texturen. Die mitgelieferte `03_Windows_Icons/AVARNETH.ico` ist für Desktop-Verknüpfungen, Installer und
Launcher gedacht und wird von Unity nicht verwendet.

## 2. Splash Image

Abschnitt **Splash Image** > *Splash Screen*:

- **Show Splash Screen** – zeigt den Unity-Splash-Screen vor der ersten Szene.
- **Show Unity Logo** – zeigt das „Made with Unity“-Logo im Splash-Screen.

Unser Branding-Overlay läuft danach in der bestehenden Login-Szene; es ersetzt den Unity-Splash nicht.

**Lizenzhinweis (Stand der Recherche, nicht juristisch geprüft):**
Unity hat am 12.09.2024 im Beitrag „Unity is canceling the Runtime Fee“ angekündigt, dass der Splash-Screen für
mit Unity 6 erstellte Projekte optional wird (sinngemäß: *“For projects made with Unity 6, the splash screen will
be optional.”*), zusammen mit der Anhebung der Unity-Personal-Umsatzgrenze auf 200.000 USD. Ein Unity-Support-
Artikel nennt für Unity 6 die Option, den „Made with Unity“-Splash auch unter **Unity Personal** abzuschalten oder
anzupassen; für ältere Editor-Versionen war das mit Personal nicht erlaubt.
In der 6000.6-C#-Quelle zeigt der Inspector *Show Splash Screen* ohne Lizenzprüfung an
(`Editor/Mono/Inspector/PlayerSettingsEditor/PlayerSettingsSplashScreenEditor.cs:349`); eine eventuelle Prüfung
im nativen Code ist aus der C#-Quelle nicht verifizierbar.

Quellen (in dieser Umgebung nur über Suchmaschinen-Auszüge einsehbar, die Seiten selbst waren nicht abrufbar –
vor dem Release bitte direkt prüfen und die für das eigene Abo geltenden Bedingungen lesen):

- Unity Blog, 12.09.2024: <https://unity.com/blog/unity-is-canceling-the-runtime-fee>
- Unity Pricing Updates: <https://unity.com/pricing-updates>
- Unity Support, „Made with Unity“-Splash-Screen: <https://support.unity.com/hc/en-us/articles/212165803>
- Unity Scripting API `PlayerSettings.SplashScreen.show` (6000.3): <https://docs.unity3d.com/ScriptReference/PlayerSettings.SplashScreen-show.html>
- Unity Scripting API `Application.persistentDataPath` (6000.6): <https://docs.unity.com/en-us/engine/6000.6/script-reference/unityengine/application/persistentdatapath>
- Unity Scripting API `PlayerPrefs` (2020.2): <https://docs.unity3d.com/es/2020.2/ScriptReference/PlayerPrefs.html>

## 3. Helper-Fenster: Tools > AVARNETH > Startup > Player Settings Helper...

| Aktion | Was passiert | API |
|---|---|---|
| Anzeige | aktueller Zustand von *Show Splash Screen*, *Show Unity Logo*, Standalone-Icons je Größe, Default Icon | `PlayerSettings.SplashScreen.show/showUnityLogo`, `PlayerSettings.GetIconSizes/GetIcons(NamedBuildTarget.Standalone, IconKind.Any)` |
| Assign AVARNETH Standalone Icons... | Dialog listet jede Größe „alt → neu“; erst nach Bestätigung gesetzt. Größen ohne passendes AVARNETH-Icon behalten ihr bisheriges Icon. | `PlayerSettings.SetIcons(NamedBuildTarget.Standalone, …, IconKind.Any)` |
| Assign AVARNETH Default Icon... | setzt nach Bestätigung das Default Icon auf die größte AVARNETH-Icon-Datei | `PlayerSettings.SetIcons(NamedBuildTarget.Unknown, …, IconKind.Any)` |
| Disable Unity Splash Screen... | nach Bestätigung (mit Lizenzhinweis): *Show Splash Screen* = aus, *Show Unity Logo* = aus | `PlayerSettings.SplashScreen.show/showUnityLogo` |

Das Fenster ändert **nichts** anderes: nicht Company Name, Product Name, Version, Application Identifier,
Scripting Backend, API Compatibility, Auflösung, Grafik-APIs, Logo-Liste oder Hintergrund des Splash-Screens.
Es speichert das Projekt nicht automatisch (*File > Save Project* schreibt `ProjectSettings/ProjectSettings.asset`)
und legt keinen Undo-Schritt an; Änderungen bei Bedarf manuell im Inspector zurücksetzen.
