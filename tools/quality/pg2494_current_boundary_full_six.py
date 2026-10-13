"""One grouped full regression for twelve independently tested current boundary methods."""
import hashlib
import inspect
import json
import subprocess
import pg2404_question_jdbc_full_six as previous
from pg2474_question_native_qualified_results import ARTIFACT, BASELINE, result_changes

SOURCE = 'cdbc07cdf77370d521e64de8b327da7f6752139b'
TESTS = {
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/BrokerJournalEvidenceTest.java':
        'evidence/01_PT/018_NK-OPS-001/evidence/current-broker-journal-boundaries/manifest-v4.json',
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSessionTest.java':
        'evidence/01_PT/018_NK-OPS-001/evidence/current-jdbc-backup-boundaries/manifest-2490-v2.json'}


def production():
    return SOURCE


def validate(snapshot):
    root = previous.transport.prior.ROOT
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root)
    paths = git('diff', '--name-only', SOURCE, snapshot, '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization').decode().splitlines()
    if set(paths) != set(TESTS) | {ARTIFACT}:
        raise ValueError('only two explicitly qualified test files and actual A01 result required')
    receipt = json.loads((previous.transport.prior.W / 'pg2470-chr-a01-native-v1.safe.json').read_bytes())
    result_changes([ARTIFACT], git('show', snapshot + ':' + ARTIFACT), git('show', snapshot + ':' + BASELINE), receipt)
    for name, path in TESTS.items():
        m = json.loads((root / path).read_bytes())
        if type(m.get('actualExit')) is not int or m['actualExit'] != 0 or m.get('source') != SOURCE or type(m.get('FESAbortedNotRun')) is not int or m['FESAbortedNotRun'] != 0:
            raise ValueError('actual independently tested same Main required')
        coverage = m.get('coverage', {})
        if set(coverage) != {'protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'} or any(type(v.get('classByteMismatch')) is not int or v['classByteMismatch'] != 0 for v in coverage.values()):
            raise ValueError('six actual CRC measurements required')
        if hashlib.sha256(git('show', snapshot + ':' + name)).hexdigest() != m['inputFiles'][name.rsplit('/', 1)[-1]]:
            raise ValueError('exact latest selected test source required')
    broker = git('show', snapshot + ':' + next(iter(TESTS))).decode()
    jdbc = git('show', snapshot + ':' + list(TESTS)[1]).decode()
    expected = ['bj247800' + str(n) for n in range(1, 5)]
    expected += ['mdb' + str(run) + '00' + str(n) for run in [2480, 2482, 2486, 2490] for n in [1, 2]]
    if any(('void ' + name) not in broker + jdbc for name in expected):
        raise ValueError('all twelve named independent methods required')


def server_source(head, digest):
    raw = previous.server_source(head, digest).replace('PG2404', 'PG2494').replace('3637', '3649')
    compile(raw, '<PG2494 necessary grouped full>', 'exec')
    return raw


def main():
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=previous.transport.prior.ROOT, text=True).strip()
    validate(head)
    raw = inspect.getsource(previous.transport.main)
    for a, b in [('PG1528', 'PG2494'), ('pg1528', 'pg2494'), ('3582', '3649'), ('524', '540'), ('1637', '1643')]:
        raw = raw.replace(a, b)
    raw = raw.replace('3578/523/1635 + LinuxFilesystemClassifier4 tests/one suite/two Main classes, other tests retained',
                      '3637/540/1643 current full plus twelve boundary methods in two existing suites; Main/resources unchanged')
    raw = raw.replace('SSC269 new production storage/batch dependency and required all-source regression; selected attempts failed before target tests, literal NoTests gates preserved',
                      'One grouped integration of PG2478/2480/2482/2486/2490 new independent boundary tests; no management-only full repetition')
    namespace = {**previous.transport.__dict__, 'PRODUCTION': SOURCE, 'server_source': server_source}
    exec(compile(raw, '<PG2494 full transport>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
