"""New-only single metadata controller stage/proof under the retained original host gate."""
import inspect
import pg4176_partial_coordinator as predecessor
from pg4346_current_partial_coordinator import owner
import pg4380_half_handoff_sources as sources

SLOT = 'pg4382-half-handoff-tools-v1'
GUEST = '/var/lib/pgpt-s1-preservation/' + SLOT


def files():
    return {'keeper.py': sources.payload()}


def stage_payload():
    ns = {**vars(predecessor), 'files': files, 'GUEST': GUEST}
    exec(compile(inspect.getsource(predecessor.stage_payload), '<single metadata stage factory>', 'exec'), ns)
    return ns['stage_payload']()


def main():
    ns = {**vars(predecessor), 'SLOT': SLOT, 'GUEST': GUEST, 'files': files,
          'stage_payload': stage_payload, 'owner': owner}
    exec(compile(inspect.getsource(predecessor.main), '<current single metadata stage/proof>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
