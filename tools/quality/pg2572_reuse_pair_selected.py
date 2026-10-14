"""Fresh isolated reused-pair integrity; unchanged Main/current native/prior guards."""
import inspect
import json
from pathlib import Path
from pyflakes.api import check
import pg2570_failed_guard_selected as previous

FILES = [previous.FILES[0], 'tools/quality/vm/050_s1/Pg2572ReusePairLauncher.java', *previous.FILES[2:]]


def native_input():
    value = previous.native_input()
    proof = json.loads(Path('evidence/01_PT/018_NK-OPS-001/evidence/strict-current-reference/final-guard-manifest-v2.json').read_bytes())
    if (type(proof.get('actualExit')) is not int or proof['actualExit'] != 0
            or proof.get('source') != previous.previous.SOURCE or proof.get('tests') != 1
            or proof.get('FESAbortedNotRun') != 0 or proof.get('classByteMismatch') != 0):
        raise ValueError('actual same Main final guard proof required')
    value['guardServerManifestSha256'] = proof['manifestSha256']
    return value


def server():
    raw = previous.server().replace('PG2570-selected-v2', 'PG2572-selected-v1').replace(
        'PG2570', 'PG2572').replace('Pg2570FailedGuardLauncher', 'Pg2572ReusePairLauncher')
    marker = "fixtures=source/'src/schubert-nk-batch/target/test-classes'"
    if raw.count(marker) != 1:
        raise ValueError('one frozen fixture scope required')
    extra = """guard_root=b/'runs/PG2570-selected-v2'
require(sha(guard_root/'manifest.safe.json')==INPUT['native']['guardServerManifestSha256'])
guard=json.loads((guard_root/'manifest.safe.json').read_bytes())
require(guard['actualExit']==0 and guard['source']==INPUT['source'] and guard['input']['full']['jarHashes']==INPUT['full']['jarHashes'])
guard_exec=guard_root/'selected.exec';require(sha(guard_exec)==guard['execSha256'])
"""
    raw = raw.replace(marker, extra + marker).replace('str(prior_exec),str(execfile)',
        'str(prior_exec),str(guard_exec),str(execfile)')
    raw = raw.replace("'fixturesUnchanged':True", "'fixturesUnchanged':True,'guardSelectedExecSha256':sha(guard_exec)")
    if check('INPUT={}\n' + raw, '<whole fresh reused pair selected>'):
        raise ValueError('whole namespace required')
    compile(raw, '<fresh reused pair>', 'exec')
    return raw


def main():
    raw = inspect.getsource(previous.previous.previous.prior.main).replace('PG2220', 'PG2572').replace(
        'pg2220', 'pg2572').replace('pg2125-metadata-boundary-full-qualified-v1',
                                   'pg2511-strict-reference-full-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    ns = {**previous.previous.previous.prior.__dict__, 'SOURCE': previous.previous.SOURCE,
          'FILES': FILES, 'SLOT': 'pg2572-reuse-pair-selected-v1', 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<fresh reuse pair immutable transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
