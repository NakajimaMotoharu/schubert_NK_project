"""New reserved immutable stage/place for current-DONE unused candidate only.

No epoch/current/approval mutation, reload/start/stop, SQL or backup operation.
The signed input and every helper byte are frozen. No same-slot retry.
"""
import inspect
import json
import sys
import pg1295_completed_unused_stage_dispatch as previous
import pg1645_completed_candidate_compile_v2 as compiler
from pg1640_completed_unused_candidate_sources import BEFORE
from pg1630_api_terminal_selected import PRODUCTION

GUEST = '/var/lib/pgpt-s1-preservation/pg1645-completed-unused-tools-v2'
REMOTE = '/home/ubuntu/pg1646-candidate-input-v1'
STAGE = previous.STAGE.replace('pg1295', 'pg1646').replace('PG1295', 'PG1646').replace('pg1293-native-tools-v1', 'pg1645-completed-unused-tools-v2')
STAGE = STAGE.replace('cbca8738-3b24-4090-b77c-bf029677cdd6', '3d69f5af-6bac-46b1-a540-7591c4a79a0d').replace('PG1068', 'PG1544')


def source():
    raw = inspect.getsource(previous.main)
    replacements = [('pg1293-native-tools-v1', 'pg1645-completed-unused-tools-v2'), ('pg1294-frozen-v1.safe.json', 'pg1645-frozen-v1.safe.json'), ('pg1296-current-readonly-v1.safe.json', 'pg1641-completed-current-before-v2/manifest.safe.json'), ('pg1295-release-v1.tar', 'pg1646-release-v2.tar'), ('pg1292-manifest-v1.sig', 'pg1638-manifest-v1.sig'), ('pg1293-native-tools-v1.tar', 'pg1645-completed-unused-tools-v2.tar'), ('pg1295', 'pg1646'), ('Pg1293', 'Pg1640'), ('pg1293_native_refs.py', 'pg1640_native_refs.py'), ('PG1068', 'PG1544'), ('PG1292', 'PG1638'), ('pg1292-manifest.sig', 'pg1638-manifest.sig')]
    for a, b in replacements:
        raw = raw.replace(a, b)
    raw = raw.replace("['git','diff','--name-only',SOURCE,'--','src','pom.xml']", "['git','diff','--name-only','1683dd9f6de00e71d2317d9af3cd50400a37bf4e','--','src','pom.xml']")
    raw = raw.replace('generated=sources()', 'generated=sources(DIGEST)')
    compile(raw, '<reserved completed current placement>', 'exec')
    return raw


def main():
    if sys.argv[1:] not in (['stage'], ['place']):
        raise ValueError('closed stage/place required')
    candidate = json.loads((previous.W / 'pg1638-candidate-build-v1.safe.json').read_bytes())
    if candidate['actualExit'] != 0 or candidate['candidateSource'] != PRODUCTION:
        raise ValueError('actual independently qualified candidate required')
    ns = {**previous.__dict__, 'SOURCE': PRODUCTION, 'DIGEST': candidate['manifestSha256'], 'BASELINE_SHA': BEFORE, 'GUEST': GUEST, 'REMOTE': REMOTE, 'STAGE': STAGE, 'sources': compiler.sources}
    exec(compile(source(), '<new currentDONE placement dispatcher>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
