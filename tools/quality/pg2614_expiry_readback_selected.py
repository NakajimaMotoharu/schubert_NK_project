"""Current real RUNNING expiry cannot become a successful typed receipt readback."""
import inspect
import json
from pyflakes.api import check
import pg2612_cleanup_references_selected as previous
import pg2220_root_uid_host_selected as transport
from pg2600_retention_group_full_six import SOURCE
from pg1446_current_cold_stage import W

FILES = previous.FILES
METHOD = 'mdb2614001ExpiryReadbackRejectsRunningWrongTargetAndDbDriftWithoutMutation'


def native_input():
    value = previous.native_input()
    receipt = json.loads((W / 'pg2612-cleanup-references-selected-v1/manifest.safe.json').read_bytes())
    if receipt['actualExit'] != 0 or receipt['source'] != SOURCE or receipt['classByteMismatch'] != 0:
        raise ValueError('actual current reference readback required')
    value['referenceServerManifestSha256'] = receipt['manifestSha256']
    return value


def server():
    raw = previous.server().replace('PG2612', 'PG2614').replace(previous.METHOD, METHOD)
    marker = "fixtures=source/'src/schubert-nk-batch/target/test-classes'"
    if raw.count(marker) != 1:
        raise ValueError('one fixture boundary required')
    extra = """reference_root=b/'runs/PG2612-selected-v1'
require(sha(reference_root/'manifest.safe.json')==INPUT['native']['referenceServerManifestSha256'])
reference=json.loads((reference_root/'manifest.safe.json').read_bytes())
require(reference['actualExit']==0 and reference['source']==INPUT['source'] and reference['input']['full']['jarHashes']==INPUT['full']['jarHashes'])
reference_exec=reference_root/'selected.exec';require(sha(reference_exec)==reference['execSha256'])
"""
    raw = raw.replace(marker, extra + marker).replace('str(cleanup_exec),str(execfile)',
        'str(cleanup_exec),str(reference_exec),str(execfile)')
    if check('INPUT={}\n' + raw, '<expiry readback namespace>'):
        raise ValueError('whole namespace required')
    compile(raw, '<expiry readback server>', 'exec')
    return raw


def main():
    raw = inspect.getsource(transport.main).replace('PG2220', 'PG2614').replace(
        'pg2220', 'pg2614').replace('pg2125-metadata-boundary-full-qualified-v1',
                                   'pg2601-retention-group-full-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    ns = {**transport.__dict__, 'SOURCE': SOURCE, 'FILES': FILES,
          'SLOT': 'pg2614-expiry-readback-selected-v1', 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<fixed expiry readback transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
