"""Read only tracked public review metadata; candidate discovery is never classification."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path.cwd()
BASE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence'
PRIOR = BASE / 'PG19930-api-consumer-context-v1'
SLOT = ROOT.parent / 'pgpt-runs/PG379/pg19940-existing-context-preflight-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())


def paths():
    tracked = subprocess.check_output(['git', 'ls-files', 'evidence/01_PT/018_NK-OPS-001/evidence/*/review.json'], text=True).splitlines()
    result = [p for p in tracked if any(t in Path(p).parent.name for t in ['context', 'thread', 'volatile', 'monitor', 'maps']) and not Path(p).parent.name.startswith(('PG197', 'PG198', 'PG199'))]
    assert len(result) == 65
    return result


def nodes(value, pointer=()):
    if isinstance(value, dict):
        yield pointer, value
        for k, v in value.items():
            yield from nodes(v, pointer + (k,))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from nodes(v, pointer + (i,))


def compatible(row, finding):
    return row.get('path') == finding['path'] and row.get('rule') == finding['rule'] and row.get('sourceSha256', row.get('inputSha256')) == finding['sourceSha256'] and row.get('attributes') == finding['attributes']


def declares_review(manifest, digest):
    if not isinstance(manifest, dict):
        return False
    files = manifest.get('files')
    return manifest.get('reviewSha256') == digest or (isinstance(files, dict) and files.get('review.json') == digest)


def inputs():
    assert sha(PRIOR / 'manifest.json') == 'afd728733fff03c0c052382a45195343da6f0564a0324ac841cd92fcab4b8404'
    remaining = load(PRIOR / 'review.json')['remaining']
    assert len(remaining) == 801
    return remaining


def run():
    output = SLOT / 'existing-context-candidates.safe.json'
    assert SLOT.is_dir() and not output.exists()
    remaining = inputs()
    sources, candidates = [], []
    for path in paths():
        p = ROOT / path
        m = p.parent / 'manifest.json'
        manifest = load(m)
        digest = sha(p)
        declared = declares_review(manifest, digest)
        sources.append({'path': path, 'sha256': digest, 'manifestPath': str(m.relative_to(ROOT)), 'manifestSha256': sha(m), 'reviewHashDirectlyDeclared': declared})
        for pointer, row in nodes(load(p)):
            if not all(k in row for k in ['path', 'rule', 'attributes']):
                continue
            for current in remaining:
                if compatible(row, current['rawFinding']):
                    candidates.append({'rawOrdinal': current['rawOrdinal'], 'reviewPath': path, 'rowPointer': list(pointer), 'reasonPresent': isinstance(row.get('reason'), str) and bool(row['reason']), 'reviewHashDirectlyDeclared': declared, 'currentSemanticReviewRequired': True})
    value = {'driverSha256': sha(__file__), 'source': '28af318d0198fe7432ca6fcd234d3fabbfd10173', 'sources': sources, 'candidates': candidates, 'matchedObservationCount': len({r['rawOrdinal'] for r in candidates}), 'candidateOnly': True, 'newClassified': 0, 'newAcceptance': 0, 'schemaCoverage': 'Only exact path/rule/attributes/sourceSha256 orinputSha256 rows. Other schemas unassessed, no claim ofall historical proof completeness.', 'productExecuted': False}
    output.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'publicReviewsRead': len(sources), 'candidateReferences': len(candidates), 'matchedRawObservations': value['matchedObservationCount'], 'newClassified': 0}))


def post():
    source = SLOT / 'existing-context-candidates.safe.json'
    output = SLOT / 'existing-context-post.safe.json'
    assert not output.exists()
    value = load(source)
    assert value['driverSha256'] == sha(__file__) and value['newClassified'] == 0
    assert {r['path'] for r in value['sources']} == set(paths())
    remaining = {r['rawOrdinal']: r['rawFinding'] for r in inputs()}
    old = {}
    for item in value['sources']:
        p, m = ROOT / item['path'], ROOT / item['manifestPath']
        assert sha(p) == item['sha256'] and sha(m) == item['manifestSha256']
        manifest = load(m)
        assert item['reviewHashDirectlyDeclared'] == declares_review(manifest, sha(p))
        old[item['path']] = load(p)
    for candidate in value['candidates']:
        row = old[candidate['reviewPath']]
        for part in candidate['rowPointer']:
            row = row[part]
        assert compatible(row, remaining[candidate['rawOrdinal']])
        assert candidate['reasonPresent'] == (isinstance(row.get('reason'), str) and bool(row['reason']))
        assert candidate['currentSemanticReviewRequired']
    result = {'actualExit': 0, 'driverSha256': sha(__file__), 'candidateFileSha256': sha(source), 'all65PublicReviewHashesVerified': True, 'allCandidateRowsLocatedIndependently': True, 'matchedObservationCount': len({r['rawOrdinal'] for r in value['candidates']}), 'newClassified': 0, 'productExecuted': False, 'wholeHistoryCompletenessClaimed': False}
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['run', 'post']
    (run if sys.argv[1] == 'run' else post)()
