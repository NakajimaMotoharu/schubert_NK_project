"""Publish only twenty-six source-bound technical assessments, no runtime or raw session."""
import hashlib
import json
import shlex
from lan_server import run
from pg3928_current_boundary_full_six import ROOT, W, SOURCE, require


def main():
    p = W / 'pg3946-jdbc-finally-review-v1/manifest.safe.json'; original = json.loads(p.read_bytes()); v = original['result']
    require(original['actualExit'] == v['actualExit'] == 0 and v['productionSource'] == SOURCE and (v['newTechnicalAssessments'], v['technicalDispositions'], v['unclassified']) == (26, 304, 1536), 'genuine exact assessment')
    code = """import hashlib,json
from pathlib import Path
p=Path('/home/mini/schubert-nk-pgpt/runs/PG3946-jdbc-finally-review-v1/assessed28.safe.json');assert hashlib.sha256(p.read_bytes()).hexdigest()==EXPECTED;print(p.read_text())
"""
    status, output = run('python3 -c ' + shlex.quote('EXPECTED=' + repr(v['assessedSha256']) + '\n' + code), timeout=30)
    require(status == 0, 'exact original safe assessments')
    rows = json.loads(next(line for line in output.splitlines() if line.startswith('[')))
    require(len(rows) == 26 and len({r['id'] for r in rows}) == 26 and all(r['qualityGatePass'] is False and r['rawWarningRemoved'] is False for r in rows), 'no gate promotion or duplicate')
    require(all(hashlib.sha256((ROOT / r['path']).read_bytes()).hexdigest() == r['sourceSha256'] for r in rows), 'all current source bytes identical')
    out = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3948-jdbc-finally-assessment-v1'; out.mkdir()
    raw = (json.dumps(rows, sort_keys=True) + '\n').encode(); (out / 'assessed26.json').write_bytes(raw)
    value = {'actualExit': 0, 'productionSource': SOURCE, 'run': 'PG3948-jdbc-finally-assessment-v1', 'technicalAssessment': v,
             'originalLocalReceiptSha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'files': {'assessed26.json': hashlib.sha256(raw).hexdigest()},
             'unsupportedFinallyFindingsRemainUnclassified': 26, 'explicitIOExceptionPrimaryUnclassified': ['PMD-7fff-1162', 'PMD-7fff-1167'],
             'F03Accepted': False, 'formalAccepted': False, 'newPT': 0, 'newVmOperations': 0, 'suppressionAdded': False,
             'failedUnqualifiedRunsPreserved': ['PG3940 annotated-type false-negative', 'PG3942 inspect before SSH', 'PG3944 braceless/IOException shape not yet supported']}
    serialized = (json.dumps(value, sort_keys=True) + '\n').encode(); (out / 'manifest.json').write_bytes(serialized)
    print(json.dumps({'actualExit': 0, 'manifestSha256': hashlib.sha256(serialized).hexdigest(), 'technicalDispositions': 304, 'unclassified': 1536, 'F03Accepted': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
