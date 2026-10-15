"""Collect exact finite static diagnostics, not a PASS or new Production PT."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

import lan_server

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg3388-static-diagnostics-v1')
PUBLIC = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3388-static-diagnostics'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    os.umask(0o077); PRIVATE.mkdir(mode=0o700); PUBLIC.mkdir()
    remote = """python3 - <<'REMOTE'
from pathlib import Path
import json,hashlib
b=Path('/home/mini/schubert-nk-pgpt/runs/PG3382-static-gate-v1/result')
a=Path('/home/mini/schubert-nk-pgpt/runs/PG3386-pmd-record-after-v1/result')
v=json.loads((b/'manifest.safe.json').read_bytes());w=json.loads((a/'manifest.safe.json').read_bytes())
print(json.dumps({'before':v,'after':w,'beforeManifestSha256':hashlib.sha256((b/'manifest.safe.json').read_bytes()).hexdigest(),'afterManifestSha256':hashlib.sha256((a/'manifest.safe.json').read_bytes()).hexdigest()}))
REMOTE"""
    rc, raw = lan_server.run(remote, timeout=30)
    assert rc == 0
    proof = json.loads(raw.strip())
    with (PRIVATE / 'server.safe.json').open('x') as f:
        json.dump(proof, f, indent=2)
    before, after = proof['before'], proof['after']
    assert before['sourceFiles'] == after['sourceFiles'] == 849
    assert before['auxMainClasses'] == after['auxMainClasses'] == 1643
    assert before['pmd']['processingErrors'] == 1 and after['processingErrors'] == 0
    assert before['pmd']['violations'] == after['violations'] == 2220 and after['exactOriginalFindingsRetained'] is True
    paths = [ROOT / p for p in before['sourceSha256']]
    assert {str(p.relative_to(ROOT)): digest(p) for p in paths} == before['sourceSha256']
    for path in paths:
        frozen = subprocess.check_output(['git', 'show', after['productionSource'] + ':' + str(path.relative_to(ROOT))], cwd=ROOT)
        assert hashlib.sha256(frozen).hexdigest() == digest(path)
    canary_dir = PRIVATE.parent / 'pg3384-static-canaries-v3-after'
    canary = json.loads((canary_dir / 'manifest.safe.json').read_bytes())
    assert canary['actualExit'] == 0 and canary['recordErrorFixed'] is True
    value = {'run': 'PG3388-static-diagnostics', 'productionSource': after['productionSource'],
             'collectionActualExit': 0, 'mainMutated': False, 'sourceJavaFiles': 849, 'auxMainClasses': 1643,
             'sourceAllEqualA9': True, 'sourceSha256': before['sourceSha256'],
             'startUTC': before['startUTC'], 'endUTC': before['endUTC'],
             'pmdBefore': {k: before['pmd'][k] for k in ['exit', 'violations', 'processingErrors', 'ruleCounts']},
             'pmdAfter': after, 'checkstyle': {k: before['checkstyle'][k] for k in ['exit', 'violations', 'ruleCounts']},
             'toolSha256': before['pinnedToolSha256'], 'ruleSha256': before['ruleSha256'],
             'reportsSha256': before['reportsSha256'], 'beforeManifestSha256': proof['beforeManifestSha256'],
             'afterManifestSha256': proof['afterManifestSha256'], 'independentCanaries': canary,
             'canaryManifestSha256': digest(canary_dir / 'manifest.safe.json'),
             'privateRawLocations': ['aru:runs/PG3382-static-gate-v1/result', 'aru:runs/PG3386-pmd-record-after-v1/result', str(canary_dir)],
             'BUG1298Scope': 'Processing error fixed, all849 exact input and original2220 findings retained; not full static gate closure',
             'F03Accepted': False, 'staticGatePass': False, 'acceptedDelta': 0,
             'newProductionPtCredit': 0, 'formalUpdated': False, 'effortCompletionRate': None}
    with (PUBLIC / 'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
    print(json.dumps({'actualExit': 0, 'path': str(PUBLIC.relative_to(ROOT)), 'manifestSha256': digest(PUBLIC / 'manifest.json'),
                      'sourceFiles': 849, 'rawPmdOpen': 2220, 'rawCheckstyleOpen': 645, 'F03Accepted': False}))


if __name__ == '__main__':
    main()
