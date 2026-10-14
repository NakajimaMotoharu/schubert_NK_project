"""One canonical fresh cold INVALID + atomic approval + preserved linked current."""
import json
import pg2848_network_cold_ro_prepare as prior
import pg2852_network_cold_publication_sources as s
import pg1450_current_cold_retry as dispatcher
from pg2854_network_cold_publication_compile import FROZEN
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

SLOT='pg2858-network-cold-publication-owned-activate-v1'


def source():
    raw=prior.source()
    for a,b in [(s.ro.CLASS,s.CLASS),(s.ro.TOOLS,s.TOOLS),(s.ro.SAVE,s.SAVE),
        ('pg2846-network-cold-ro-stage-v1','pg2856-network-cold-publication-stage-v1'),(prior.SLOT,SLOT),
        ('PG2848-network-cold-ro-owned-prepare-v1','PG2858-network-cold-publication-owned-activate-v1'),
        ("'prepare-ro'])","'activate'])")]:
        if a not in raw:raise ValueError('explicit owned finite publication family required')
        raw=raw.replace(a,b)
    compile(raw,'<one newboot finite publication dispatcher>','exec');return raw


def main():
    s.qualify();v=json.loads((W/FROZEN).read_bytes())
    if v.get('actualExit')!=0 or v.get('candidateSource')!=s.ro.unused.CANDIDATE:raise ValueError('full candidate ABI required')
    ns={**dispatcher.__dict__,'qualify_before':s.qualify,'FROZEN':W/FROZEN}
    exec(compile(source(),'<once finite cold publication>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['prepare']()


if __name__=='__main__':raise SystemExit(main())
