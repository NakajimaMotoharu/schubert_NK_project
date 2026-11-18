"""Classify two saved scanner candidates by exact synthetic physical-class provenance."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import subprocess

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
SCAN = E / 'PG40164-g07-resumed-public-patch-only-v1'
ORIGIN = E / 'PG40146-f02-controller-spring-jdbc-independent-v1' / 'manifest.json'
NAME = 'dev.codex.schubert.nk.api.OwnedCanary'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def ref(p):
    return dict(path=str(p), sha256=digest(Path(p).read_bytes()))


def main():
    scan = json.loads((SCAN / 'manifest.json').read_bytes())
    proof = json.loads(ORIGIN.read_bytes())
    assert scan['actualExit'] == 1 and scan['found'] == 2 and proof['productJars'] == 0
    assert {r['file'] for r in scan['candidates']} == {p['path'] for p in proof['phases']}
    rows = []
    for r in scan['candidates']:
        assert r['rule'] == 'generic-api-key'
        assert (r['startLine'], r['endLine'], r['startColumn'], r['endColumn']) == (23, 23, 9, 114)
        content = subprocess.check_output(['git', 'show', f"{r['commit']}:{r['file']}"], timeout=20)
        pin, = [p for p in proof['phases'] if p['path'] == r['file']]
        assert digest(content) == pin['sha256'] and ref(r['file']) == pin
        audit = json.loads(content)
        assert audit['productionClassesLoaded'] == 0
        line = content.splitlines()[r['startLine'] - 1]
        m = re.fullmatch(rb' {6}"dev\.codex\.schubert\.nk\.api\.OwnedCanary": "([0-9a-f]{64})"', line)
        assert m and m[1].decode() == audit['physical']['api'][NAME]
        rows.append(dict(r, resolution='Exact SHA-256 of a compile-only synthetic class',
                         className=NAME, lineSha256=digest(line), audit=pin))
    assert len({r['lineSha256'] for r in rows}) == 1
    result = dict(actualExit=0, source=scan['source'], fromCommit=scan['start'], commits=scan['commits'],
                  distinctFiles=scan['distinctFiles'], candidateCount=2, initialScannerExit=1,
                  findings=rows, confirmedSecrets=0, unresolved=0, rawScanner=ref(SCAN / 'manifest.json'),
                  uniqueStaticPost=ref(ORIGIN), scannedRangeOnly=True, scopedTextPatchesOnly=True,
                  executableOrArchiveCoverage=False, scannerRepeated=False, wholeG07Accepted=False,
                  whole451Accepted=False, newFormalAcceptance=0,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    p = SCAN / 'independent.json'
    p.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(ref(p))


if __name__ == '__main__':
    main()
