"""Typed actual eighteen parent fields from same current genuine post-Root seal."""
import inspect
import pg2706_operation_current_parent_projection as prior
from pg2862_network_newcurrent_observer import SOURCE,BOM
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

SLOT='pg2888-network-parent-projection-v1'
SEAL='pg2886-network-newcurrent-full-seal-v1'


def payload(sha,bom=None):
    if bom is not None and bom!=BOM:raise ValueError('only actual a9 manifest required')
    raw=prior.payload(sha,BOM).replace('pg2704-operation-current-full-seal-v1',SEAL).replace(prior.SOURCE,SOURCE)
    from pyflakes.api import check
    if check(raw,'<actual current a9 parent18>'):raise ValueError('complete actual parent18 namespace required')
    compile(raw,'<same seal typed parent18>','exec');return raw


def main():
    raw=inspect.getsource(prior.previous.main).replace('pg2548-strict-current-full-seal-v1',SEAL)
    ns={**prior.previous.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<actual a9 parent18 capture>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
