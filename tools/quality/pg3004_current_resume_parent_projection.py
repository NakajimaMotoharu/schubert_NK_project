"""Actual sealed current fresh-resume parent eighteen fields, no synthetic completion."""
import inspect
import pg2888_network_parent_projection as previous
from pg2982_current_resume_observer import SOURCE
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

SLOT = 'pg3004-current-resume-parent-projection-v1'
SEAL = 'pg3000-current-resume-full-seal-v1'


def payload(sha):
    return previous.payload(sha).replace(previous.SEAL, SEAL)


def main():
    raw = inspect.getsource(previous.prior.previous.main).replace('pg2548-strict-current-full-seal-v1', SEAL)
    ns = {**previous.prior.previous.__dict__, 'SOURCE': SOURCE, 'SLOT': SLOT, 'payload': payload}
    exec(compile(raw, '<actual same current parent18>', 'exec'), ns)
    with management_gate(P / 'current-management-critical.lock'):
        return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
