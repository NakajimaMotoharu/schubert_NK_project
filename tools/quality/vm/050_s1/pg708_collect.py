"""Independent 40PT/3suite/2static and six unchanged main-byte qualification."""
import datetime
import hashlib
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pg707_selected import classes, MODULES, HOST, D, T


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    os.umask(0o077)
    run = json.loads((D / 'run.safe.json').read_bytes())
    assert run['actualExit'] == 0 and run['allSixMainBytesUnchanged']
    source = run['operatorSource']; assert source == '329dd8d76f467b8702a6d453f3ba429cbd4d92c6'
    assert (D / 'exit').read_bytes() == b'0\n'
    for name, digest in run['files'].items(): assert sha(D / name) == digest
    counts = {'api': {'dev.codex.schubert.nk.api.bootstrap.BootstrapAdminMainTest': 5,
                      'dev.codex.schubert.nk.api.bootstrap.ApiProcessMainTest': 4},
              'batch': {'dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest': 31}}
    new_names = {'boot707001ExternalMainRejectsMissingNamespaceAndArgvWithoutSecretDiagnostics',
                 'mdb707001FailedAndMissingRetentionRowsStayIneligibleWithIndependentSqlPostcondition'}
    observed = set(); all_cases = []; main_count = 0
    for module in MODULES:
        name = 'schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar'
        baseline = classes(HOST / module / name)
        current = classes((D / module / name) if module in counts else HOST / module / name)
        assert current == baseline; main_count += len(baseline)
    assert main_count == 1612
    for module, expected in counts.items():
        paths = list((D / module).glob('TEST-*.xml'))
        assert {p.name for p in paths} == {'TEST-' + n + '.xml' for n in expected}
        for path in paths:
            root = ET.parse(path).getroot(); assert root.get('name') in expected
            assert root.get('tests') == str(expected[root.get('name')])
            assert all(root.get(k) == '0' for k in ('failures', 'errors', 'skipped'))
            cases = root.findall('testcase'); assert len(cases) == expected[root.get('name')]
            assert len({c.get('name') for c in cases}) == len(cases)
            for case in cases:
                assert not any(case.findall(k) for k in ('failure', 'error', 'skipped', 'flakyFailure', 'rerunFailure', 'rerunError'))
                observed.add(case.get('name')); all_cases.append(case.get('name'))
        bugs = ET.parse(D / module / 'spotbugsXml.xml').getroot()
        assert not bugs.findall('BugInstance') and not bugs.findall('.//Error')
        assert (D / module / 'jacoco.exec').stat().st_size > 0
    assert len(all_cases) == 40 and new_names <= observed
    for path in ('src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMainTest.java',
                 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSessionTest.java'):
        assert subprocess.check_output(['git', 'show', source + ':' + path], cwd=T) == (T / path).read_bytes()
    result = {'actualExit': 0, 'run': D.name, 'operatorSource': source,
              'productionSource': '9bd50536f692610036a0ed8b83e0a8b35fe2a66f',
              'selectedTests': 40, 'suites': 3, 'newCases': 2, 'FESFlakyNotRun': 0,
              'staticModules': 2, 'staticIssues': 0, 'allMainClassBytesEqualPG680': 1612,
              'selectedExecHashes': {m: sha(D / m / 'jacoco.exec') for m in counts},
              'runReceiptSha256': sha(D / 'run.safe.json'), 'files': run['files'],
              'startedUTC': run['startedUTC'], 'endedUTC': run['endedUTC'],
              'recordedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'formalAccepted': False, 'actualVMAdmission': False, 'rawExported': False}
    with (D / 'manifest.safe.json').open('x') as output:
        json.dump(result, output, sort_keys=True); output.flush(); os.fsync(output.fileno())
    print(json.dumps({'actualExit': 0, 'tests': 40, 'suites': 3, 'newCases': 2,
                      'staticIssues': 0, 'mainByteEqual': 1612, 'manifestSha256': sha(D / 'manifest.safe.json')}))


if __name__ == '__main__': main()
