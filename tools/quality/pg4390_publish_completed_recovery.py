"""Actual original0 recovery receipt and old failures; no raw source/DB/credential export."""
import hashlib
import json
from pathlib import Path
from pg1446_current_cold_stage import W
from pg4384_half_handoff_recover import completed


def main():
    original = W / 'pg4384-half-handoff-recover-v1'
    raw = (original / 'manifest.safe.json').read_bytes(); current = json.loads(raw)
    if current['actualExit'] != 0: raise ValueError('original recovery actual0 first')
    completed(current['result'])
    out = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4390-completed-current-recovery-v1'
    out.mkdir(); files = {}
    for name, value in [('original4384.json', {**current, 'originalManifestSha256': hashlib.sha256(raw).hexdigest()}),
                        ('original4328-failure.json', json.loads((W / 'pg4316-current-failed-dispatch-v1-recover/manifest.safe.json').read_bytes())),
                        ('old-retainer-transport.json', json.loads((original / 'old-retainer-transport.safe.json').read_bytes()))]:
        path = out / name; path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    path = out / 'stages.safe.log'; path.write_bytes((original / 'stages.safe.log').read_bytes()); files[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    value = {'actualExit': 0, 'operatorCommit': 'd65ba6d7c', 'source': current['source'], 'branch': 'dev-foundation',
             'command': 'python3 -B tools/quality/pg4384_half_handoff_recover.py recover', 'originalExecSession': 25637,
             'designMain': 'd6c8b23fdcec49e6cc086a0dd435a895b2bf2ce9', 'designPR': 140,
             'files': files, 'recoveryOnlyAccepted': True, 'oldScopesNormal': False, 'oldRootNormal': False,
             'nativeQualificationPending': True, 'rawExported': False, 'formalAccepted': False, 'productionPtAdded': 0}
    path = out / 'manifest.json'; path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'manifestSha256': hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
