"""Exact snapshot readback and original references against current immutable Main."""
import inspect
import json
from pyflakes.api import check
import pg2610_cleanup_readback_selected as previous
import pg2220_root_uid_host_selected as transport
from pg2600_retention_group_full_six import SOURCE
from pg1446_current_cold_stage import W

FILES = previous.FILES
METHOD = 'mdb2612001CleanupReferencesRejectDriftAndForgedSnapshotWithoutChangingRows'


def native_input():
    value = previous.native_input()
    receipt = json.loads((W / 'pg2610-cleanup-readback-selected-v1/manifest.safe.json').read_bytes())
    if receipt['actualExit'] != 0 or receipt['source'] != SOURCE or receipt['classByteMismatch'] != 0:
        raise ValueError('actual current cleanup readback required')
    value['cleanupServerManifestSha256'] = receipt['manifestSha256']
    return value


def server():
    raw = previous.server().replace('PG2610', 'PG2612').replace(previous.METHOD, METHOD)
    marker = "fixtures=source/'src/schubert-nk-batch/target/test-classes'"
    if raw.count(marker) != 1:
        raise ValueError('one fixture boundary required')
    extra = """cleanup_root=b/'runs/PG2610-selected-v1'
require(sha(cleanup_root/'manifest.safe.json')==INPUT['native']['cleanupServerManifestSha256'])
cleanup=json.loads((cleanup_root/'manifest.safe.json').read_bytes())
require(cleanup['actualExit']==0 and cleanup['source']==INPUT['source'] and cleanup['input']['full']['jarHashes']==INPUT['full']['jarHashes'])
cleanup_exec=cleanup_root/'selected.exec';require(sha(cleanup_exec)==cleanup['execSha256'])
"""
    raw = raw.replace(marker, extra + marker).replace('str(handoff_exec),str(execfile)',
        'str(handoff_exec),str(cleanup_exec),str(execfile)')
    if check('INPUT={}\n' + raw, '<cleanup references namespace>'):
        raise ValueError('whole namespace required')
    compile(raw, '<cleanup references server>', 'exec')
    return raw


def main():
    raw = inspect.getsource(transport.main).replace('PG2220', 'PG2612').replace(
        'pg2220', 'pg2612').replace('pg2125-metadata-boundary-full-qualified-v1',
                                   'pg2601-retention-group-full-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    ns = {**transport.__dict__, 'SOURCE': SOURCE, 'FILES': FILES,
          'SLOT': 'pg2612-cleanup-references-selected-v1', 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<fixed cleanup references transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
