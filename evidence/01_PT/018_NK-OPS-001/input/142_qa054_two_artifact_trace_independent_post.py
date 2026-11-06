"""Independent qualification of historical trace bindings; no Product replay."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

r = Path.cwd()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
p = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21780-qa054-two-artifact-existing-proof-trace-v2/manifest.json'
assert sha(p) == 'ef21d2770c1b5d6e7655d3a585a9f1619c3c186a3cc21a02bbc0c242ec092c8e'
m = load(p)
assert m['actualExit'] == 0 and m['newlyExecutedTests'] == 0 and not m['currentCombinedRun'] and not m['oldExecUnion']
assert len(m['rows']) == m['boundArtifacts'] == 2 and sum(len(x['methods']) for x in m['rows']) == m['boundMethods'] == 23
specs = {}
for ref in m['independentOracleSpecifications']:
    q = r / ref['path']
    assert sha(q) == ref['sha256']
    specs[q.name] = q.read_text()
special = {
    'concurrentValidAndInvalidSnapshotsKeepTheirDiagnosticsAndInputsIsolated': 'PT-CHR-LOG-COR-009',
    'strictVersionPredicateNeverCoercesMissingFractionalTextOrOversizedValues': 'PT-CHR-LOG-COR-011'}
counts = {'methods': 0, 'line': 0, 'branch': 0, 'testIds': 0, 'supportGroupMethods': 0}
for row in m['rows']:
    original = r / row['original']['path']
    assert sha(original) == row['original']['sha256']
    old = load(original)
    assert old['source'] == row['original']['source']
    assert old['actualExit'] == old['failures'] == old['errors'] == old['skipped'] == old['aborted'] == 0
    assert sha(r / row['path']) == row['mainSha256']
    for n, h in row['evidenceFiles'].items():
        assert sha(original.parent / n) == old['files'][n] == h
    selected = {(c, n) for c, n in old['selectedTestMethods']}
    assert selected == {(x['className'], x['method']) for x in row['selectedTests']}
    assert len(selected) == row['originalTestCount']
    ids = set()
    for case in row['selectedTests']:
        ident, method = case['testId'], case['method']
        if ident is None:
            assert case['className'].endswith('WebRequestTraceTest')
            assert 'REQ004/006/007/008' in case['originalRegressionGroup']
            counts['supportGroupMethods'] += 1
        else:
            assert case['originalRegressionGroup'] is None
            if method in special:
                assert ident == special[method] and method in specs['001_NK-CHR-001_相関ログ証拠単体テスト仕様書.md']
            elif ident.startswith('PT-CHR-QA054'):
                assert method.startswith('qa054log' + ident[-3:]) and 1 <= int(ident[-3:]) <= 7
            else:
                assert any(ident in text and method in text for text in specs.values())
            ids.add(ident)
            counts['testIds'] += 1
    cls = row['path'].split('/src/main/java/', 1)[1][:-5]
    xml = ET.parse(original.parent / 'coverage.xml')
    c = next(c for c in xml.findall('.//class') if c.get('name') == cls)
    reported = {x.get('type'): dict(covered=int(x.get('covered')), missed=int(x.get('missed'))) for x in c.findall('counter')}
    assert reported == row['coverage'] and all(reported[k]['missed'] == 0 for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH'])
    measured = {(x.get('name'), x.get('desc')): x for x in c.findall('method')}
    assert set(measured) == {(x['name'], x['descriptor']) for x in row['methods']}
    for method in row['methods']:
        x = measured[(method['name'], method['descriptor'])]
        counters = {a.get('type'): dict(covered=int(a.get('covered')), missed=int(a.get('missed'))) for a in x.findall('counter')}
        assert counters == method['counters'] and all(a['missed'] == 0 for a in counters.values())
        assert set(method['specificationTestIds']) <= ids and method['specificationTestIds']
        assert method['binding'] == 'SUITE_SET_COVERAGE_NOT_SINGLE_TEST_PROBE_ATTRIBUTION'
    assert not row['singleTestProbeAttributionMeasured'] and not row['currentCombinedRun']
    counts['methods'] += len(measured)
    counts['line'] += reported['LINE']['covered']
    counts['branch'] += reported['BRANCH']['covered']
assert counts == dict(methods=23, line=204, branch=238, testIds=21, supportGroupMethods=10)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
assert hashlib.sha256(subprocess.check_output(['git', 'show', head + ':' + str(Path(__file__).relative_to(r))])).hexdigest() == sha(Path(__file__))
out = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21782-qa054-two-artifact-trace-independent-post-v1'
assert not out.exists()
out.mkdir()
v = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), checkerSource=head,
    checkerSha256=sha(Path(__file__)), original=dict(path=str(p.relative_to(r)), sha256=sha(p)),
    boundArtifacts=2, counts=counts, historicalTestInvocationsReferenced=31,
    newProductTests=0, newMethods=0, newSourceProofs=0, newAcceptance=0,
    currentCombinedRun=False, exactAssertionLevelTraceVerified=False, wholeG13Accepted=False, effortRate=None)
(out / 'manifest.json').write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(actualExit=0, boundArtifacts=2, methods=23, newProductTests=0, manifestSha256=sha(out / 'manifest.json'))))
