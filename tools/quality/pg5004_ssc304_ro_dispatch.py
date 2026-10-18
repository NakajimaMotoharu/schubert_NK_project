"""One stage or prepare-ro, authenticated fresh local forward; no publication."""
import sys
import pg4876_ssc301_302_ro_dispatch as previous
import pg5000_ssc304_ro_sources as role
from pg5002_ssc304_ro_compile import TARGET, generated
from pg4996_resume_connection import authenticate_host

GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS
REMOTE = '/home/ubuntu/pg5004-fixed-stage-v1'
STAGE = previous.STAGE.replace(previous.GUEST, GUEST).replace(previous.REMOTE, REMOTE)


def entry_source():
    raw = previous.entry_source()
    for a, b in [('pg4876', 'pg5004'), ('pg4874', 'pg5002'), ('Pg4872', 'Pg5000'), ('PG4702', 'PG4860')]:
        raw = raw.replace(a, b)
    return raw


def main():
    if sys.argv[1:] not in (['stage'], ['prepare-ro']):
        raise ValueError('one explicit RO stage/prepare only')
    authenticate_host()
    ns = {**vars(previous.previous.previous), '__file__': __file__, 'role': role,
          'TARGET': TARGET, 'generated': generated, 'GUEST': GUEST, 'REMOTE': REMOTE, 'STAGE': STAGE}
    exec(compile(entry_source(), '<actual04bb/candidatea2ecc RO>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
