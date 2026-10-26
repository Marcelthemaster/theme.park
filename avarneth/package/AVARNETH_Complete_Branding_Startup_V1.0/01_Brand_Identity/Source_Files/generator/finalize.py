"""Final packaging run: docs -> QA checks -> QA report -> SHA256SUMS -> ZIP -> verification.

    python3 finalize.py

Two-pass: the QA report contains the package verification of pass 1; the archive is then rebuilt with
the final report and verified again (pass 2). The pass-2 result is written next to the ZIP to
PACKAGE_VERIFICATION.txt (it cannot be inside the archive it describes).
"""
from __future__ import annotations

import datetime
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
PKG = os.path.join(ROOT, 'package', 'AVARNETH_Complete_Branding_Startup_V1.0')
WORK = os.path.join(ROOT, 'work')


def run(*args):
    print('$', ' '.join(args), flush=True)
    subprocess.run(['python3', *args], cwd=HERE, check=True)


def main():
    run('make_docs.py')
    shutil.copy2(os.path.join(WORK, 'unity_compile_evidence.md'), os.path.join(PKG, '07_Documentation', 'UNITY_COMPILE_EVIDENCE.md'))
    # copy the current generator sources into the package (Source_Files/generator)
    run('build_all.py', 'sources')
    run('qa.py', 'checks')
    run('qa_report.py')                 # pass 1 report (package section: previous verification if present)
    run('qa.py', 'package')             # sums + zip + verify (pass 1)
    run('qa_report.py')                 # report now includes the pass-1 package verification
    run('qa.py', 'package')             # final sums + zip + verify (pass 2)
    pv = json.load(open(os.path.join(WORK, 'package_verification.json')))
    lines = [f'AVARNETH_Complete_Branding_Startup_V1.0.zip - package verification ({datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")})',
             f'zip size: {pv["zip_size"]} bytes', f'zip sha256: {pv["zip_sha256"]}', '']
    for k in ('zip_test', 'complete', 'readable', 'no_zero_bytes', 'sha256_check', 'docs'):
        ok, txt = pv[k]
        lines.append(f'{"PASS" if ok else "FAIL"}  {k}: {txt}')
    with open(os.path.join(ROOT, 'package', 'PACKAGE_VERIFICATION.txt'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
