"""Explicit new-only stage/owned stop from actual whole seal, never Root replay."""
import inspect
import sys
import pg2712_operation_owned_dispatch as old
import pg3490_outbox_owned_sources as role
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS
REMOTE = '/home/ubuntu/pg3494-outbox-owned-stage-v1'
ARCHIVE = 'pg3494-' + role.TOOLS + '.tar'


def namespace():
    base = old.previous
    ns = {**base.__dict__, 'GUEST': GUEST, 'REMOTE': REMOTE, 'ARCHIVE': ARCHIVE,
          'POST_SLOT': role.current.SEAL, 'sources': role.sources, 'context': role.context,
          'SOURCE': role.SOURCE, 'TOOLS': role.TOOLS, 'candidate_bom': role.candidate_bom,
          'payload': lambda binding: role.current.seal_payload(binding)}
    for fn in [base.stage, base.post_payload, base.run_source, base.run_action, base.main]:
        exec(compile(role.bind(inspect.getsource(fn)), '<new exact owned dispatch>', 'exec'), ns)
    stage_fn, run = ns['stage'], ns['run_source']
    ns['stage'] = lambda: role.bind(stage_fn())
    ns['run_source'] = lambda: role.bind(run())
    return ns


def stage():
    return namespace()['stage']()


def run_source():
    return namespace()['run_source']()


def main():
    if sys.argv[1:] not in (['stage'], ['stop']):
        raise ValueError('separate exact new-only stage or owned stop required')
    with management_gate(P / 'current-management-critical.lock'):
        return namespace()['main']()


if __name__ == '__main__':
    raise SystemExit(main())
