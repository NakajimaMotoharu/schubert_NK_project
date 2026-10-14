"""Frozen literal cleanup readback selection, reusable tool not a Production port."""
import inspect
import json
from pyflakes.api import check
import pg2608_expiry_handoff_selected as previous
import pg2220_root_uid_host_selected as transport
from pg2600_retention_group_full_six import SOURCE
from pg1446_current_cold_stage import W

FILES = [previous.FILES[0], 'tools/quality/vm/050_s1/IsolatedJdbcSelectedLauncher.java', *previous.FILES[2:]]
METHOD = 'mdb2610001CleanupReadbackRejectsDbDriftReceiptAndBackupModeWithoutMutation'


def native_input():
    value = previous.native_input()
    receipt = json.loads((W / 'pg2608-expiry-handoff-selected-v1/manifest.safe.json').read_bytes())
    if receipt['actualExit'] != 0 or receipt['source'] != SOURCE or receipt['classByteMismatch'] != 0:
        raise ValueError('actual current expiry handoff required')
    value['handoffServerManifestSha256'] = receipt['manifestSha256']
    return value


def server():
    raw = previous.server().replace('PG2608', 'PG2610').replace(
        'Pg2608ExpiryHandoffLauncher', 'IsolatedJdbcSelectedLauncher')
    marker = "'IsolatedJdbcSelectedLauncher',str(xml)]"
    if raw.count(marker) != 1:
        raise ValueError('one fixed launcher call required')
    raw = raw.replace(marker, "'IsolatedJdbcSelectedLauncher',str(xml),'PG2610','dev.codex.schubert.nk.batch.repository.MorningExpirySessionTest'," + repr(METHOD) + "]")
    marker = "fixtures=source/'src/schubert-nk-batch/target/test-classes'"
    if raw.count(marker) != 1:
        raise ValueError('one fixture boundary required')
    extra = """handoff_root=b/'runs/PG2608-selected-v1'
require(sha(handoff_root/'manifest.safe.json')==INPUT['native']['handoffServerManifestSha256'])
handoff=json.loads((handoff_root/'manifest.safe.json').read_bytes())
require(handoff['actualExit']==0 and handoff['source']==INPUT['source'] and handoff['input']['full']['jarHashes']==INPUT['full']['jarHashes'])
handoff_exec=handoff_root/'selected.exec';require(sha(handoff_exec)==handoff['execSha256'])
"""
    raw = raw.replace(marker, extra + marker).replace('str(expiry_exec),str(execfile)',
        'str(expiry_exec),str(handoff_exec),str(execfile)')
    if check('INPUT={}\n' + raw, '<cleanup readback namespace>'):
        raise ValueError('whole namespace required')
    compile(raw, '<cleanup readback server>', 'exec')
    return raw


def main():
    raw = inspect.getsource(transport.main).replace('PG2220', 'PG2610').replace(
        'pg2220', 'pg2610').replace('pg2125-metadata-boundary-full-qualified-v1',
                                   'pg2601-retention-group-full-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    ns = {**transport.__dict__, 'SOURCE': SOURCE, 'FILES': FILES,
          'SLOT': 'pg2610-cleanup-readback-selected-v1', 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<fixed cleanup readback transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
