"""New-only immutable publication tools; no activation/permission."""
import pg2846_network_cold_ro_stage as prior
import pg1446_current_cold_stage as transport
import pg2852_network_cold_publication_sources as s
from pg2854_network_cold_publication_compile import FROZEN
from pg1674_critical_management_gate import management_gate

SLOT='pg2856-network-cold-publication-stage-v1'


def source():
    raw=prior.source()
    for a,b in [('pg2844-network-cold-ro-frozen-v1.safe.json',FROZEN),('pg2846','pg2856'),('PG2846','PG2856'),(s.ro.TOOLS,s.TOOLS)]:
        if a not in raw:raise ValueError('exact publication immutable role required')
        raw=raw.replace(a,b)
    compile(raw,'<newboot publication immutable tools>','exec');return raw


def main():
    s.qualify();ns={**transport.__dict__,'OUT':transport.W/SLOT,'TOOLS':transport.W/s.TOOLS}
    exec(compile(source(),'<actual immutable publication transport>','exec'),ns)
    with management_gate(transport.P/'current-management-critical.lock'):ns['main']()
    return 0


if __name__=='__main__':raise SystemExit(main())
