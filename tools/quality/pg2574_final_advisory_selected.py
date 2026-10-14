"""Current immutable Main final advisory guard matrix, previous qualified execs only."""
import inspect
import json
from pathlib import Path
from pyflakes.api import check
import pg2572_reuse_pair_selected as previous
import pg2220_root_uid_host_selected as transport
from pg2564_strict_current_native_qualification import SOURCE

FILES = [previous.FILES[0], 'tools/quality/vm/050_s1/Pg2574FinalAdvisoryLauncher.java', *previous.FILES[2:]]


def native_input():
    value = previous.native_input()
    proof = json.loads(Path('evidence/01_PT/018_NK-OPS-001/evidence/strict-current-reference/reused-pair-manifest-v3.json').read_bytes())
    if (type(proof.get('actualExit')) is not int or proof['actualExit'] != 0
            or proof.get('source') != SOURCE or proof.get('tests') != 1
            or proof.get('FESAbortedNotRun') != 0 or proof.get('classByteMismatch') != 0):
        raise ValueError('actual same Main reuse qualification required')
    value['reuseServerManifestSha256'] = proof['manifestSha256']
    return value


def server():
    raw = previous.server().replace('PG2572-selected-v3', 'PG2574-selected-v1').replace(
        'PG2572', 'PG2574').replace('Pg2572ReusePairLauncher', 'Pg2574FinalAdvisoryLauncher')
    marker = "fixtures=source/'src/schubert-nk-batch/target/test-classes'"
    if raw.count(marker) != 1:
        raise ValueError('one frozen current fixture boundary required')
    extra = """reuse_root=b/'runs/PG2572-selected-v3'
require(sha(reuse_root/'manifest.safe.json')==INPUT['native']['reuseServerManifestSha256'])
reuse=json.loads((reuse_root/'manifest.safe.json').read_bytes())
require(reuse['actualExit']==0 and reuse['source']==INPUT['source'] and reuse['input']['full']['jarHashes']==INPUT['full']['jarHashes'])
reuse_exec=reuse_root/'selected.exec';require(sha(reuse_exec)==reuse['execSha256'])
"""
    raw = raw.replace(marker, extra + marker).replace('str(guard_exec),str(execfile)',
        'str(guard_exec),str(reuse_exec),str(execfile)')
    if check('INPUT={}\n' + raw, '<current final advisory namespace>'):
        raise ValueError('whole selected namespace required')
    compile(raw, '<current advisory selected>', 'exec')
    return raw


def main():
    raw = inspect.getsource(transport.main).replace('PG2220', 'PG2574').replace(
        'pg2220', 'pg2574').replace('pg2125-metadata-boundary-full-qualified-v1',
                                   'pg2511-strict-reference-full-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    ns = {**transport.__dict__, 'SOURCE': SOURCE, 'FILES': FILES,
          'SLOT': 'pg2574-final-advisory-selected-v1', 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<fixed advisory actual transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
