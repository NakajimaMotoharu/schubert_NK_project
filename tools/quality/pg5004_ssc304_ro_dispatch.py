"""One stage or prepare-ro, authenticated fresh local forward; no publication."""
import sys
import pg4876_ssc301_302_ro_dispatch as previous
import pg5000_ssc304_ro_sources as role
from pg5002_ssc304_ro_compile import TARGET, generated
from pg4996_resume_connection import authenticate_host

GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS
REMOTE = '/home/ubuntu/pg5004-fixed-stage-v2'
STAGE = (previous.STAGE.replace(previous.GUEST, GUEST).replace(previous.REMOTE, REMOTE)
         .replace('0.1.0-PG4702', '0.1.0-PG4860')
         .replace('pg4872-ssc301-302-ro-tools-v1.tar', 'pg5000-ssc304-ro-tools-v1.retry2.tar'))


def entry_source():
    raw = previous.entry_source()
    for a, b in [('pg4876', 'pg5004'), ('pg4874', 'pg5002'), ('Pg4872', 'Pg5000'), ('PG4702', 'PG4860')]:
        raw = raw.replace(a, b)
    marker = "archive=P/(role.TOOLS+'.tar')"
    if raw.count(marker) != 1:
        raise ValueError('one new-only retry archive boundary')
    raw = raw.replace(marker, "archive=P/(role.TOOLS+'.retry2.tar')", 1)
    raw = raw.replace("('pg5004-'+action+'-v1')", "('pg5004-'+action+'-v2')")
    raw = raw.replace('pg5004-stage-v1.exit', 'pg5004-stage-v2.exit')
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
