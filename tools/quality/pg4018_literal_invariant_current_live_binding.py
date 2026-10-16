"""Read-only actual Root and peer generations; never extend original budget."""
import inspect
from pyflakes.api import check
import pg3466_outbox_current_live_binding as previous
from pg4012_literal_invariant_current_observer import SOURCE, BOM
from pg4016_literal_invariant_current_noargs_once import SLOT as ONCE
from pg4002_literal_invariant_publication_sources import ro
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

SLOT = 'pg4018-literal-invariant-current-live-binding-v1'


def body():
    raw = previous.body().replace('PG3420', 'PG3976')
    current, _, _ = ro.unused.current_tuple()
    raw += '\nrequire(fields[1]!=' + repr(current['run']) + 'and fields[3]!=' + repr(current['activation']) + ')\n'
    if check('SOURCE="test"\nDIGEST="test"\nEXPECTED={}\n' + raw, '<actual new Root live binding>'): raise ValueError('complete live namespace required')
    compile(raw, '<new actual Root distinct from old completed tuple>', 'exec')
    return raw


def main():
    raw = inspect.getsource(previous.transport.main).replace('pg2015-completed-run-fresh-resume-once-v1', ONCE)
    values = {**previous.transport.__dict__, 'SOURCE': SOURCE, 'BOM': BOM, 'SLOT': SLOT, 'body': body}
    exec(compile(raw, '<new once-issued job observer>', 'exec'), values)
    with management_gate(P / 'current-management-critical.lock'): return values['main']()


if __name__ == '__main__': raise SystemExit(main())
