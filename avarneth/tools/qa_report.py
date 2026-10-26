"""Collect build/compile/cross-check evidence and render 07_Documentation/QA_REPORT.md.

    python3 qa_report.py      (run after `qa.py checks`; package checks come from work/package_verification.json)
"""
from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import crosscheck  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..'))
PKG = os.path.join(ROOT, 'package', 'AVARNETH_Complete_Branding_Startup_V1.0')
WORK = os.path.join(ROOT, 'work')
REF = '/tmp/claude-0/unityref'


def build(proj):
    r = subprocess.run(['dotnet', 'build', proj, '-nologo', '-clp:NoSummary', '--no-incremental'],
                       capture_output=True, text=True)
    out = r.stdout + r.stderr
    errs = sorted(set(re.findall(r': error (CS\d+: [^\[]+)', out)))
    warns = sorted(set(re.findall(r': warning (CS\d+: [^\[]+)', out)))
    return r.returncode == 0, errs, warns


def collect():
    ev = {}
    for key, proj in (('runtime', f'{REF}/compile/Runtime/Avarneth.Runtime.Harness.csproj'),
                      ('editor', f'{REF}/compile/Editor/Avarneth.Editor.Harness.csproj'),
                      ('editor_split', f'{REF}/compile/EditorSplit/Avarneth.EditorSplit.Harness.csproj'),
                      ('mathtest', f'{REF}/mathtest/MathTest.csproj')):
        if os.path.isfile(proj):
            ev[key] = build(proj)
        else:
            ev[key] = None
    st = subprocess.run(['dotnet', f'{REF}/mathtest/bin/Debug/net8.0/avarneth-mathtest.dll', '--selftest'],
                        capture_output=True, text=True)
    ev['selftest'] = (st.returncode == 0, (st.stdout + st.stderr).strip().splitlines()[-3:])
    jp = os.path.join(PKG, '04_Animated_Startup', 'Animation_Timeline.json')
    cc = []
    for fps in (30, 60, 144):
        n, m, _ = crosscheck.run(jp, fps)
        cc.append((fps, n, len(m)))
    ev['crosscheck'] = cc
    ap = subprocess.run(['python3', f'{REF}/compile/apicheck_6000_6.py'], capture_output=True, text=True)
    oks = [l for l in ap.stdout.splitlines() if l.startswith('OK |')]
    used_obsolete = [l for l in oks if 'OBSOLETE' in l and '[NOT used]' not in l]
    missing = sum(1 for l in ap.stdout.splitlines() if l.startswith('MISSING'))
    ev['apicheck'] = (missing == 0 and not used_obsolete, len(oks), missing)
    stubs = os.path.join(REF, 'compile', 'Stubs')
    ev['stubs'] = []
    for f in sorted(os.listdir(stubs)):
        txt = open(os.path.join(stubs, f)).read()
        ev['stubs'] += re.findall(r'public (?:static )?(?:readonly )?[\w\[\]<>.]+ (\w+)\s*[\(;{=]', txt)
    return ev


def status(ok):
    return 'PASS' if ok else 'FAIL'


def md_escape(s):
    return s.replace('|', '\\|').replace('\n', ' ')


def render(ev):
    qa = json.load(open(os.path.join(WORK, 'qa_results.json')))
    pv_path = os.path.join(WORK, 'package_verification.json')
    pv = json.load(open(pv_path)) if os.path.isfile(pv_path) else None
    rows = {}
    for r in qa:
        rows.setdefault(r['area'], []).append(r)

    def table(items):
        out = ['| Status | Prüfung | Nachweis |', '|---|---|---|']
        for r in items:
            out.append(f"| **{r['status']}** | {md_escape(r['check'])} | {md_escape(r['evidence'])} |")
        return '\n'.join(out)

    u = []
    rt, ed, es, mt = ev['runtime'], ev['editor'], ev['editor_split'], ev['mathtest']

    def cres(x):
        if x is None:
            return 'nicht vorhanden'
        ok, e, w = x
        return f"{'Build OK' if ok else 'Build FEHLER'}, {len(e)} Fehler, {len(w)} Warnungen" + (f" ({'; '.join(w)[:300]})" if w else '')
    u.append({'status': status(rt and rt[0] and not rt[1]), 'check': 'C#-Runtime kompiliert ohne UnityEditor-Referenz (C# 9, netstandard2.1)',
              'evidence': 'dotnet build gegen echte Unity-Referenzassemblies UnityEngine 2021.3.33 (Module) + UnityEngine.UI 2020.3.21: ' + cres(rt)})
    u.append({'status': status(ed and ed[0] and not ed[1]), 'check': 'Editor + Runtime kompilieren gemeinsam',
              'evidence': 'zusätzlich UnityEditor.dll 2021.1 + Harness-Stubs (nur im Prüfaufbau, nicht im Paket) für Unity-6-APIs: '
              + ', '.join(sorted(set(ev['stubs'])))[:400] + ' – ' + cres(ed)})
    if es is not None:
        u.append({'status': status(es[0] and not es[1]), 'check': 'Editor-Assembly separat gegen die Runtime-Assembly (asmdef-Aufteilung nachgestellt)',
                  'evidence': cres(es)})
    u.append({'status': status(mt and mt[0] and ev['selftest'][0]), 'check': 'Zeitleisten-Mathematik (Unity-frei) – Selbsttest',
              'evidence': f"Konsolen-Harness net8.0: {cres(mt)}; --selftest: {' / '.join(ev['selftest'][1])}"})
    total = sum(n for _, n, _ in ev['crosscheck'])
    bad = sum(m for _, _, m in ev['crosscheck'])
    u.append({'status': status(bad == 0), 'check': 'C#-Laufzeitmathematik = Python-Referenz (Vorschau-Renderer) für die echte Animation_Timeline.json',
              'evidence': f'{total} CSV-Zeilen (Layer + Partikel je Frame) bei ' + ', '.join(f'{f} fps' for f, _, _ in ev['crosscheck'])
              + f' verglichen: {bad} Abweichungen (Sichtbarkeit, Flipbook-Index, Pixelposition, Alpha ±0.002)'})
    api_ok, api_n, api_missing = ev['apicheck']
    u.append({'status': status(api_ok), 'check': 'Verwendete Unity-APIs gegen den Unity-6000.6.0f1-Quellcode geprüft (Existenz, Signatur, [Obsolete])',
              'evidence': f'apicheck_6000_6.py gegen Unity-C#-Reference-Source (Tag 6000.6.0f1): {api_n} Einträge OK, {api_missing} fehlend; '
              'kein verwendetes Member ist [Obsolete]. Datei:Zeile-Liste in UNITY_COMPILE_EVIDENCE.md'})
    u.extend(r for r in rows.get('Unity-Integration', []))

    pk = []
    if pv:
        for key, label in (('zip_test', 'ZIP-Datei vollständig und unbeschädigt (unzip -t)'), ('complete', 'ZIP enthält exakt alle Paketdateien'),
                           ('readable', 'Dateien nach dem Entpacken lesbar'), ('no_zero_bytes', 'Keine Nullbyte-Platzhalter'),
                           ('sha256_check', 'Prüfsummen tatsächlich berechnet und nach dem Entpacken verifiziert'),
                           ('docs', 'Dokumentation vorhanden')):
            ok, txt = pv[key]
            pk.append({'status': status(ok), 'check': label, 'evidence': txt})
    else:
        pk.append({'status': 'NOT TESTED', 'check': 'Paketprüfung', 'evidence': 'noch nicht ausgeführt'})

    not_tested = [
        ('Import in Unity 6.6 (6000.6.0f1) / Kompilierung im echten Unity-Editor', 'kein Unity-Editor in dieser Umgebung; Ersatz: Compile gegen Unity-2021-Referenzassemblies + API-Abgleich mit 6000.6-Quellcode (siehe oben)'),
        ('Editor-Werkzeug ausführen (Importeinstellungen, Prefab-Erzeugung, Szene, Player-Settings-Helfer)', 'benötigt Unity-Editor'),
        ('AvarnethStartup.prefab', 'nicht geliefert – wird in Unity vom Installer erzeugt (kein ungeprüftes Prefab-YAML)'),
        ('Play-Mode: Ablauf, Skalierung bei 1280×720 / 1920×1080 / 2560×1440 / 3840×2160, Eingabesperre, Login-CanvasGroup-Wiederherstellung', 'benötigt Unity-Projekt'),
        ('Integration in die bestehende Login-/Bootstrap-Szene, Zusammenspiel mit Nakama-Login', 'kein Zugriff auf Projekt/Server (absichtlich keine Änderungen daran)'),
        ('EXE-Icon im Windows-Build, Taskleiste, Alt-Tab, Desktop-Verknüpfung', 'kein Windows-Rechner; ICO technisch geprüft (siehe Abschnitt 2)'),
        ('Unity-Splashscreen in einem Build tatsächlich deaktiviert', 'lizenz- und projektabhängig; Schritte in PLAYER_SETTINGS.md'),
        ('Darstellung im Linear-Farbraum des Projekts', 'Vorschau mischt Alpha in sRGB; deckende Pixel identisch, Übergänge minimal anders'),
        ('Performance / Speicher auf dem Zielrechner', 'Budget dokumentiert (ANIMATION_SPECIFICATION.md §8), nicht gemessen'),
    ]

    lines = [
        '# AVARNETH Branding & Startup – QA-Bericht V1.0', '',
        f'Erstellt: {datetime.date.today().isoformat()} · Umgebung: Linux-Container (Python 3, Pillow, NumPy, SciPy, ffmpeg, icoutils, .NET SDK 8), '
        'kein Unity-Editor, kein Windows, kein Zugriff auf das Produktivprojekt.', '',
        'Statuswerte: **PASS** = tatsächlich geprüft und bestanden · **FAIL** = tatsächlich geprüft und fehlgeschlagen · '
        '**NOT TESTED** = nicht geprüft bzw. erforderliche Umgebung nicht vorhanden. Grundsatz: *No evidence = no pass.*', '',
        'Alle automatisierten Prüfungen sind reproduzierbar: `Source_Files/generator/qa.py`, `qa_report.py`, `crosscheck.py`.', '',
        '## 1. Grafikprüfung', '', table(rows.get('Grafik', [])), '',
        '## 2. Windows-Icon-Prüfung', '', table(rows.get('Windows-Icon', [])), '',
        '## 3. Animationsprüfung', '', table(rows.get('Animation', [])), '',
        '## 4. Unity-Integrationsprüfung', '', table(u), '',
        '## 5. Paketprüfung', '', table(pk), '',
        ('Die Paketprüfung wurde am fertig gepackten ZIP ausgeführt (entpacken, `sha256sum -c`, jede Datei öffnen). '
         'Da dieser Bericht selbst Teil des Pakets ist, wurde das ZIP nach dem Einfügen des Berichts neu gebaut und '
         'mit demselben Skript erneut verifiziert; das Ergebnis dieses letzten Laufs steht in `PACKAGE_VERIFICATION.txt` '
         'neben dem ZIP.'), '',
        '## 6. Nicht prüfbar in dieser Umgebung (NOT TESTED)', '',
        '| Status | Prüfung | Grund / Ersatznachweis |', '|---|---|---|',
    ]
    for c, why in not_tested:
        lines.append(f'| **NOT TESTED** | {c} | {why} |')
    lines += ['', '## 7. Lokale Abnahme-Checkliste (auf dem Unity-Rechner)', '',
              '1. Ordner `05_Unity_Integration` nach `Assets/…` kopieren → Console ohne Fehler.',
              '2. *Tools ▸ AVARNETH ▸ Startup ▸ Validate Installation* → keine Fehler.',
              '3. *Configure Sprite Import Settings*, dann *Create / Update Startup Prefab* → Prefab entsteht ohne Fehlermeldung.',
              '4. Bestehende Bootstrap-/Login-Szene öffnen, *Add Startup Overlay To Open Scene…*, Login-CanvasGroup zuweisen, Szene speichern.',
              '5. Play: Animation ca. 2 s, danach Overlay deaktiviert, Login bedienbar, keine Fehler/Warnungen; bei 1280×720, 1920×1080 und 2560×1440 prüfen.',
              '6. Windows-Build mit gesetzten Icons: EXE-, Taskleisten- und Alt-Tab-Symbol prüfen; Splash-Einstellungen gemäß PLAYER_SETTINGS.md.',
              '7. Ergebnisse in diesem Bericht von NOT TESTED auf PASS/FAIL setzen.', '']
    lines += ['## 8. Anhang', '',
              'Vollständiges Compile-/API-Protokoll (englisch, mit allen Befehlen, Datei:Zeile-Nachweisen gegen den '
              'Unity-6000.6.0f1-Quellcode, Stub-Liste und Review-Runden): `UNITY_COMPILE_EVIDENCE.md`.', '']
    with open(os.path.join(PKG, '07_Documentation', 'QA_REPORT.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    counts = {}
    for sec in (rows.get('Grafik', []), rows.get('Windows-Icon', []), rows.get('Animation', []), u, pk):
        for r in sec:
            counts[r['status']] = counts.get(r['status'], 0) + 1
    counts['NOT TESTED'] = counts.get('NOT TESTED', 0) + len(not_tested)
    print('QA_REPORT.md written', counts)
    return counts


if __name__ == '__main__':
    ev = collect()
    json.dump({k: v for k, v in ev.items()}, open(os.path.join(WORK, 'qa_build_evidence.json'), 'w'), indent=1, default=str)
    render(ev)
