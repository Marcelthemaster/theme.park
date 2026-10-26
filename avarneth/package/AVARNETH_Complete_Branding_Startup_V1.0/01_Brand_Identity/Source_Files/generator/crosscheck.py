"""Cross-check: C# AvarnethStartupMath (via the console harness) vs. the Python reference evaluator."""
import json, subprocess, sys, os, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import timeline_eval as te

def run(json_path, fps, harness='/tmp/claude-0/unityref/mathtest'):
    dll = sorted(glob.glob(os.path.join(harness, 'bin', '**', '*.dll'), recursive=True))
    dll = [d for d in dll if os.path.basename(d).lower().startswith(('mathtest', 'avarneth'))]
    out = subprocess.run(['dotnet', dll[0], json_path, str(fps)], capture_output=True, text=True, check=True).stdout
    cs = [l for l in out.strip().split('\n') if l and not l.startswith('frame')]
    py = te.csv_rows(json.load(open(json_path)), fps)
    assert len(cs) == len(py), (len(cs), len(py))
    mism = []
    for a, b in zip(cs, py):
        A, B = a.split(','), b.split(',')
        if A[:4] != B[:4]:
            mism.append((a, b)); continue
        if A[3] == '1':
            if A[4] != B[4] or abs(int(A[5]) - int(B[5])) > 0 or abs(int(A[6]) - int(B[6])) > 0 or abs(float(A[7]) - float(B[7])) > 0.002:
                mism.append((a, b))
    return len(cs), mism, os.path.basename(dll[0])

if __name__ == '__main__':
    jp = sys.argv[1]
    for fps in (60, 144, 30):
        n, m, d = run(jp, fps)
        print(f'fps {fps}: {n} rows compared ({d}), mismatches: {len(m)}')
        for a, b in m[:8]:
            print('  C#:', a, '\n  PY:', b)
