"""Finite new-only stage/activate; no Unit exchange/reload or Root business start."""
import sys
import pg2676_operation_publication_dispatch as old
import pg3450_current_outbox_publication_sources as role
from pg3452_current_outbox_publication_compile import TARGET

GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS
REMOTE = '/home/ubuntu/pg3454-current-outbox-publication-stage-v1'


def stage(bom):
    return role.bind(old.stage(bom), bom).replace(old.REMOTE, REMOTE)


def source(bom):
    raw = role.bind(old.source(bom), bom)
    for a, b in [('pg2675-frozen', 'pg3452-frozen'), ('pg2676-', 'pg3454-'),
                 ('2f7ca23be804567a5d9a61636cf4c1d4ec96fcd0', role.production())]:
        if a not in raw:
            raise ValueError('one whole finite boundary: ' + a)
        raw = raw.replace(a, b)
    compile(raw, '<same signed candidate finite publication>', 'exec')
    return raw


def main():
    if sys.argv[1:] not in (['stage'], ['activate']):
        raise ValueError('separate new-only stage or finite activate only')
    bom = role.candidate_bom()
    engine = old.previous.previous.prior.prior
    namespace = {**engine.__dict__, '__file__': __file__, 'TARGET': TARGET,
                 'TOOLS': role.TOOLS, 'CLASS': role.CLASS, 'GUEST': GUEST, 'REMOTE': REMOTE,
                 'STAGE': stage(bom), 'sources': role.sources, 'CANDIDATE': role.production(),
                 'OLD': role.CURRENT, 'BOM': bom, 'BEFORE': role.BEFORE}
    exec(compile(source(bom), '<new finite publication entry>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
