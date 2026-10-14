"""Actual successful-pair projections on the qualified unchanged Main/isolated DB."""
import inspect
import json
from pathlib import Path
from pyflakes.api import check
import pg2590_original_reinspection_selected as previous

FILES = [previous.FILES[0], 'tools/quality/vm/050_s1/Pg2592SuccessfulPairLauncher.java', *previous.FILES[2:]]


def native_input():
    value = previous.native_input()
    proof = json.loads(Path('evidence/01_PT/018_NK-OPS-001/evidence/strict-current-reference/original-reinspection-manifest-v3.json').read_bytes())
    if (type(proof.get('actualExit')) is not int or proof['actualExit'] != 0
            or proof['source'] != previous.previous.SOURCE or proof['tests'] != 1
            or proof['classByteMismatch'] != 0 or proof['FESAbortedNotRun'] != 0):
        raise ValueError('actual original reinspection qualification required')
    value['originalServerManifestSha256'] = proof['manifestSha256']
    return value


def server():
    raw = previous.server().replace('PG2590-selected-v3', 'PG2592-selected-v2').replace(
        'Pg2590OriginalReinspectionLauncher', 'Pg2592SuccessfulPairLauncher').replace(
        'PG2590', 'PG2592')
    marker = "fixtures=source/'src/schubert-nk-batch/target/test-classes'"
    if raw.count(marker) != 1:
        raise ValueError('one fixture boundary required')
    extra = """original_root=b/'runs/PG2590-selected-v3'
require(sha(original_root/'manifest.safe.json')==INPUT['native']['originalServerManifestSha256'])
original=json.loads((original_root/'manifest.safe.json').read_bytes())
require(original['actualExit']==0 and original['source']==INPUT['source'] and original['input']['full']['jarHashes']==INPUT['full']['jarHashes'])
original_exec=original_root/'selected.exec';require(sha(original_exec)==original['execSha256'])
"""
    raw = raw.replace(marker, extra + marker).replace('str(prior_exec),str(execfile)',
        'str(prior_exec),str(original_exec),str(execfile)')
    if check('INPUT={}\n' + raw, '<current successful pair namespace>'):
        raise ValueError('whole namespace required')
    compile(raw, '<current successful pair server>', 'exec')
    return raw


def main():
    transport = previous.previous.transport
    raw = inspect.getsource(transport.main).replace('PG2220', 'PG2592').replace(
        'pg2220', 'pg2592').replace('pg2125-metadata-boundary-full-qualified-v1',
                                   'pg2579-current-jdbc-group-full-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    raw = raw.replace('PG2592-selected-v1', 'PG2592-selected-v2')
    ns = {**transport.__dict__, 'SOURCE': previous.previous.SOURCE, 'FILES': FILES,
          'SLOT': 'pg2592-successful-pair-selected-v2', 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<fixed successful pair transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
