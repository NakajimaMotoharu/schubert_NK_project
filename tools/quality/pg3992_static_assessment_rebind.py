"""Narrow source/statement/Test requalification; unmatched historical assessments stay unresolved."""
import difflib
import hashlib
import inspect
import json
import os
import subprocess
from lan_server import run, copy
from pg3966_literal_invariant_full_six import ROOT, W, SOURCE, MAIN, require


def mapped_lines(before, after, first, last):
    old = before.splitlines(); new = after.splitlines()
    if not 1 <= first <= last <= len(old): return None
    block_lines = old[first - 1:last]; count = len(block_lines)
    # Repeated identical statements in distinct scopes are not a sufficient
    # identity proof. Hold them rather than infer a scope from line proximity.
    if sum(old[i:i + count] == block_lines for i in range(len(old) - count + 1)) != 1: return None
    if sum(new[i:i + count] == block_lines for i in range(len(new) - count + 1)) != 1: return None
    for block in difflib.SequenceMatcher(None, old, new, autojunk=False).get_matching_blocks():
        if block.a <= first - 1 and last <= block.a + block.size:
            return first + block.b - block.a, last + block.b - block.a
    return None


def server(data):
    from collections import Counter
    import datetime
    import hashlib
    import json
    from pathlib import Path
    import xml.etree.ElementTree as E
    b = Path('/home/mini/schubert-nk-pgpt'); sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    old = b / 'runs/PG3946-jdbc-finally-review-v1'; prior = json.loads((old / 'manifest.safe.json').read_bytes())
    require(sha(old / 'manifest.safe.json') == data['priorManifestSha256'] and prior['technicalDispositions'] == 304, 'original304 assessment authority')
    previous = old / 'all1840-dispositions.safe.json'; require(sha(previous) == prior['allDispositionsSha256'], 'all old rows retained')
    historical = json.loads(previous.read_bytes()); require(len(historical) == 1840, 'original full1840 not reduced in place')
    static_dir = b / 'runs/PG3970-current-main-static-v1'; require(sha(static_dir / 'manifest.safe.json') == data['staticManifestSha256'], 'actual fixed1653 authority')
    static = json.loads((static_dir / 'manifest.safe.json').read_bytes()); require(static['mainGitSource'] == data['source'] and sha(static_dir / 'pmd.xml') == static['pmd']['reportSha256'], 'actual new Main/raw report bytes')
    qpath = b / 'runs/PG3968-literal-invariant-whole-qualified-v1/manifest.safe.json'; require(sha(qpath) == data['wholeQualificationSha256'], 'genuine new3717 qualification')
    q = json.loads(qpath.read_bytes()); require(q['actualExit'] == 0 and q['productionSource'] == data['source'] and q['tests'] == 3717 and q['allOriginalCaseIdentitiesRetained'], 'newsource all old cases retained')
    proof_path = b / 'runs/PG3952-literal-candidate-v1/manifest.safe.json'; require(sha(proof_path) == data['literalProofSha256'], 'all six full normalized compiler proof')
    proof = json.loads(proof_path.read_bytes()); require(proof['allValuesTypedBindingsFullAstAndPublicAbiIdentical'] and proof['changedFiles'] == 71 and proof['proposedConstants'] == 187, 'only proven compile-time string change can bridge a changed source')
    current = b / 'source-full-PG3966'; original = b / 'source-full-PG3734'; candidate = b / 'runs/PG3970-current-main-static-input-v1/candidate'
    actual_map = {str(p.relative_to(current)): sha(p) for p in current.glob('src/*/src/main/java/**/*.java')}
    require(len(actual_map) == 849 and actual_map == static['allMainSha256'] == data['sourceSha256'], 'all current actual Main bytes')
    rows = []
    for f in E.parse(static_dir / 'pmd.xml').getroot().findall('{*}file'):
        path = str(Path(f.get('name')).relative_to(candidate)); require(path in actual_map, 'actual source-bound raw finding')
        for finding in f.findall('{*}violation'):
            rows.append({'path': path, 'sourceSha256': actual_map[path], 'rule': finding.get('rule'), 'priority': finding.get('priority'),
                         'coordinates': {k: int(finding.get(k)) for k in ['beginline', 'endline', 'begincolumn', 'endcolumn']},
                         'message': (finding.text or '').strip(), 'disposition': 'UNCLASSIFIED'})
    require(len(rows) == 1653, 'all new raw findings retained')
    rows.sort(key=lambda r: (r['path'], r['coordinates']['beginline'], r['rule'], r['coordinates']['begincolumn']))
    for index, row in enumerate(rows, 1): row['id'] = 'PMD-7bb-' + str(index).zfill(4)
    requalified = []; held = []
    for oldrow in historical:
        if oldrow['disposition'] == 'UNCLASSIFIED': continue
        path = oldrow['path']; oldfile = original / path; newfile = current / path
        require(sha(oldfile) == oldrow['sourceSha256'], 'historical source identity not rewritten')
        if sha(newfile) != sha(oldfile) and (path not in proof['changes'] or path == data['nonEquivalentSource']):
            held.append({'priorId': oldrow['id'], 'reason': 'NO_FULL_SEMANTIC_EQUIVALENCE_FOR_CHANGED_SOURCE'}); continue
        c = oldrow['coordinates']; positions = mapped_lines(oldfile.read_text(), newfile.read_text(), c['beginline'], c['endline'])
        if positions is None:
            held.append({'priorId': oldrow['id'], 'reason': 'STATEMENT_BYTES_NOT_ONE_UNCHANGED_BLOCK'}); continue
        coordinates = {**c, 'beginline': positions[0], 'endline': positions[1]}
        matches = [r for r in rows if r['path'] == path and r['rule'] == oldrow['rule'] and r['coordinates'] == coordinates and r['priority'] == oldrow['priority'] and r['message'] == oldrow['message']]
        if len(matches) != 1:
            held.append({'priorId': oldrow['id'], 'reason': 'NO_UNIQUE_CURRENT_SAME_RULE_MESSAGE_COORDINATE'}); continue
        row = matches[0]; require(row['disposition'] == 'UNCLASSIFIED', 'one historical assessment cannot double-own a new finding')
        # Require all unchanged independent Test files; case retention is checked against the new actual whole, not arithmetic.
        witnesses = []
        for item in oldrow.get('owningTestIds', []):
            if isinstance(item, str): witnesses.append(item)
            elif isinstance(item, dict) and 'testId' in item: witnesses.append(item['testId'])
        if oldrow.get('owningTestId'): witnesses.append(oldrow['owningTestId'])
        for item in oldrow.get('evidence', []):
            if isinstance(item, dict) and 'testId' in item: witnesses.append(item['testId'])
        verified = []; changed_test = False
        for test_id in sorted(set(witnesses)):
            cls, method = test_id.split('#', 1); module = path.split('/')[1].removeprefix('schubert-nk-')
            test_path = 'src/schubert-nk-' + module + '/src/test/java/' + cls.replace('.', '/') + '.java'
            if sha(current / test_path) != sha(original / test_path):
                changed_test = True; break
            xml = b / 'runs/PG3966-six-v1' / module / 'surefire-reports' / ('TEST-' + cls + '.xml')
            require(sha(xml) == q['modules'][module]['xmlHashes'][xml.name] and any(c.get('name') == method for c in E.parse(xml).getroot().findall('testcase')), 'named owning case exists in qualified new actual whole')
            verified.append({'testId': test_id, 'currentXmlSha256': sha(xml)})
        if changed_test:
            held.append({'priorId': oldrow['id'], 'reason': 'OWNING_TEST_FILE_CHANGED_REQUIRES_SEPARATE_ORACLE_PROOF'}); continue
        row.update(disposition=oldrow['disposition'], priorAssessment=oldrow, currentAssessmentProof={
            'unchangedStatementRange': coordinates, 'normalizedFullCompilerProofSha256': data['literalProofSha256'] if sha(newfile) != sha(oldfile) else None,
            'currentWholeQualificationSha256': data['wholeQualificationSha256'], 'currentOwningTests': verified, 'fullSourceUnchanged': sha(newfile) == sha(oldfile)},
            qualityGatePass=False, rawWarningRemoved=False, scope='NARROW_TECHNICAL_REQUALIFICATION_NOT_F03_GATE')
        requalified.append(row['id'])
    require(len(requalified) + len(held) == 304, 'all original304 decisions either proved or explicitly held')
    out = b / 'runs/PG3992-static-assessment-rebind-v1'; out.mkdir()
    (out / 'all1653-dispositions.safe.json').write_text(json.dumps(rows, sort_keys=True)); (out / 'held.safe.json').write_text(json.dumps(held, sort_keys=True))
    result = {'actualExit': 0, 'productionSource': data['source'], 'rawFindings': 1653, 'technicalDispositions': len(requalified), 'historicalAssessmentsHeld': len(held),
              'unclassified': 1653 - len(requalified), 'applicableViolationCount': None, 'dispositions': dict(Counter(r['disposition'] for r in rows)),
              'allDispositionsSha256': sha(out / 'all1653-dispositions.safe.json'), 'heldSha256': sha(out / 'held.safe.json'),
              'staticManifestSha256': data['staticManifestSha256'], 'wholeQualificationSha256': data['wholeQualificationSha256'], 'priorManifestSha256': data['priorManifestSha256'],
              'F03Accepted': False, 'formalAccepted': False, 'suppressionAdded': False, 'rulesChanged': False, 'newTechnicalAssessments': 0, 'vmActions': 0,
              'recordedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True)); result['serverManifestSha256'] = sha(out / 'manifest.safe.json'); print(json.dumps(result))


def main():
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    qualified = json.loads((W / 'pg3968-literal-invariant-whole-qualified-v1/manifest.safe.json').read_bytes())
    require(qualified['actualExit'] == 0 and qualified['source'] == SOURCE, 'genuine whole qualification first')
    require(not subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', '.mvn'], cwd=ROOT), 'unchanged source since genuine whole')
    require(not subprocess.check_output(['git', 'diff', '7fffab57a567914956b66452e5e54388642efdec', 'HEAD', '--', 'src/deployment', 'pom.xml', ':(glob)src/*/pom.xml', 'documents/300_SS'], cwd=ROOT), 'unchanged standalone architecture, dependencies and approved design premises')
    data = {'source': SOURCE, 'wholeQualificationSha256': qualified['result']['qualificationManifestSha256'],
            'staticManifestSha256': json.loads((W / 'pg3970-current-main-static-v1/manifest.safe.json').read_bytes())['result']['serverManifestSha256'],
            'priorManifestSha256': json.loads((W / 'pg3946-jdbc-finally-review-v1/manifest.safe.json').read_bytes())['result']['serverManifestSha256'],
            'literalProofSha256': json.loads((W / 'pg3952-literal-candidate-v1/manifest.safe.json').read_bytes())['result']['serverManifestSha256'],
            'sourceSha256': {str(p.relative_to(ROOT)): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}, 'nonEquivalentSource': MAIN}
    os.umask(0o077); out = W / 'pg3992-static-assessment-rebind-v1'; out.mkdir()
    script = out / 'review.private.py'; script.write_text('import difflib\n' + '\n'.join(inspect.getsource(f) for f in [require, mapped_lines, server]) + '\nserver(' + repr(data) + ')\n')
    compile(script.read_text(), '<current narrow static assessment>', 'exec')
    destination = '/home/mini/schubert-nk-pgpt/transfer/PG3992-static-assessment-rebind-v1'
    status, _ = run('test ! -e /home/mini/schubert-nk-pgpt/runs/PG3992-static-assessment-rebind-v1 && mkdir -m700 ' + destination, timeout=30); require(status == 0, 'new-only narrow assessment')
    status, _ = copy(script, destination + '/', timeout=60); require(status == 0, 'complete assessment tool')
    status, output = run('python3 -B ' + destination + '/review.private.py', timeout=120); (out / 'observer.private.log').write_text(output)
    value = {'actualExit': status, 'source': SOURCE, 'payloadSha256': sha(script), 'F03Accepted': False}
    if status == 0: value['result'] = json.loads(next(line for line in reversed(output.splitlines()) if line.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps(value)); return status


if __name__ == '__main__': raise SystemExit(main())
