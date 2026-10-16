"""One reserved finite publication, normal M/A/DB/Ref only; no Root/noargs or Unit reload."""
import inspect
import pg3792_hygiene_publication_dispatch as previous
import pg4002_literal_invariant_publication_sources as role
from pg4004_literal_invariant_publication_compile import TARGET, generated

GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS
REMOTE = '/home/ubuntu/pg4006-literal-invariant-publication-stage-v1'
STAGE = role.bind(previous.template.stage(previous.template.role.ro.role.BOM).replace(previous.template.REMOTE, REMOTE))


def qualify_fixed(fixed):
    namespace = {**previous.__dict__, 'role': role}
    raw = inspect.getsource(previous.qualify_fixed).replace('Pg3788', 'Pg4002').replace('pg3788', 'pg4002').replace('Pg3780', 'Pg3994').replace('pg3780', 'pg3994')
    exec(compile(raw, '<actual new finite target receipt>', 'exec'), namespace)
    return namespace['qualify_fixed'](fixed)


def source():
    raw = previous.source()
    for old, new in [('pg3792', 'pg4006'), ('pg3790', 'pg4004'), ('Pg3788', 'Pg4002'), ('PG3420', 'PG3748')]: raw = raw.replace(old, new)
    compile(raw, '<new finite code-only publication dispatcher>', 'exec')
    return raw


def main():
    namespace = {**previous.previous.__dict__, 'role': role, 'TARGET': TARGET, 'generated': generated, 'GUEST': GUEST, 'REMOTE': REMOTE, 'STAGE': STAGE, 'qualify_fixed': qualify_fixed}
    exec(compile(source(), '<new finite publication explicit action>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
