"""Current isolated failed expiry handoff; actual prior admission kept separate."""
import inspect
import json
from pyflakes.api import check
import pg2606_expiry_admission_selected as previous
import pg2220_root_uid_host_selected as transport
from pg2600_retention_group_full_six import SOURCE
from pg1446_current_cold_stage import W

FILES = [previous.FILES[0], 'tools/quality/vm/050_s1/Pg2608ExpiryHandoffLauncher.java', *previous.FILES[2:]]


def native_input():
    value = previous.native_input()
    receipt = json.loads((W / 'pg2606-expiry-admission-selected-v1/manifest.safe.json').read_bytes())
    if receipt['actualExit'] != 0 or receipt['source'] != SOURCE or receipt['classByteMismatch'] != 0:
        raise ValueError('actual current expiry admission required')
    value['expiryServerManifestSha256'] = receipt['manifestSha256']
    return value


def server():
    raw = previous.server().replace('PG2606', 'PG2608').replace(
        'Pg2606ExpiryAdmissionLauncher', 'Pg2608ExpiryHandoffLauncher')
    marker = "fixtures=source/'src/schubert-nk-batch/target/test-classes'"
    if raw.count(marker) != 1:
        raise ValueError('one fixture boundary required')
    extra = """expiry_root=b/'runs/PG2606-selected-v1'
require(sha(expiry_root/'manifest.safe.json')==INPUT['native']['expiryServerManifestSha256'])
expiry=json.loads((expiry_root/'manifest.safe.json').read_bytes())
require(expiry['actualExit']==0 and expiry['source']==INPUT['source'] and expiry['input']['full']['jarHashes']==INPUT['full']['jarHashes'])
expiry_exec=expiry_root/'selected.exec';require(sha(expiry_exec)==expiry['execSha256'])
"""
    raw = raw.replace(marker, extra + marker).replace('str(permit_exec),str(execfile)',
        'str(permit_exec),str(expiry_exec),str(execfile)')
    if check('INPUT={}\n' + raw, '<expiry handoff namespace>'):
        raise ValueError('whole namespace required')
    compile(raw, '<expiry handoff server>', 'exec')
    return raw


def main():
    raw = inspect.getsource(transport.main).replace('PG2220', 'PG2608').replace(
        'pg2220', 'pg2608').replace('pg2125-metadata-boundary-full-qualified-v1',
                                   'pg2601-retention-group-full-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    ns = {**transport.__dict__, 'SOURCE': SOURCE, 'FILES': FILES,
          'SLOT': 'pg2608-expiry-handoff-selected-v1', 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<fixed expiry handoff transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
