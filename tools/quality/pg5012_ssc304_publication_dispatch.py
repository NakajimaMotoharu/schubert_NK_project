"""One finite stage/activate only; same original/current safety and exact tool kind."""
import inspect
import sys
import pg4884_ssc301_302_publication_dispatch as previous
import pg5008_ssc304_publication_sources as role
from pg5010_ssc304_publication_compile import TARGET, generated
from pg4996_resume_connection import authenticate_host

GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS
REMOTE = '/home/ubuntu/pg5012-ssc304-publication-stage-v1'
STAGE = role.ro.unused.normalized_text(previous.STAGE)
STAGE = (STAGE.replace(previous.GUEST, GUEST).replace(previous.REMOTE, REMOTE)
         .replace('pg4880-ssc301-302-publication-tools-v1.tar', role.TOOLS + '.tar'))


def qualify_fixed(fixed):
    if type(fixed.get('actualExit')) is not int:
        raise ValueError('actual numeric fixed qualification')
    template = previous.previous.previous
    ns = {**vars(template), 'role': role}
    raw = inspect.getsource(template.qualify_fixed)
    for a, b in [('Pg3788', 'Pg5008'), ('pg3788', 'pg5008'), ('Pg3780', 'Pg5000'), ('pg3780', 'pg5000')]:
        raw = raw.replace(a, b)
    exec(compile(raw, '<exact finite target and bound graph>', 'exec'), ns)
    return ns['qualify_fixed'](fixed)


def source():
    raw = previous.source()
    for a, b in [('pg4884', 'pg5012'), ('pg4882', 'pg5010'), ('Pg4880', 'Pg5008'), ('PG4702', 'PG4860')]:
        raw = raw.replace(a, b)
    return raw


def main():
    if sys.argv[1:] not in (['stage'], ['activate']):
        raise ValueError('one finite stage/activate only')
    authenticate_host()
    ns = {**vars(previous.previous.previous.previous), '__file__': __file__, 'role': role,
          'TARGET': TARGET, 'generated': generated, 'GUEST': GUEST, 'REMOTE': REMOTE,
          'STAGE': STAGE, 'qualify_fixed': qualify_fixed}
    exec(compile(source(), '<actual04bb finitea2ecc publication>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
