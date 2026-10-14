"""Isolated resume rejects incompatible original claims and failed commit, unchanged Main."""
import inspect
import json
from pathlib import Path
from pyflakes.api import check
import pg2592_successful_pair_selected as previous

FILES = [previous.FILES[0], 'tools/quality/vm/050_s1/Pg2594ResumeAdmissionLauncher.java', *previous.FILES[2:]]


def native_input():
    value = previous.native_input()
    proof = json.loads(Path('evidence/01_PT/018_NK-OPS-001/evidence/strict-current-reference/successful-pair-manifest-v2.json').read_bytes())
    if proof['actualExit'] != 0 or proof['source'] != previous.previous.previous.SOURCE or proof['classByteMismatch'] != 0:
        raise ValueError('same Main successful pair qualification required')
    value['pairServerManifestSha256'] = proof['manifestSha256']
    return value


def server():
    raw = previous.server().replace('PG2592-selected-v2', 'PG2594-selected-v1').replace(
        'Pg2592SuccessfulPairLauncher', 'Pg2594ResumeAdmissionLauncher').replace('PG2592', 'PG2594')
    marker = "fixtures=source/'src/schubert-nk-batch/target/test-classes'"
    if raw.count(marker) != 1:
        raise ValueError('one fixture boundary required')
    extra = """pair_root=b/'runs/PG2592-selected-v2'
require(sha(pair_root/'manifest.safe.json')==INPUT['native']['pairServerManifestSha256'])
pair=json.loads((pair_root/'manifest.safe.json').read_bytes())
require(pair['actualExit']==0 and pair['source']==INPUT['source'] and pair['input']['full']['jarHashes']==INPUT['full']['jarHashes'])
pair_exec=pair_root/'selected.exec';require(sha(pair_exec)==pair['execSha256'])
"""
    raw = raw.replace(marker, extra + marker).replace('str(original_exec),str(execfile)',
        'str(original_exec),str(pair_exec),str(execfile)')
    if check('INPUT={}\n' + raw, '<current resume admission namespace>'):
        raise ValueError('whole namespace required')
    compile(raw, '<current resume admission server>', 'exec')
    return raw


def main():
    transport = previous.previous.previous.transport
    raw = inspect.getsource(transport.main).replace('PG2220', 'PG2594').replace(
        'pg2220', 'pg2594').replace('pg2125-metadata-boundary-full-qualified-v1',
                                   'pg2579-current-jdbc-group-full-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    ns = {**transport.__dict__, 'SOURCE': previous.previous.previous.SOURCE, 'FILES': FILES,
          'SLOT': 'pg2594-resume-admission-selected-v1', 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<fixed resume admission transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
