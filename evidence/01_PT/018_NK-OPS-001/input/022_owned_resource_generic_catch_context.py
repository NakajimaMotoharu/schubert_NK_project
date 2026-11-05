"""Finite source review of twenty generic catches; never loads or calls Java."""
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
SLOT = ROOT.parent / 'pgpt-runs/PG379/pg19840-resource-generic-catch-context-v1'
PUBLIC = BASE / 'PG19840-resource-generic-catch-context-v1'
PRIOR = [
    ('PG19752-f03-finite-source-context-corrected-v1', 'd4d8274a68727f8bb278ff89140b8778fa5293011263f4e75c8d195e8fe4cf14'),
    ('PG19760-f03-identity-context-v1', '40e501ddd751e8e7849721e7a063d69062d49ad3ba0e1e3429c345b5245723bf'),
    ('PG19770-f03-map-monitor-context-v1', '6a272d4a9ecad5c26ee13e3af9765f766f9fcd2936ec1e0b39bf030a8778bae4'),
    ('PG19830-resource-type-context-v1', '6c3055b08e58ec40e023bbf70dd56d667dc1ea50357e1c3d1703aee00534e8a5'),
]
CASES = {
    'ConfigurationGroupResolver.java': [('scope', 103, 121, 107, 110, [751, 752, 753, 754])],
    'ProcessResourceScope.java': [
        ('acquire', 33, 62, 44, 48, [833, 834, 835, 836]),
        ('use', 65, 85, 68, 71, [848, 849, 850, 851]),
    ],
    'ResourceScope.java': [
        ('acquire', 69, 102, 82, 86, [1208, 1209, 1210, 1211]),
        ('use', 104, 130, 112, 115, [1217, 1218, 1219, 1220]),
    ],
}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
canon = lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
load = lambda p: json.loads(Path(p).read_text())


def prerequisites():
    assert sha(RAW / 'manifest.json') == 'cef691f454c1324bf16bd01948dbc9f0ed5b2091acb7da5f5817b0a48e9f7d7b'
    spec = importlib.util.spec_from_file_location('current_inputs', ROOT / 'evidence/01_PT/018_NK-OPS-001/input/014_owned_current_main_static_repaired.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.read_inputs()  # Hash/metadata checks only, not that tool's run/post.
    previous = []
    for name, digest in PRIOR:
        assert sha(BASE / name / 'manifest.json') == digest
        previous.extend(load(BASE / name / 'review.json')['classified'])
    assert len(previous) == len({r['rawOrdinal'] for r in previous}) == 307
    return previous


def inspect():
    previous = prerequisites()
    findings = load(RAW / 'findings.json')
    old = {r['rawOrdinal'] for r in previous}
    rows = []
    refs = []
    for number, lines in [('333', [17, 27, 29, 33, 35]), ('343', [785, 787, 789])]:
        path = next((ROOT / 'documents/300_SS').glob('*/' + number + '*'))
        data = subprocess.check_output(['git', 'show', 'origin/main:' + str(path.relative_to(ROOT))])
        assert hashlib.sha256(data).hexdigest() == sha(path)
        text = data.decode().splitlines()
        refs.extend({'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'line': n, 'text': text[n - 1]} for n in lines)
    for name, methods in CASES.items():
        for method, first, last, primary, secondary, ordinals in methods:
            for ordinal in ordinals:
                finding = findings[ordinal]
                assert ordinal not in old and Path(finding['path']).name == name
                assert finding['rule'] == 'AvoidCatchingGenericException'
                assert finding['attributes']['method'] == method
                path = ROOT / finding['path']
                assert sha(path) == finding['sourceSha256']
                source = path.read_text().splitlines()
                line = int(finding['attributes']['beginline'])
                assert line in [primary, secondary]
                caught = 'RuntimeException' if 'RuntimeException' in finding['message'] else 'Error'
                assert caught in source[line - 1]
                role = 'BODY_FAILURE_OWNED_CLEANUP' if line == primary else 'CLEANUP_FAILURE_PRIORITY'
                if name == 'ResourceScope.java':
                    contract = 'SS333:17,27,29 and SS343:789'
                    matrix = ('Unknown body RuntimeException/Error must retain original identity after one same-owner cleanup attempt; cleanup failures add one new fixed StorageIoException secondary. Known IOException body with unchecked/fatal cleanup prioritizes that original cleanup. The outer catch normalizes only IOException; no unchecked/fatal failure returns success.')
                    post = ['factory failure: no action/release; raw E/identity', 'one release on success/body failure; no normal return before release', 'each body IO/Runtime/Error x cleanup IO/Runtime/Error; same/distinct throwable', 'known IO reason/unknown identity/fixed secondary and nested reverse order', 'null ports before acquisition; null acquired resource; nullable action result']
                elif name == 'ProcessResourceScope.java':
                    contract = 'SS333:33 and SS343:787'
                    matrix = ('Known IO/Interrupted/StopGate primary with unknown cleanup prioritizes the same unknown cleanup and restores interrupt for Interrupted primary. Unknown primary remains identical with one fresh fixed StopGate secondary, including same throwable from both ports. Successful work cannot return before release.')
                    post = ['factory/nullable acquisition ownership boundaries', 'one same-resource release; nested stream reverse order', 'IO/Interrupted/StopGate/unknown Runtime/Error cross cleanup StopGate/Runtime/Error', 'same throwable avoids self-suppression; fixed diagnostics only', 'interrupt flag before unknown cleanup propagation; no actual process completion inferred']
                else:
                    contract = 'SS343:785'
                    matrix = ('Checked IO/Interrupted lookup scope intentionally retains IOException contract. Unknown cleanup takes priority over checked primary and restores interrupt; unknown body identity is retained with fresh fixed IOException secondary. Scope caller normalizes checked IO only after nested cleanup, joins readers before wiping buffer; it does not certify OS/NSS termination.')
                    post = ['checked IO/Interrupted and unknown Runtime/Error cross cleanup IO/Runtime/Error', 'same/distinct throwable identity and fresh fixed IOException secondary', 'exact once release, nested stdio/executor order and TERM-before-join', 'interrupt preservation, all getters/nulls, buffer wipe after reader termination', 'actual NSS timeout/OS termination remains separate unperformed dynamic work']
                necessity = ('Catching ' + caught + ' at the body boundary is necessary to attempt cleanup of already-owned resources before propagating failure; removing this catch leaves the approved failure path without cleanup.' if line == primary else 'Catching ' + caught + ' from cleanup is necessary to enforce the approved competing-failure matrix rather than replace an unknown body identity with an incidental release failure. It does not swallow or retry the cleanup failure.')
                rows.append({'rawOrdinal': ordinal, 'id': f'{ordinal:06d}:' + hashlib.sha256(canon(finding)).hexdigest(), 'rawFinding': finding, 'method': method, 'caughtType': caught, 'catchRole': role, 'sourceContext': {'firstLine': first, 'lastLine': last, 'lines': source[first - 1:last]}, 'reason': contract + '. ' + necessity + ' ' + matrix, 'requiredDynamicPostconditions': post, 'classification': 'CONTEXTUAL_NONAPPLICABLE', 'actualViolation': False, 'ptExempt': False, 'runtimeProven': False, 'newWbsAcceptance': False})
    chosen = old | {r['rawOrdinal'] for r in rows}
    assert len(rows) == 20 and len(chosen) == 327
    remaining = [{'rawOrdinal': i, 'id': f'{i:06d}:' + hashlib.sha256(canon(f)).hexdigest(), 'rawFinding': f, 'applicability': 'UNCLASSIFIED', 'actualViolation': None} for i, f in enumerate(findings) if i not in chosen]
    assert len(remaining) == 1164
    return {'source': '28af318d0198fe7432ca6fcd234d3fabbfd10173', 'rawCount': 1491, 'priorContext': 307, 'newContext': 20, 'combinedReviewed': 327, 'remainingCount': 1164, 'classified': rows, 'remaining': remaining, 'canonicalMain': subprocess.check_output(['git', 'rev-parse', 'origin/main'], text=True).strip(), 'canonicalDesignReferences': refs, 'rawGateUnchanged': 1, 'actualApplicableViolations': None, 'productExecuted': False, 'coverageMeasured': False, 'newAcceptance': 0, 'wholeF03Accepted': False, 'whole451Accepted': False}


def run():
    assert not SLOT.exists() and not PUBLIC.exists()
    value = inspect()
    SLOT.mkdir()
    (SLOT / 'review.json').write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    manifest = {'actualExit': 0, 'source': value['source'], 'atJST': datetime.datetime.now().astimezone().isoformat(), 'driverSha256': sha(__file__), 'reviewSha256': sha(SLOT / 'review.json'), 'orchestrationHead': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), 'newContext': 20, 'combinedReviewed': 327, 'remaining': 1164, 'productExecuted': False, 'newAcceptance': 0, 'wholeF03Accepted': False}
    (SLOT / 'manifest.safe.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'reviewed': 20, 'combined': 327, 'remaining': 1164}))


def post():
    # Reconstruct the partition from original raw observations, independently of inspect().
    manifest = load(SLOT / 'manifest.safe.json')
    value = load(SLOT / 'review.json')
    assert manifest['actualExit'] == 0 and manifest['driverSha256'] == sha(__file__)
    assert manifest['reviewSha256'] == sha(SLOT / 'review.json')
    previous = prerequisites()
    raw = load(RAW / 'findings.json')
    required = {i for methods in CASES.values() for case in methods for i in case[-1]}
    current = value['classified']
    assert len(current) == 20 and {r['rawOrdinal'] for r in current} == required
    assert all(not r['ptExempt'] and not r['runtimeProven'] for r in current)
    for row in current:
        finding = row['rawFinding']
        path = ROOT / finding['path']
        assert sha(path) == finding['sourceSha256']
        lines = path.read_text().splitlines()
        context = row['sourceContext']
        assert context['lines'] == lines[context['firstLine'] - 1:context['lastLine']]
        assert row['requiredDynamicPostconditions'] and row['reason']
    for ref in value['canonicalDesignReferences']:
        data = subprocess.check_output(['git', 'show', 'origin/main:' + ref['path']])
        assert sha(ROOT / ref['path']) == ref['sha256'] == hashlib.sha256(data).hexdigest()
        assert data.decode().splitlines()[ref['line'] - 1] == ref['text']
    allrows = previous + current + value['remaining']
    assert len(previous + current) == 327 and len(value['remaining']) == 1164
    assert len(allrows) == len({r['rawOrdinal'] for r in allrows}) == len({r['id'] for r in allrows}) == len(raw) == 1491
    indexed = {r['rawOrdinal']: r for r in allrows}
    assert set(indexed) == set(range(1491))
    for i, finding in enumerate(raw):
        assert indexed[i]['rawFinding'] == finding
        assert indexed[i]['id'] == f'{i:06d}:' + hashlib.sha256(canon(finding)).hexdigest()
    counts = collections.Counter(canon(f) for f in raw)
    assert len(counts) == 1439 and sum(c == 2 for c in counts.values()) == 52 and max(counts.values()) == 2
    assert not PUBLIC.exists()
    PUBLIC.mkdir(parents=True)
    for p in SLOT.iterdir():
        if p.is_file():
            shutil.copyfile(p, PUBLIC / p.name)
    result = dict(manifest, independentPostReconstruction=True, allOriginalOrdinalsExact=True, disjointPartition1491=True, duplicateGroupsPreserved=52, files={p.name: sha(p) for p in PUBLIC.iterdir() if p.is_file()})
    (PUBLIC / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'manifestSha256': sha(PUBLIC / 'manifest.json'), 'combined': 327, 'remaining': 1164}))


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['run', 'post']
    (run if sys.argv[1] == 'run' else post)()
