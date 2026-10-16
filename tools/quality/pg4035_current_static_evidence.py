"""Public current304/raw1653 plus four current owning witnesses; no guest or new test execution."""
import base64
import hashlib
import inspect
import json
import shlex
from lan_server import run
from pg3966_literal_invariant_full_six import ROOT, W, SOURCE, require


def server(data):
    import base64
    import hashlib
    import json
    from pathlib import Path
    import xml.etree.ElementTree as E
    b = Path('/home/mini/schubert-nk-pgpt'); sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    p = b / 'runs/PG4034-current-jdbc-finally-static-v1/manifest.safe.json'; require(sha(p) == data['typedManifestSha256'], 'actual current304 typed authority')
    typed = json.loads(p.read_bytes()); rows_path = p.parent / 'all1653-dispositions.safe.json'; require(sha(rows_path) == typed['allDispositionsSha256'], 'all current raw1653 records')
    rows = json.loads(rows_path.read_bytes()); require(len(rows) == 1653 and sum(r['disposition'] != 'UNCLASSIFIED' for r in rows) == 304, 'complete current raw/assessed partition')
    qp = b / 'runs/PG3968-literal-invariant-whole-qualified-v1/manifest.safe.json'; require(sha(qp) == data['qualificationSha256'], 'actual new3717 whole authority')
    q = json.loads(qp.read_bytes()); require(q['productionSource'] == data['source'] and q['tests'] == 3717, 'no old source XML transfer')
    selected = [r for r in rows if r['disposition'] == 'REQUIRED_JDK_SELF_SUPPRESSION_IDENTITY_GUARD']
    require(len(selected) == 30 and sum(not r.get('owningTestIds') for r in selected) == 4, 'exact four non-conventional owning mappings')
    joined = []
    for case in data['cases']:
        matches = [r for r in selected if r['path'] == case['productionPath'] and {k: r['typedIdentityFact'][k] for k in case['fact']} == case['fact']]
        require(len(matches) == 1 and not matches[0].get('owningTestIds'), 'unique current actual resolved symbol/type guard, not historical coordinate substitution')
        row = matches[0]; source = b / 'source-full-PG3966'
        require(sha(source / case['productionPath']) == row['sourceSha256'] and sha(source / case['testPath']) == case['testSha256'], 'actual current Main/Test bytes')
        xml = b / 'runs/PG3966-six-v1' / case['module'] / 'surefire-reports' / ('TEST-' + case['class'] + '.xml')
        require(sha(xml) == q['modules'][case['module']]['xmlHashes'][xml.name], 'qualified new current XML')
        tests = [c for c in E.parse(xml).getroot().findall('testcase') if c.get('name') == case['method']]
        require(len(tests) == 1 and not any(n.tag in {'failure', 'error', 'skipped', 'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError'} for n in tests[0].iter()), 'actual named independent identity witness passed')
        evidence = {**case, 'currentFindingId': row['id'], 'qualifiedXmlSha256': sha(xml), 'currentWholeQualificationSha256': data['qualificationSha256']}
        row['owningTestIds'] = [case['class'] + '#' + case['method']]; row['currentExplicitWitness'] = evidence; joined.append(evidence)
    require(len(joined) == 4 and all(r.get('owningTestIds') for r in selected), 'all30 actual current owning witnesses')
    raw = json.dumps(rows, sort_keys=True).encode()
    print(json.dumps({'actualExit': 0, 'rawSha256': hashlib.sha256(raw).hexdigest(), 'rowsBase64': base64.b64encode(raw).decode(), 'fourCurrentWitnesses': joined}))


def main():
    typed_path = W / 'pg4034-current-jdbc-finally-static-v1/manifest.safe.json'; typed = json.loads(typed_path.read_bytes()); t = typed['result']
    require(typed['actualExit'] == 0 and t['productionSource'] == SOURCE and (t['rawFindings'], t['technicalDispositions'], t['unclassified']) == (1653, 304, 1349), 'genuine current typed assessment')
    public = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
    blueprint = json.loads((public / 'PG3894-identity-explicit-witness-v1/four-explicit-witnesses.json').read_bytes())
    old_rows = json.loads((public / 'PG3868-identity-assessment-v1/all-65-identity-findings.json').read_bytes())
    facts = {r['id']: r['typedIdentityFact'] for r in old_rows if r.get('typedIdentityFact')}
    keys = ['kind', 'path', 'leftSymbol', 'leftType', 'rightSymbol', 'rightType']; cases = []
    for old in blueprint['fourExplicitWitnesses']:
        test = ROOT / old['path']; require(hashlib.sha256(test.read_bytes()).hexdigest() == old['sha256'], 'unchanged independent owning Test source')
        cases.append({'priorFindingId': old['findingId'], 'productionPath': old['productionPath'], 'testPath': old['path'], 'testSha256': old['sha256'],
                      'module': old['module'], 'class': old['class'], 'method': old['method'], 'fact': {k: facts[old['findingId']][k] for k in keys}})
    q = json.loads((W / 'pg3968-literal-invariant-whole-qualified-v1/manifest.safe.json').read_bytes())
    data = {'source': SOURCE, 'cases': cases, 'typedManifestSha256': t['serverManifestSha256'], 'qualificationSha256': q['result']['qualificationManifestSha256']}
    code = inspect.getsource(require) + '\n' + inspect.getsource(server) + '\nserver(' + repr(data) + ')\n'
    status, output = run('python3 -B -c ' + shlex.quote(code), timeout=90); require(status == 0, 'current raw assessment and explicit owning witness read')
    actual = json.loads(next(line for line in output.splitlines() if line.startswith('{'))); raw = base64.b64decode(actual.pop('rowsBase64'), validate=True)
    require(hashlib.sha256(raw).hexdigest() == actual['rawSha256'], 'exact current safe row capsule')
    out = public / 'PG4035-current-static-assessments-v1'; out.mkdir()
    (out / 'all-1653-findings.json').write_bytes(raw)
    (out / 'four-current-owning-witnesses.json').write_text(json.dumps(actual['fourCurrentWitnesses'], sort_keys=True, indent=2) + '\n')
    receipts = {label: json.loads((W / name / 'manifest.safe.json').read_bytes()) for label, name in [('standalone239', 'pg4030-current-standalone-static-v1'), ('identity30', 'pg4032-current-identity-static-v1'), ('jdbc26', 'pg4034-current-jdbc-finally-static-v1')]}
    (out / 'current-technical-receipts.json').write_text(json.dumps(receipts, sort_keys=True, indent=2) + '\n')
    manifest = {'actualExit': 0, 'productionSource': SOURCE, 'run': 'PG4035-current-static-assessments-v1', 'testIds': ['PT-F03-ARCH4030', 'PT-F03-IDENTITY4032', 'PT-F03-JDBC4034', 'PT-F03-WITNESS4035'],
                'branch': 'dev-foundation', 'os': 'Linux aru host', 'jdk': '25.0.4', 'pmd': '7.28.0 pinned unchanged rules/record overlay', 'rawFindings': 1653,
                'technicalDispositions': 304, 'unclassified': 1349, 'applicableViolationCount': None, 'currentIdentityFindingsWithOwningTests': 30,
                'unsupportedCurrentJdbcScopes': t['unsupportedCurrentScopes'], 'F03Accepted': False, 'formalAccepted': False, 'formalTests': 1964, 'formalScopes': 53,
                'effortPercent': None, 'qa051Final': 'HELD', 'sourceChanged': False, 'pmdReissued': False, 'newTests': 0, 'vmActions': 0,
                'qualificationSha256': data['qualificationSha256'], 'readPayloadSha256': hashlib.sha256(code.encode()).hexdigest(),
                'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()}}
    (out / 'manifest.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'rawFindings': 1653, 'technicalDispositions': 304, 'unclassified': 1349, 'currentIdentityOwning': 30, 'F03Accepted': False, 'manifestSha256': hashlib.sha256((out / 'manifest.json').read_bytes()).hexdigest()}))
    return 0


if __name__ == '__main__': raise SystemExit(main())
