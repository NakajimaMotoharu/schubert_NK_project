"""Current isolated expiry admission rejects foreign run and transaction drift."""
import inspect
import json
from pathlib import Path
from pyflakes.api import check
import pg2604_permit_database_selected as previous

FILES = [previous.FILES[0], 'tools/quality/vm/050_s1/Pg2606ExpiryAdmissionLauncher.java', *previous.FILES[2:]]


def native_input():
    value = previous.native_input()
    proof = json.loads(Path('evidence/01_PT/018_NK-OPS-001/evidence/strict-current-reference/permit-database-manifest.json').read_bytes())
    if proof['actualExit'] != 0 or proof['source'] != previous.SOURCE or proof['classByteMismatch'] != 0:
        raise ValueError('same Main actual permit DB qualification required')
    value['permitServerManifestSha256'] = proof['manifestSha256']
    return value


def server():
    raw = previous.server().replace('PG2604', 'PG2606').replace(
        'Pg2604PermitDatabaseLauncher', 'Pg2606ExpiryAdmissionLauncher')
    marker = "fixtures=source/'src/schubert-nk-batch/target/test-classes'"
    if raw.count(marker) != 1:
        raise ValueError('one fixture boundary required')
    extra = """permit_root=b/'runs/PG2604-selected-v1'
require(sha(permit_root/'manifest.safe.json')==INPUT['native']['permitServerManifestSha256'])
permit=json.loads((permit_root/'manifest.safe.json').read_bytes())
require(permit['actualExit']==0 and permit['source']==INPUT['source'] and permit['input']['full']['jarHashes']==INPUT['full']['jarHashes'])
permit_exec=permit_root/'selected.exec';require(sha(permit_exec)==permit['execSha256'])
"""
    raw = raw.replace(marker, extra + marker).replace('str(prior_exec),str(execfile)',
        'str(prior_exec),str(permit_exec),str(execfile)')
    if check('INPUT={}\n' + raw, '<expiry admission namespace>'):
        raise ValueError('whole namespace required')
    compile(raw, '<expiry admission server>', 'exec')
    return raw


def main():
    transport = previous.previous.previous.previous.previous.transport
    raw = inspect.getsource(transport.main).replace('PG2220', 'PG2606').replace(
        'pg2220', 'pg2606').replace('pg2125-metadata-boundary-full-qualified-v1',
                                   'pg2601-retention-group-full-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    ns = {**transport.__dict__, 'SOURCE': previous.SOURCE, 'FILES': FILES,
          'SLOT': 'pg2606-expiry-admission-selected-v1', 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<fixed expiry admission transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
