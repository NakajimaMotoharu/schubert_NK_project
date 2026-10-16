"""Exactly one new stage/prepare-ro action; no current publication or business starts."""
import inspect
import pg3784_hygiene_ro_dispatch as previous
import pg3994_literal_invariant_ro_sources as role
from pg3996_literal_invariant_ro_compile import TARGET, generated

GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS
REMOTE = '/home/ubuntu/pg3998-fixed-stage-v1'
STAGE = role.bind(previous.template.STAGE)


def main():
    raw = inspect.getsource(previous.main)
    for old, new in [('pg3784', 'pg3998'), ('pg3782', 'pg3996'), ('Pg3780', 'Pg3994'), ('PG3420', 'PG3748')]: raw = raw.replace(old, new)
    namespace = {**previous.__dict__, 'role': role, 'TARGET': TARGET, 'generated': generated, 'GUEST': GUEST, 'REMOTE': REMOTE, 'STAGE': STAGE}
    exec(compile(raw, '<one new owned RO action>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
