"""Actual new source parent eighteen fields; no synthetic authority."""
import inspect
import pg2552_strict_current_parent_projection as previous
from pg2674_operation_publication_sources import production,candidate_bom
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

SOURCE=production();SLOT='pg2706-operation-current-parent-projection-v1'


def payload(sha,bom=None):
    if bom is None:bom=candidate_bom()
    raw=previous.payload(sha,bom).replace('pg2548-strict-current-full-seal-v1','pg2704-operation-current-full-seal-v1').replace(previous.SOURCE,SOURCE)
    compile(raw,'<new source typed eighteen parent fields>','exec');return raw


def main():
    raw=inspect.getsource(previous.main).replace('pg2548-strict-current-full-seal-v1','pg2704-operation-current-full-seal-v1')
    ns={**previous.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<new actual parent18 capture>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
