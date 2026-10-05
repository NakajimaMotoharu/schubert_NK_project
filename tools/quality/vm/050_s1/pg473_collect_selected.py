"""PG-D378: exact fresh selected XML; accumulated coverage is provisional only."""
import datetime
import hashlib
import json
import pathlib
import sys
import xml.etree.ElementTree as E

ROOT = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
version = sys.argv[1]
assert version in ('v2', 'v3')
stem = WORK / ('pg473-web-remaining-selected-' + version)
def read(suffix):
    return pathlib.Path(str(stem) + suffix).read_text().strip()
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
assert read('.exit') == '0'
started = datetime.datetime.fromisoformat(read('.started')).timestamp()
log = read('.log')
assert 'BUILD SUCCESS' in log
assert log.count('BugInstance size is 0') == 5
assert log.count('No errors/warnings found') == 5
expected = {
    'protocol': {'MessageCodecTest': 7},
    'storage': {'ResourceScopeTest': 8, 'PrivateDirectoryEntryTest': 12},
    'bootstrap': {'FixedServiceIdentityTest': 10, 'ServiceCredentialSetTest': 5},
    'api': {'ApiProcessMainTest': 4},
    'web': {'WebProcessMainTest': 4, 'WebProcessLifetimeTest': 3,
            'WebNativeRuntimePartialTest': 3, 'WebRequestIdentityConsistencyTest': 3,
            'WebRuntimeHealthTest': 4, 'WebUnknownRetentionTest': 1, 'WebRuntimeStopTest': 5,
            'WebRuntimeRemainderTest': 4, 'WebRuntimeExecutionTest': 2,
            'WebTerminalCaptureTest': 3, 'WebAdmissionRemainderTest': 3},
}
rows = []
for module, names in expected.items():
    reports = ROOT / 'src' / ('schubert-nk-' + module) / 'target/surefire-reports'
    for name, count in names.items():
        paths = list(reports.glob('TEST-*.' + name + '.xml'))
        assert len(paths) == 1
        path = paths[0]
        assert path.stat().st_mtime >= started
        suite = E.parse(path).getroot()
        assert int(suite.get('tests')) == count
        assert all(int(suite.get(k)) == 0 for k in ('failures', 'errors', 'skipped'))
        cases = suite.findall('testcase')
        assert len(cases) == count
        assert all(not any(c.find(t) is not None for t in ('failure','error','skipped')) for c in cases)
        rows.append({'module': module, 'class': suite.get('name'), 'tests': count,
                     'xmlSha256': sha(path), 'methods': [c.get('name') for c in cases]})
assert len(rows) == 17 and sum(r['tests'] for r in rows) == 81
coverage_path = ROOT / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml'
assert coverage_path.stat().st_mtime >= started
report = E.parse(coverage_path).getroot()
counters = {}
for name in ('WebRuntimeFailureSignal','WebRuntimeExecution','WebTerminalCapture',
             'WebTerminalCapture$Owner','WebRuntimeHealth','WebProcessLifetime','WebProcessMain'):
    c = report.find(".//class[@name='dev/codex/schubert/nk/web/bootstrap/" + name + "']")
    assert c is not None
    counters[name] = {v.get('type'): {'missed': int(v.get('missed')), 'covered': int(v.get('covered'))}
                      for v in c.findall('counter')}
if version == 'v3':
    assert all(counters['WebRuntimeExecution'][k]['missed'] == 0 for k in ('LINE','METHOD','CLASS'))
out = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional' / ('PG473-web-remaining-selected-' + version)
assert not out.exists()
out.mkdir(parents=True)
payload = {'id': out.name, 'programId': ['NK-WEB-002','NK-OPS-001'],
    'TestIDs': ['PT-OPS-WEB-REM001..006','PT-OPS-NWEB-UNKNOWN001'], 'PGD': 'PG-D378',
    'baseCommit': read('.source'), 'branch': 'dev-foundation', 'dirtySource': True,
    'started': read('.started'), 'completed': read('.completed'), 'actualExit': 0,
    'command': 'bash tools/quality/vm/050_s1/pg473_web_remaining_selected_' + version + '.sh',
    'tests': 81, 'suites': 17, 'F': 0, 'E': 0, 'S': 0, 'XML': rows,
    'staticModules': 5, 'staticFindings': 0, 'formatNullAwayWerror': 'PASS',
    'localCounters': counters, 'coverageXMLSha256': sha(coverage_path),
    'privateLogSha256': sha(pathlib.Path(str(stem)+'.log')),
    'sourceDiffSha256': sha(pathlib.Path(str(stem)+'.source-diff.private')),
    'initialSourceFilesSha256': sha(pathlib.Path(str(stem)+'.source-files.sha256')),
    'environment': {'JDK':'25.0.4','Maven':'3.9.12','JaCoCo':'0.8.15','OS':'Linux'},
    'independentOracle': 'literal route/order/error identity, JDK SHA and isolated actual retention',
    'accumulatedExec': True, 'wholeCoverage100': False, 'nativeAccepted': False,
    'formalUpdated': False, 'ITSTAccepted': False, 'oldNativeReused': False,
    'v1ActualExit': 1, 'v1NewWebTests': 'NOT_RUN', 'rawSecretsExported': False}
path = out / 'manifest.json'
path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'tests':81,'suites':17,'static5zero':True,'manifestSha256':sha(path),
                  'executionCounters':counters['WebRuntimeExecution'],'formal':False}))
