"""One required full3657 integration for four independently accepted JDBC boundaries."""
import ast
import hashlib
import inspect
import json
import subprocess
from pathlib import Path
import pg2578_current_jdbc_group_full_six as previous
from pg1446_current_cold_stage import W

SOURCE = previous.SOURCE
TEST = previous.TEST


def validate(snapshot):
    root = Path(__file__).resolve().parents[2]
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root)
    paths = git('diff', '--name-only', SOURCE, snapshot, '--', *previous.previous.SCOPE).decode().splitlines()
    if set(paths) != {TEST, previous.ARTIFACT}:
        raise ValueError('only accepted JDBC test source and actual A01 artifact permitted')
    previous.result_changes([previous.ARTIFACT], git('show', snapshot + ':' + previous.ARTIFACT),
        git('show', snapshot + ':' + previous.BASELINE),
        json.loads((W / 'pg2550-chr-a01-native-v1.safe.json').read_bytes()))
    receipt = json.loads((root / 'evidence/01_PT/018_NK-OPS-001/evidence/strict-current-reference/resume-admission-manifest.json').read_bytes())
    if (type(receipt.get('actualExit')) is not int or receipt['actualExit'] != 0
            or receipt['source'] != SOURCE or receipt['tests'] != 1
            or receipt['classByteMismatch'] != 0 or receipt['FESAbortedNotRun'] != 0):
        raise ValueError('actual same Main group closure required')
    payload = (W / 'pg2594-resume-admission-selected-v1/selected.private.py').read_bytes()
    if hashlib.sha256(payload).hexdigest() != receipt['payloadSha256']:
        raise ValueError('fixed selected payload required')
    inputs = ast.literal_eval(payload.decode().splitlines()[0].removeprefix('INPUT='))
    text = git('show', snapshot + ':' + TEST)
    if (inputs['source'] != SOURCE or inputs['head'] != receipt['testSource']
            or hashlib.sha256(text).hexdigest() != inputs['files']['MorningDatabaseSessionTest.java']):
        raise ValueError('exact selected whole test file required')
    for name in ['mdb2568001', 'mdb2570001', 'mdb2572001', 'mdb2588001', 'mdb2590001', 'mdb2592001', 'mdb2594001']:
        if ('void ' + name) not in text.decode():
            raise ValueError('all seven current JDBC methods required')


def server_source(head, digest):
    raw = previous.server_source(head, digest).replace('PG2578', 'PG2600').replace('3653', '3657')
    compile(raw, '<necessary four-method full3657>', 'exec')
    return raw


def main():
    transport = previous.previous.previous.previous.transport
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=transport.prior.ROOT, text=True).strip()
    validate(head)
    raw = inspect.getsource(transport.main)
    for before, after in [('PG1528', 'PG2600'), ('pg1528', 'pg2600'), ('3582', '3657'), ('524', '540'), ('1637', '1643')]:
        raw = raw.replace(before, after)
    raw = raw.replace('3578/523/1635 + LinuxFilesystemClassifier4 tests/one suite/two Main classes, other tests retained',
        '3653 retained plus four independently accepted JDBC boundary methods; unchanged Main540suite1643')
    raw = raw.replace('SSC269 new production storage/batch dependency and required all-source regression; selected attempts failed before target tests, literal NoTests gates preserved',
        'One required integration for2588/2590/2592/2594; no management-only repetition')
    ns = {**transport.__dict__, 'PRODUCTION': SOURCE, 'server_source': server_source}
    exec(compile(raw, '<retention grouped full transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
