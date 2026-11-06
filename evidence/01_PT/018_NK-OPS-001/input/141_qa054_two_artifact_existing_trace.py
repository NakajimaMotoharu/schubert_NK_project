"""Bind immutable original success to two same-byte artifacts, without any replay."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET

r = Path.cwd()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
normal = load(r.parent / 'pgpt-runs/PG379/pg20990-outbox-required-six-main-compile-v1/manifest.safe.json')
tool = load(r.parent / 'pgpt-runs/PG379/pg21088-characterization-tool-original-main-compile-v1/manifest.safe.json')
lineagep = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21766-current4217-static-artifact-lineage-v2/manifest.json'
assert sha(lineagep) == 'ee465df2a40a6bba40c02680062a2cbc7d0441a0bc012c67efebfb752ac70a09'
lineage = {a['path']: a for a in load(lineagep.parent / 'artifacts.json')}
webspec = r / 'evidence/01_PT/015_NK-WEB-001/044_QA054メニューmarker・Trace・Controller単体仕様.md'
charspec = r / 'evidence/01_PT/020_NK-CHR-001/001_NK-CHR-001_相関ログ証拠単体テスト仕様書.md'
qaspec = r / 'evidence/01_PT/020_NK-CHR-001/016_QA054相関ログ限定ACTION単体仕様.md'
original_ids = dict((method, ident) for ident, method in re.findall(
    r'\|\s*(PT-CHR-[A-Z0-9-]+)\s*\|\s*(?:CorrelatedLogEvidenceValidatorTest)?#([A-Za-z0-9_]+)', charspec.read_text()))
for pattern in [r'PT-CHR-LOG-COR-(\d{3}) / #([A-Za-z0-9_]+)',
                r'COR-(\d{3})はvalidator#([A-Za-z0-9_]+)']:
    for number, method in re.findall(pattern, charspec.read_text()):
        assert method not in original_ids
        original_ids[method] = 'PT-CHR-LOG-COR-' + number
targets = [
    ('015_NK-WEB-001/evidence/PG19558-qa054-web-menu-fifteen-v1', 'd8be18461ee3436e92752f09ce00fe3e9f70ee5c2edcb51c3fa32aa7060c5adc',
     'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebHttpLogKind.java',
     'dev/codex/schubert/nk/web/logging/WebHttpLogKind', 'WBS-P006-03', 15, 6),
    ('020_NK-CHR-001/evidence/PG19608-qa054-correlated-sixteen-v1', 'bf2fb176f8f1d137d6b94a23091ca2d34952aa23f5e50e2e8d83a9c3bd8e4d06',
     'program/characterization/src/main/java/dev/codex/schubert/characterization/CorrelatedLogEvidenceValidator.java',
     'dev/codex/schubert/characterization/CorrelatedLogEvidenceValidator', 'WBS-P020-01', 16, 17)]
rows = []
held = {'RootFailedStartRecoveryTest.java', 'RootFailedStartPairRecoveryTest.java', 'SnapshotKeyCloseWitness.java', 'pg9892_snapshot_key_close_witness.py'}
for directory, expected, main, cls, owner, count, methods in targets:
    p = r / 'evidence/01_PT' / directory / 'manifest.json'
    assert sha(p) == expected
    m = load(p)
    assert m['actualExit'] == m['failures'] == m['errors'] == m['skipped'] == m['aborted'] == 0
    assert m['tests'] == count
    needed = ['begin.safe.json', 'unit-exit.safe.json', 'coverage.xml']
    needed += ['testcases.safe.xml'] if count == 15 else ['TEST-junit-jupiter.xml', 'TEST-junit-vintage.xml', 'TEST-junit-platform-suite.xml']
    for n in needed:
        assert sha(p.parent / n) == m['files'][n]
    begin, terminal = load(p.parent / 'begin.safe.json'), load(p.parent / 'unit-exit.safe.json')
    assert terminal['actualExit'] == 0 and not terminal['timedOut']
    assert all(Path(n).name not in held for n in begin['inputHashes'])
    for n, h in begin['inputHashes'].items():
        assert sha(r / n) == h
        assert hashlib.sha256(subprocess.check_output(['git', 'show', m['source'] + ':' + n])).hexdigest() == h
    assert lineage[main]['sha256'] == begin['inputHashes'][main] == sha(r / main)
    assert lineage[main]['owner'] == lineage[main]['costOwner'] == owner
    physical = m['physicalHashes'][cls] if count == 15 else m['physical'][cls]
    current_physical = normal['normalPhysicalClassHashes']['web:' + cls + '.class'] if count == 15 else tool['physicalHashes'][cls]
    assert physical == current_physical
    xmlpairs = set()
    for n in needed:
        if n.endswith('.xml') and n != 'coverage.xml':
            for t in ET.parse(p.parent / n).getroot().iter('testcase'):
                assert not any(t.find(k) is not None for k in ['failure', 'error', 'skipped'])
                xmlpairs.add((t.get('classname'), t.get('name', '').removesuffix('()')))
    assert xmlpairs == {tuple(x) for x in m['selectedTestMethods']} and len(xmlpairs) == count
    ids = []
    for classname, method in m['selectedTestMethods']:
        regression_group = None
        if classname.endswith('MenuAuditContractTest'):
            code = 'PT-WEB-MENU' + re.fullmatch(r'menu(\d{3}).*', method)[1]
            assert code in webspec.read_text() and method in webspec.read_text()
        elif classname.endswith('WebRequestTraceTest'):
            code = None
            regression_group = 'REQ004/006/007/008 (015044 existing whole10 group)'
        elif classname.endswith('CorrelatedMenuActionContractTest'):
            code = 'PT-CHR-QA054' + re.fullmatch(r'qa054log(\d{3}).*', method)[1]
            assert 'PT-CHR-QA054001..007' in qaspec.read_text()
        else:
            assert classname.endswith('CorrelatedLogEvidenceValidatorTest') and method in original_ids
            code = original_ids[method]
        ids.append(dict(testId=code, originalRegressionGroup=regression_group, className=classname, method=method))
    xml = ET.parse(p.parent / 'coverage.xml')
    classes = [c for c in xml.findall('.//class') if c.get('name') == cls]
    assert len(classes) == 1
    c = classes[0]
    counts = {x.get('type'): dict(covered=int(x.get('covered')), missed=int(x.get('missed'))) for x in c.findall('counter')}
    assert all(counts[k]['missed'] == 0 for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH'])
    measured = []
    for method in c.findall('method'):
        cs = {x.get('type'): dict(covered=int(x.get('covered')), missed=int(x.get('missed'))) for x in method.findall('counter')}
        assert cs['METHOD'] == dict(covered=1, missed=0) and all(v['missed'] == 0 for v in cs.values())
        applicable = [x['testId'] for x in ids if x['testId'] is not None]
        if count == 15:
            applicable = ['PT-WEB-MENU001', 'PT-WEB-MENU002'] if method.get('name') == 'eligible' else ['PT-WEB-MENU002']
        measured.append(dict(name=method.get('name'), descriptor=method.get('desc'), counters=cs,
            specificationTestIds=applicable, binding='SUITE_SET_COVERAGE_NOT_SINGLE_TEST_PROBE_ATTRIBUTION'))
    assert len(measured) == methods
    rows.append(dict(path=main, owner=owner, costOwner=owner, mainSha256=sha(r / main), physicalSha256=physical,
        original=dict(path=str(p.relative_to(r)), sha256=expected, source=m['source']),
        originalTestCount=count, selectedTests=ids, coverage=counts, methods=measured,
        evidenceFiles={n: m['files'][n] for n in needed}, currentSameByte=True,
        requirementRefs=['FUN-002', 'FUN-008', 'MON-003', 'TST-004', 'UI235', 'UI264', 'SS351', 'SS355', 'QA-054'],
        singleTestProbeAttributionMeasured=False, currentCombinedRun=False))
spec = r / 'evidence/01_PT/018_NK-OPS-001/3610_QA054追加二artifact既存証拠trace仕様.md'
for p in [spec, Path(__file__)]:
    assert hashlib.sha256(subprocess.check_output(['git', 'show', head + ':' + str(p.relative_to(r))])).hexdigest() == sha(p)
out = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21780-qa054-two-artifact-existing-proof-trace-v2'
assert not out.exists()
out.mkdir()
m = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), observerSource=head,
    productionMain='4217e14083c6ecac116216e08d57f4361eb2f12d', rows=rows,
    specification=dict(path=str(spec.relative_to(r)), sha256=sha(spec)),
    independentOracleSpecifications=[dict(path=str(p.relative_to(r)), sha256=sha(p)) for p in [webspec, charspec, qaspec]],
    existingTestInvocationsReferenced=31, newlyExecutedTests=0, boundArtifacts=2, boundMethods=23,
    currentCombinedRun=False, oldExecUnion=False, newMethods=0, newSourceProofs=0,
    newAcceptance=0, exactAssertionLevelTraceVerified=False, wholeG13Accepted=False,
    relatedBug='BUG-2403', relatedHorizontal='YKT-2148', effortRate=None)
(out / 'manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(actualExit=0, boundArtifacts=2, boundMethods=23, newlyExecutedTests=0, manifestSha256=sha(out / 'manifest.json'))))
