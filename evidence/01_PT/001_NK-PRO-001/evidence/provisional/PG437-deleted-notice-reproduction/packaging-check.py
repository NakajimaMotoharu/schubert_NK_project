"""Metadata-only Git/hash packaging oracle; no native operation or formal acceptance."""
import hashlib, json, pathlib, subprocess
root = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
tracked = set(subprocess.check_output(['git', 'ls-files'], cwd=root, text=True).splitlines())
checked = 0
for name in sorted(tracked):
    if not name.startswith('evidence/') or not name.endswith('manifest.json'):
        continue
    data = json.loads((root / name).read_text())
    files = data.get('files', [])
    if not isinstance(files, list):
        continue
    for row in files:
        path = row.get('path') if isinstance(row, dict) else None
        if not isinstance(path, str) or not path.endswith(('.log', 'artifact-oracle.txt', 'pg386-failed-unit-state.txt', '/result.txt')) and path != 'result.txt':
            continue
        parent = pathlib.Path(name).parent
        base = next((p for p in [parent, *parent.parents] if p.name == 'evidence'), parent) if 'runId' in data else parent
        candidate = path if path.startswith('evidence/') else str(base / path)
        assert candidate in tracked and (root / candidate).is_file(), candidate
        assert hashlib.sha256((root / candidate).read_bytes()).hexdigest() == row['sha256'], candidate
        checked += 1
assert checked == 237, checked
# Independent negative canary: generic .log really is ignored, .txt replacement is tracked.
probe = 'evidence/01_PT/001_NK-PRO-001/evidence/provisional/PG437-deleted-notice-reproduction'
assert subprocess.run(['git', 'check-ignore', '-q', probe + '/result.log'], cwd=root).returncode == 0
assert probe + '/result.txt' in tracked
print(json.dumps({'testId': 'PT-OPS-EVIDENCE-GIT001', 'references': checked, 'untracked': 0, 'hashMismatch': 0, 'negativeCanary': 'PASS', 'formal': False}))
