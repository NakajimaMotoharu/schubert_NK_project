"""Actual sealed current4856 parent18 projection, no fabricated completion."""
import inspect
import pg2706_operation_current_parent_projection as old
import pg3472_outbox_acceptance as current
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

SLOT = 'pg3478-outbox-parent-projection-v1'


def payload(sha, bom=None):
    if bom is not None and bom != current.BOM:
        raise ValueError('one actual current4856 BOM required')
    return current.bind(old.payload(sha, current.BOM))


def main():
    raw = inspect.getsource(old.main).replace('pg2704-operation-current-full-seal-v1', current.SEAL)
    # old.main already owns the single host management gate.
    ns = {**old.__dict__, 'SOURCE': current.SOURCE, 'SLOT': SLOT, 'payload': payload,
          'P': P, 'management_gate': management_gate}
    exec(compile(raw, '<actual current4856 parent18 projection>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
