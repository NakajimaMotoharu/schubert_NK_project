"""One finite SSC249 candidate host RO under fresh M-A/DB/Ref ownership."""
import json
import pg2838_network_cold_unused_place as prior
import pg2842_network_cold_ro_sources as s
from pg2844_network_cold_ro_compile import FROZEN
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

SLOT='pg2848-network-cold-ro-owned-prepare-v1'


def source():
    raw=prior.source()
    for a,b in [(s.unused.CLASS,s.CLASS),(s.unused.TOOLS,s.TOOLS),(s.unused.SAVE,s.SAVE),
        ('pg2836-network-cold-unused-stage-v1','pg2846-network-cold-ro-stage-v1'),(prior.SLOT,SLOT),
        ('PG2838-network-cold-unused-owned-place-v1','PG2848-network-cold-ro-owned-prepare-v1'),("'place'])","'prepare-ro'])")]:
        if a not in raw:raise ValueError('explicit RO owned preparation family required')
        raw=raw.replace(a,b)
    compile(raw,'<one cold RO prepare dispatcher>','exec');return raw


def main():
    s.qualify();v=json.loads((W/FROZEN).read_bytes())
    if v.get('actualExit')!=0 or v.get('candidateSource')!=s.unused.CANDIDATE:raise ValueError('actual current candidate ABI required')
    ns={**prior.prior.prior.prior.__dict__,'qualify_before':s.qualify,'FROZEN':W/FROZEN}
    exec(compile(source(),'<actual one candidate RO dispatcher>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['prepare']()


if __name__=='__main__':raise SystemExit(main())
