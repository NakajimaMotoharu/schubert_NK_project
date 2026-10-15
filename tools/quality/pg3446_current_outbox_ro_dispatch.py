"""New-only RO stage/prepare; never publish, start, stop or repeat unused placement."""
import sys

import pg2668_operation_ro_dispatch as old
import pg3442_current_outbox_ro_sources as role
from pg3444_current_outbox_ro_compile import TARGET

GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS
REMOTE = '/home/ubuntu/pg3446-fixed-stage-v1'
STAGE = role.bind(old.STAGE).replace('pg2668-fixed-stage-v1', 'pg3446-fixed-stage-v1')


def source():
    raw = role.bind(old.source())
    for before, after in [('pg2667-frozen', 'pg3444-frozen'), ('pg2668-', 'pg3446-'),
                          ('2f7ca23be804567a5d9a61636cf4c1d4ec96fcd0', role.role.SOURCE)]:
        if before not in raw:
            raise ValueError('explicit whole RO boundary required: ' + before)
        raw = raw.replace(before, after)
    compile(raw, '<same candidate full RO dispatcher>', 'exec')
    return raw


def main():
    if sys.argv[1:] not in (['stage'], ['prepare-ro']):
        raise ValueError('explicit distinct stage or prepare-ro only')
    role.qualify()
    engine = old.previous.previous.prior.prior.prior
    namespace = {**engine.__dict__, '__file__': __file__, 'TARGET': TARGET,
                 'TOOLS': role.TOOLS, 'CLASS': role.CLASS, 'GUEST': GUEST, 'REMOTE': REMOTE,
                 'STAGE': STAGE, 'sources': role.sources, 'CANDIDATE': role.role.SOURCE,
                 'OLD': role.role.CURRENT, 'BEFORE': role.role.BEFORE}
    exec(compile(source(), '<currenta9 unused4856 RO entry>', 'exec'), namespace)
    # The complete composed entry owns the single non-reentrant management gate.
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
