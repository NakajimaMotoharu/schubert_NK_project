"""Fresh read-only actual job/peer/run binding of the once-issued current4856 Root."""
import inspect
from pyflakes.api import check
import pg2017_fresh_resume_live_binding as transport
import pg2686_operation_current_live_binding as old
import pg3434_current_outbox_candidate_sources as roles
from pg3462_outbox_current_observer import SOURCE, BOM
from pg3464_outbox_current_noargs_once import SLOT as ONCE
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

SLOT = 'pg3466-outbox-current-live-binding-v1'


def body():
    raw = old.body().replace('PG2654', 'PG3420')
    raw = raw.replace('b2d6f605-61cf-425f-8fbd-12d606f6ee66', roles.BOOT)
    raw = raw.replace('b2d6f60561cf425f8fbd12d606f6ee66', roles.BOOT.replace('-', ''))
    _, _, previous, _ = roles._binding_context()
    raw += "\nrequire(fields[1]!=" + repr(previous['run']) + "and fields[3]!=" + repr(previous['activation']) + ")\n"
    if check('SOURCE="test"\nDIGEST="test"\nEXPECTED={}\n' + raw, '<whole actual new Root binding>'):
        raise ValueError('whole live-binding exports required')
    compile(raw, '<current4856 actual distinct Root identity>', 'exec')
    return raw


def entry():
    raw = inspect.getsource(transport.main).replace('pg2015-completed-run-fresh-resume-once-v1', ONCE)
    ns = {**transport.__dict__, 'SOURCE': SOURCE, 'BOM': BOM, 'SLOT': SLOT, 'body': body}
    exec(compile(raw, '<current4856 same issued job read-only binding>', 'exec'), ns)
    return ns['main']


if __name__ == '__main__':
    with management_gate(P / 'current-management-critical.lock'):
        raise SystemExit(entry()())
