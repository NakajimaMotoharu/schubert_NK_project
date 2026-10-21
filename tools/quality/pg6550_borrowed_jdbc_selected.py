"""Finite borrowed JDBC proxy red/green; original result readers never execute tests."""
import argparse
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6054_expiry_read_qualification import qualify
import finite_selected_profile as profile

OLD = '8cfe4388a58af3a5229c2c367353abd44e75bedf'
RED_SOURCE = 'ac5f4d6c7115ae25f6c7e46e05589c0842deb94b'
TESTS = {
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/persistence/BorrowedJdbcFatal329Test.java',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/dispatch/JdbcTransactionBoundary329Test.java'}
NAMES = ('UserQueryRepository', 'ScenarioRepository', 'MediaRepository', 'LogQueryRepository', 'QuestionQueryRepository')
MAINS = {'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/persistence/'+n+'.java' for n in NAMES}
TARGETS = {'api': ['api/persistence/'+n for n in NAMES]+['api/dispatch/JdbcSyncRequestProcessor']}
SLOTS = {'red': 'pg6550-borrowed-jdbc-red-v1', 'green': 'pg6552-borrowed-jdbc-green-v1'}
METHODS = {
 'borrowed329001UserSearch': 'UserQueryException', 'borrowed329002UserDetail': 'UserQueryException',
 'borrowed329003ScenarioRows': 'ScenarioQueryException', 'borrowed329004ScenarioSearch': 'ScenarioQueryException',
 'borrowed329005ScenarioDetail': 'ScenarioQueryException', 'borrowed329006MediaQuery': 'MediaQueryException',
 'borrowed329007LogSearch': 'LogQueryException', 'borrowed329008QuestionPaged': 'QuestionQueryException',
 'borrowed329009QuestionDetail': 'QuestionQueryException'}


def inventory():
    return profile.inventory({'api': {'api.persistence.BorrowedJdbcFatal329Test',
        'api.dispatch.JdbcTransactionBoundary329Test'}}, (23, 9))


def guard_source(source, phase):
    path = BASE/'PG6548-jdbc-transaction-qualification-v1/manifest.json'
    if sha(path) != '979bb5c9283ded355130413afe1f2e0a6fff9a8a38905237c6f959cd8a39f18a':
        raise ValueError('genuine qualified23/9 original first')
    value = json.loads(path.read_bytes())
    if value['source'] != OLD or value['actualExit'] != 0:
        raise ValueError('exact qualified Main source')
    changes = set(subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'],
                                        cwd=ROOT, text=True).splitlines())
    if changes != (TESTS if phase == 'red' else TESTS | MAINS):
        raise ValueError('two independent Test paths / five localized mapper PG only')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw',
                               'program/characterization', 'tools/quality/static'], cwd=ROOT):
        raise ValueError('fixed build/gates/Current')
    if phase == 'green' and (RED_SOURCE is None or subprocess.check_output(
            ['git', 'diff', RED_SOURCE, source, '--', ':(glob)src/*/src/test/**'], cwd=ROOT)):
        raise ValueError('independent red oracle bytes fixed')


def validate_failure(method, failure):
    name = METHODS.get(method)
    expected = ('Unexpected exception type thrown, expected: <java.lang.AssertionError> '
                'but was: <dev.codex.schubert.nk.api.persistence.'+str(name)+'>')
    if (name is None or not failure.get('type', '').endswith('AssertionFailedError')
            or failure.get('message') != expected):
        raise ValueError('only exact predicted missing fatal assertion')


def read_red():
    run = W/SLOTS['red']; m = json.loads((run/'manifest.safe.json').read_bytes())
    begin = json.loads((run/'begin.safe.json').read_bytes()); guard_source(m['source'], 'red')
    if not (m['source'] == begin['source'] and m['actualExit'] == m['mavenActualExit'] == 1
            and m['phaseExits'] == [0, 0, 1] and m['sourceFixed'] and not m['selectedQualified']
            and (m['tests'], m['suites']) == (17, 6) and sha(run/'source.tar') == begin['archiveSha256']):
        raise ValueError('original exact purposeful red terminal and snapshot')
    xmls = {}; failures = set(); count = 0
    for path in (run/'source').glob('src/*/target/surefire-reports/TEST-*.xml'):
        root = ET.parse(path).getroot(); xmls[root.get('name')] = sha(path)
        for case in root.findall('testcase'):
            count += 1
            if any(n.tag in ('error', 'skipped', 'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError') for n in case.iter()):
                raise ValueError('unexpected error/skip/flaky, not counterexample')
            failed = case.find('failure')
            if failed is not None:
                method = case.get('name', '').split('(', 1)[0]
                if root.get('name') != 'dev.codex.schubert.nk.api.persistence.BorrowedJdbcFatal329Test':
                    raise ValueError('no unexpected core or baseline failure')
                validate_failure(method, failed); failures.add(method)
    if count != 17 or len(xmls) != 6 or failures != set(METHODS):
        raise ValueError('all nine exact actual original failures')
    value = dict(actualExit=0, originalExit=1, source=m['source'], run=run.name,
        originalManifestSha256=sha(run/'manifest.safe.json'), archiveSha256=begin['archiveSha256'],
        TestHashes={p: sha(run/'source'/p) for p in sorted(TESTS)}, tests=17, suites=6,
        expectedFailures=sorted(failures), xmlHashes=xmls, laterNotRun=6,
        testsExecutedByReader=0, formalAccepted=False, ptAlternativeCompleted=0, vmActions=0)
    out = BASE/'PG6550-borrowed-jdbc-original-red-v1'; os.umask(0o077); out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, redFailures=9, manifestSha256=sha(out/'manifest.json'))))


def qualify_green():
    run = W/SLOTS['green']; source = json.loads((run/'begin.safe.json').read_bytes())['source']
    guard_source(source, 'green'); cases, _ = inventory()
    return qualify(source, run, cases, (23, 9), MAINS,
        BASE/'PG6548-jdbc-transaction-qualification-v1/manifest.json',
        '979bb5c9283ded355130413afe1f2e0a6fff9a8a38905237c6f959cd8a39f18a',
        W/'pg6548-jdbc-transaction-qualification-v1/manifest.safe.json',
        W/'pg6548-jdbc-transaction-qualification-v1/findings.safe.json',
        'pg6554-borrowed-jdbc-qualification-v1', 'PG6554-borrowed-jdbc-qualification-v1',
        expected_phase_exits=(0, 0, 0))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=('red', 'green', 'read-red', 'qualify-green'))
    phase = parser.parse_args().phase
    if phase == 'read-red': return read_red()
    if phase == 'qualify-green': return qualify_green()
    cases, counts = inventory()
    return profile.execute(SLOTS[phase], lambda source: guard_source(source, phase), cases, counts, (23, 9), TARGETS)


if __name__ == '__main__':
    raise SystemExit(main())
