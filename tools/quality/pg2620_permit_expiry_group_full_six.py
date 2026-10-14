"""Required six-method DB ownership integration, frozen3663/current Main unchanged."""
import ast
import hashlib
import inspect
import json
import subprocess
from pathlib import Path
import pg2600_retention_group_full_six as previous
from pg1446_current_cold_stage import W

SOURCE = previous.SOURCE
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningExpirySessionTest.java'


def validate(snapshot):
    root = Path(__file__).resolve().parents[2]
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root)
    full = json.loads((W / 'pg2601-retention-group-full-qualified-v1/manifest.safe.json').read_bytes())
    if full['actualExit'] != 0 or full['result']['tests'] != 3657 or full['result']['productionSource'] != SOURCE:
        raise ValueError('actual fixed3657 baseline required')
    original = full['result']['sourceSnapshot']
    previous.validate(original)
    if git('show', snapshot + ':' + previous.TEST) != git('show', original + ':' + previous.TEST):
        raise ValueError('previous seven JDBC tests unchanged required')
    paths = git('diff', '--name-only', SOURCE, snapshot, '--', *previous.previous.previous.SCOPE).decode().splitlines()
    if set(paths) != {previous.TEST, TEST, previous.previous.ARTIFACT}:
        raise ValueError('only two accepted test paths and real A01 result permitted')
    if git('show', snapshot + ':' + previous.previous.ARTIFACT) != git('show', original + ':' + previous.previous.ARTIFACT):
        raise ValueError('independently accepted A01 unchanged required')
    receipt = json.loads((W / 'pg2614-expiry-readback-selected-v1/manifest.safe.json').read_bytes())
    if (type(receipt['actualExit']) is not int or receipt['actualExit'] != 0
            or receipt['source'] != SOURCE or receipt['classByteMismatch'] != 0
            or receipt['tests'] != 1 or receipt['FESAbortedNotRun'] != 0):
        raise ValueError('actual group closure selection required')
    payload = (W / 'pg2614-expiry-readback-selected-v1/selected.private.py').read_bytes()
    if hashlib.sha256(payload).hexdigest() != receipt['payloadSha256']:
        raise ValueError('exact selected payload required')
    inputs = ast.literal_eval(payload.decode().splitlines()[0].removeprefix('INPUT='))
    text = git('show', snapshot + ':' + TEST)
    if (inputs['source'] != SOURCE or inputs['head'] != receipt['testSource']
            or hashlib.sha256(text).hexdigest() != inputs['files']['MorningExpirySessionTest.java']):
        raise ValueError('whole selected Test file required')
    for name in ['mdb2604001', 'mdb2606001', 'mdb2608001', 'mdb2610001', 'mdb2612001', 'mdb2614001']:
        if ('void ' + name) not in text.decode():
            raise ValueError('all six accepted methods required')


def server_source(head, digest):
    raw = previous.server_source(head, digest).replace('PG2600', 'PG2620').replace('3657', '3663')
    compile(raw, '<necessary six-method full3663>', 'exec')
    return raw


def main():
    raw = inspect.getsource(previous.main).replace('PG2600', 'PG2620').replace('pg2600', 'pg2620').replace('3657', '3663')
    raw = raw.replace('3653 retained plus four independently accepted JDBC boundary methods; unchanged Main540suite1643',
        '3657 retained plus six independently accepted permit-expiry-cleanup methods; Main unchanged540suite1643')
    raw = raw.replace('One required integration for2588/2590/2592/2594; no management-only repetition',
        'One required integration for2604/2606/2608/2610/2612/2614; no management-only repetition')
    ns = {**previous.__dict__, 'validate': validate, 'server_source': server_source, 'SOURCE': SOURCE}
    exec(compile(raw, '<six-method frozen full transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
