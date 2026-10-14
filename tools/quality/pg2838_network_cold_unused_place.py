"""One owned cold signed unused placement. No original/business/permission changes."""
import json
import pg2822_network_current_cold_prepare as prior
import pg2832_network_cold_unused_sources as s
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate
from pg2834_network_cold_unused_compile import FROZEN

SLOT='pg2838-network-cold-unused-owned-place-v1'


def source():
    raw=prior.source()
    for a,b in [(s.current.CLASS,s.CLASS),(s.current.TOOLS,s.TOOLS),
        ('pg2820-network-current-cold-stage-v1','pg2836-network-cold-unused-stage-v1'),
        ('pg2822-network-current-cold-owned-prepare-v1',SLOT),
        ('PG2822-network-current-cold-owned-prepare-v1','PG2838-network-cold-unused-owned-place-v1'),
        (s.current.PREPARED,s.SAVE),("'prepare'])","'place'])")]:
        if a not in raw:raise ValueError('exact cold owned place family required')
        raw=raw.replace(a,b)
    compile(raw,'<one owned cold unused placement>','exec');return raw


def main():
    s.qualify()
    v=json.loads((W/FROZEN).read_bytes())
    if v.get('actualExit')!=0 or v.get('candidateSource')!=s.CANDIDATE:raise ValueError('signed candidate ABI required')
    ns={**prior.prior.prior.__dict__,'qualify_before':s.qualify,'FROZEN':W/FROZEN}
    exec(compile(source(),'<newboot unused placement dispatcher>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['prepare']()


if __name__=='__main__':raise SystemExit(main())
