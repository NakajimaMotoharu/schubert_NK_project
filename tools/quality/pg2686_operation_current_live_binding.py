"""Read-only new Root identity; reject every prior generation including current a79."""
import inspect
import pg2542_strict_current_live_binding as previous
from pg2674_operation_publication_sources import candidate_bom,production
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

SLOT='pg2686-operation-current-live-binding-v1'


def body():
    raw=previous.body().replace('PG2512','PG2654')
    return raw+"\nrequire(fields[1]!='b29fb3e5-2c46-4eac-b8f3-d03b986338e3'and fields[3]!='d0219581-24e4-4136-ac90-39d54e704378')\n"


def entry():
    raw=inspect.getsource(previous.previous.prior.prior.transport.main).replace('pg2015-completed-run-fresh-resume-once-v1','pg2684-operation-current-noargs-once-v1')
    ns={**previous.previous.prior.prior.transport.__dict__,'SOURCE':production(),'BOM':candidate_bom(),'SLOT':SLOT,'body':body}
    exec(compile(raw,'<new candidate readonly live job authentication>','exec'),ns);return ns['main']


if __name__=='__main__':
    with management_gate(P/'current-management-critical.lock'):raise SystemExit(entry()())
