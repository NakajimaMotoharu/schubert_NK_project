"""SSC293 new-only full-FD/pool-bound stage/proof; original failed tools are immutable."""
import inspect
import pg4176_partial_coordinator as predecessor
from pg4346_current_partial_coordinator import owner
import pg4360_pool_bound_partial_sources as sources

SLOT = 'pg4366-pool-bound-tools-v3'
GUEST = '/var/lib/pgpt-s1-preservation/' + SLOT


def files():
    return sources.files()


def stage_payload():
    ns = {**vars(predecessor), 'files': files, 'GUEST': GUEST}
    exec(compile(inspect.getsource(predecessor.stage_payload), '<pool-bound stage factory>', 'exec'), ns)
    return ns['stage_payload']()


def main():
    ns = {**vars(predecessor), 'SLOT': SLOT, 'GUEST': GUEST, 'files': files,
          'stage_payload': stage_payload, 'owner': owner}
    exec(compile(inspect.getsource(predecessor.main), '<pool-bound stage/proof transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
