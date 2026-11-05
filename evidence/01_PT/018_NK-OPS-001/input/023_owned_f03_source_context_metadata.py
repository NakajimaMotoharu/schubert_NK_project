"""Metadata-only binding of individually authored F03 source decisions; no Java execution."""
from pathlib import Path
import collections
import datetime
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys

ROOT = Path.cwd()
BASE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence'
RAW = BASE / 'PG19744-current-six-main-static-repaired-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
canon = lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
load = lambda p: json.loads(Path(p).read_text())


def prior(config):
    spec = importlib.util.spec_from_file_location('normal', ROOT / 'evidence/01_PT/018_NK-OPS-001/input/014_owned_current_main_static_repaired.py')
    normal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(normal)
    normal.read_inputs()
    assert sha(RAW / 'manifest.json') == 'cef691f454c1324bf16bd01948dbc9f0ed5b2091acb7da5f5817b0a48e9f7d7b'
    rows = []
    for item in config['priorManifests']:
        p = ROOT / item['path']
        assert sha(p) == item['sha256']
        rows.extend(load(p.parent / 'review.json')['classified'])
    assert len(rows) == len({r['rawOrdinal'] for r in rows}) == config['priorCount']
    return rows


def source_inputs(config):
    contexts = []
    for item in config['sourceContexts']:
        p = ROOT / item['path']
        assert sha(p) == item['sha256']
        lines = p.read_text().splitlines()
        spans = []
        for first, last in item['ranges']:
            assert 1 <= first <= last <= len(lines)
            spans.append({'firstLine': first, 'lastLine': last, 'lines': lines[first - 1:last]})
        contexts.append(dict(item, spans=spans))
    refs = []
    for item in config['designReferences']:
        p = ROOT / item['path']
        data = subprocess.check_output(['git', 'show', 'origin/main:' + item['path']])
        assert sha(p) == hashlib.sha256(data).hexdigest() == item['sha256']
        refs.append(dict(item, text=data.decode().splitlines()[item['line'] - 1]))
    return contexts, refs


def run(config, slot, public):
    assert not slot.exists() and not public.exists()
    previous = prior(config)
    contexts, refs = source_inputs(config)
    raw = load(RAW / 'findings.json')
    rows = []
    old = {r['rawOrdinal'] for r in previous}
    paths = {c['path']: c['sha256'] for c in contexts}
    for decision in config['decisions']:
        i = decision['rawOrdinal']
        f = raw[i]
        assert i not in old and f['rule'] == decision['rule']
        assert paths[f['path']] == f['sourceSha256'] == decision['sourceSha256']
        if 'attributeValues' in decision:
            assert decision['attributeValues']
            assert all(f['attributes'][k] == v for k, v in decision['attributeValues'].items())
        else:
            assert f['attributes']['variable'] == decision['variable']
        assert int(f['attributes']['beginline']) == decision['line']
        assert decision['reason'] and decision['requiredDynamicPostconditions']
        rows.append(dict(decision, id=f'{i:06d}:' + hashlib.sha256(canon(f)).hexdigest(), rawFinding=f, classification='CONTEXTUAL_NONAPPLICABLE', actualViolation=False, runtimeProven=False, ptExempt=False, newWbsAcceptance=False))
    assert len(rows) == len({r['rawOrdinal'] for r in rows}) == config['newCount']
    selected = old | {r['rawOrdinal'] for r in rows}
    remaining = [{'rawOrdinal': i, 'id': f'{i:06d}:' + hashlib.sha256(canon(f)).hexdigest(), 'rawFinding': f, 'applicability': 'UNCLASSIFIED', 'actualViolation': None} for i, f in enumerate(raw) if i not in selected]
    assert len(remaining) == 1491 - config['priorCount'] - config['newCount']
    result = {'source': config['mainSource'], 'classified': rows, 'remaining': remaining, 'sourceContexts': contexts, 'canonicalDesignReferences': refs, 'deferred': config['deferred'], 'productExecuted': False, 'coverageMeasured': False, 'rawGateUnchanged': 1, 'actualApplicableViolations': None, 'wholeF03Accepted': False, 'whole451Accepted': False}
    slot.mkdir()
    (slot / 'review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    manifest = {'actualExit': 0, 'source': config['mainSource'], 'atJST': datetime.datetime.now().astimezone().isoformat(), 'driverSha256': sha(__file__), 'configSha256': sha(sys.argv[2]), 'reviewSha256': sha(slot / 'review.json'), 'orchestrationHead': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), 'newContext': len(rows), 'combinedReviewed': len(selected), 'remaining': len(remaining), 'productExecuted': False, 'newAcceptance': 0}
    (slot / 'manifest.safe.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'new': len(rows), 'remaining': len(remaining)}))


def post(config, slot, public):
    manifest = load(slot / 'manifest.safe.json')
    value = load(slot / 'review.json')
    assert manifest['actualExit'] == 0 and manifest['driverSha256'] == sha(__file__)
    assert manifest['configSha256'] == sha(sys.argv[2]) and manifest['reviewSha256'] == sha(slot / 'review.json')
    previous = prior(config)
    contexts, refs = source_inputs(config)
    assert value['sourceContexts'] == contexts and value['canonicalDesignReferences'] == refs
    rows = value['classified']
    expected = {r['rawOrdinal']: r for r in config['decisions']}
    assert len(rows) == len(expected) == config['newCount']
    for row in rows:
        decision = expected[row['rawOrdinal']]
        assert all(row[k] == v for k, v in decision.items())
        assert not row['ptExempt'] and not row['runtimeProven']
    allrows = previous + rows + value['remaining']
    raw = load(RAW / 'findings.json')
    indexed = {r['rawOrdinal']: r for r in allrows}
    assert len(allrows) == len(indexed) == len({r['id'] for r in allrows}) == len(raw) == 1491
    assert set(indexed) == set(range(1491))
    for i, finding in enumerate(raw):
        assert indexed[i]['rawFinding'] == finding
        assert indexed[i]['id'] == f'{i:06d}:' + hashlib.sha256(canon(finding)).hexdigest()
    counts = collections.Counter(canon(f) for f in raw)
    assert len(counts) == 1439 and sum(c == 2 for c in counts.values()) == 52 and max(counts.values()) == 2
    assert {r['rawOrdinal'] for r in config['deferred']} <= {r['rawOrdinal'] for r in value['remaining']}
    assert not public.exists()
    public.mkdir(parents=True)
    for p in slot.iterdir():
        if p.is_file():
            shutil.copyfile(p, public / p.name)
    output = dict(manifest, independentPostReconstruction=True, allOriginalOrdinalsExact=True, disjointPartition1491=True, duplicateGroupsPreserved=52, files={p.name: sha(p) for p in public.iterdir() if p.is_file()})
    (public / 'manifest.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'new': len(rows), 'combined': config['priorCount'] + len(rows), 'remaining': len(value['remaining']), 'manifestSha256': sha(public / 'manifest.json')}))


if __name__ == '__main__':
    assert len(sys.argv) == 3 and sys.argv[1] in ['run', 'post']
    config = load(sys.argv[2])
    assert config['mainSource'] == '28af318d0198fe7432ca6fcd234d3fabbfd10173'
    slot = ROOT.parent / 'pgpt-runs/PG379' / config['slot']
    public = BASE / config['publicName']
    (run if sys.argv[1] == 'run' else post)(config, slot, public)
