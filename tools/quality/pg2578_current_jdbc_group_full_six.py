"""One necessary full campaign for three new JDBC tests, not a management-only repetition."""
import ast
import hashlib
import inspect
import json
import subprocess
from pathlib import Path
import pg2510_strict_reference_full_six as previous
from pg2564_strict_current_native_qualification import ARTIFACT, result_changes
from pg1446_current_cold_stage import W

SOURCE = previous.SOURCE
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSessionTest.java'
BASELINE = 'program/characterization/baseline/current/artifacts/CHR-A01.json'


def validate(snapshot):
    root = Path(__file__).resolve().parents[2]
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root)
    paths = git('diff', '--name-only', SOURCE, snapshot, '--', *previous.SCOPE).decode().splitlines()
    if set(paths) != {TEST, ARTIFACT}:
        raise ValueError('only independently qualified JDBC test and actual A01 result required')
    result_changes([ARTIFACT], git('show', snapshot + ':' + ARTIFACT), git('show', snapshot + ':' + BASELINE),
                   json.loads((W / 'pg2550-chr-a01-native-v1.safe.json').read_bytes()))
    receipt = json.loads((root / 'evidence/01_PT/018_NK-OPS-001/evidence/strict-current-reference/final-advisory-manifest.json').read_bytes())
    if (type(receipt.get('actualExit')) is not int or receipt['actualExit'] != 0
            or receipt.get('source') != SOURCE or receipt.get('classByteMismatch') != 0
            or receipt.get('tests') != 1 or receipt.get('FESAbortedNotRun') != 0):
        raise ValueError('actual same Main selected result required')
    payload = (W / 'pg2574-final-advisory-selected-v1/selected.private.py').read_bytes()
    if hashlib.sha256(payload).hexdigest() != receipt['payloadSha256']:
        raise ValueError('actual selected input hash required')
    inputs = ast.literal_eval(payload.decode().splitlines()[0].removeprefix('INPUT='))
    if inputs['source'] != SOURCE or inputs['head'] != receipt['testSource']:
        raise ValueError('selected source and operator must match actual result')
    if hashlib.sha256(git('show', snapshot + ':' + TEST)).hexdigest() != inputs['files']['MorningDatabaseSessionTest.java']:
        raise ValueError('whole selected test source unchanged required')
    text = git('show', snapshot + ':' + TEST).decode()
    for name in ['mdb2568001', 'mdb2570001', 'mdb2572001']:
        if ('void ' + name) not in text:
            raise ValueError('all three independently tested methods required')


def server_source(head, digest):
    raw = previous.server_source(head, digest).replace('PG2510', 'PG2578').replace('3650', '3653')
    compile(raw, '<necessary three-method full3653>', 'exec')
    return raw


def main():
    transport = previous.previous.previous.transport
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=transport.prior.ROOT, text=True).strip()
    validate(head)
    raw = inspect.getsource(transport.main)
    for before, after in [('PG1528', 'PG2578'), ('pg1528', 'pg2578'), ('3582', '3653'), ('524', '540'), ('1637', '1643')]:
        raw = raw.replace(before, after)
    raw = raw.replace('3578/523/1635 + LinuxFilesystemClassifier4 tests/one suite/two Main classes, other tests retained',
        '3650 retained plus three independently tested JDBC methods; Main unchanged; 540suite/1643Main')
    raw = raw.replace('SSC269 new production storage/batch dependency and required all-source regression; selected attempts failed before target tests, literal NoTests gates preserved',
        'One necessary integration of2568/2570-expanded17/2572 boundary group; no management-only repeated campaign')
    ns = {**transport.__dict__, 'PRODUCTION': SOURCE, 'server_source': server_source}
    exec(compile(raw, '<grouped JDBC full transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
