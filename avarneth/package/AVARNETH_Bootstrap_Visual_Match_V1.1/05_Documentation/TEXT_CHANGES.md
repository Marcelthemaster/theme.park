# Sichtbare Texte, die lokal angepasst werden müssen

Quelle: `Existing_Previews/Unity_Capture/Login.png` und die 20-s-Capture. Die Herkunft der Strings (Szene `Bootstrap.unity`,
Login-Skripte, Lokalisierung) ist im Referenzpaket **nicht enthalten**. Codex sucht im Projekt nach
`World of Eckertengineering`, `WOE-Nakama`, `Willkommen in`, `Private Entwicklungswelt`.
Die Vorschläge sind im Mockup-Video zu sehen und müssen vom Projektinhaber freigegeben werden.

| # | Objekt (Hierarchie laut Referenz-JSON) | Aktuell sichtbar | Vorschlag V1.1 | Hinweis |
|---|---|---|---|---|
| 1 | `LoginScreen/LogoAreaTopLeft/LogoText` | „World of“ / „Eckertengineering“ | – (Objekt deaktivieren) | ersetzt durch Header-Bild, siehe CODEX_INTEGRATION B |
| 2 | `LoginScreen/BreakingNewsPanelLeft/NewsBody` (Zeile 1) | „Willkommen in World of Eckertengineering.“ | „Willkommen in AVARNETH: Veil of Embers.“ | |
| 3 | `LoginScreen/BreakingNewsPanelLeft/NewsBody` (Zeilen 2–3) | „Login, Charakterverwaltung und Welteintritt werden weiterhin über den WOE-Nakama-Server ausgeführt.“ | „Login, Charakterverwaltung und Welteintritt werden weiterhin über den bestehenden Nakama-Server ausgeführt.“ | nur Anzeigetext; Server, Keys, IDs bleiben unverändert |
| 4 | `LoginScreen/BottomCenterCopyright` | „© World of Eckertengineering · Private Entwicklungswelt ™“ | „© Eckertengineering · AVARNETH: Veil of Embers“ | ™ entfernt, weil kein Markenrecht bekannt. Ob ™ wieder aufgenommen wird, entscheidet der Inhaber. Breite ≤ 408 px eingehalten (15 pt). |
| 5 | `LoginScreen/LogoAreaTopLeft/SubtitleText` | „PRIVATE ENTWICKLUNGSWELT“ | unverändert | enthält keinen WOE-Namen |
| 6 | `LoginScreen/BottomRightVersion` | „Alpha Version 0.1“ | unverändert | |
| 7 | FPS-Anzeige oben rechts („12 FPS“) | Zähler aus der Capture | unverändert | nicht Teil der Login-Hierarchie im Referenz-JSON |

Nicht sichtbar im Login, aber zu prüfen (nicht geändert): Fenstertitel/Product Name in den PlayerSettings (siehe V1.0
`PLAYER_SETTINGS.md`, keine blinde Änderung). Interne Namen (Namespaces `Woe…`, Nakama-IDs, Ordner) bleiben **WOE**.
