"""Immutable new-only RO tool transport, no candidate placement replay."""
import pg2820_network_current_cold_stage as prior
import pg1446_current_cold_stage as transport
import pg2842_network_cold_ro_sources as s
from pg2844_network_cold_ro_compile import FROZEN
from pg1674_critical_management_gate import management_gate

SLOT='pg2846-network-cold-ro-stage-v1'


def source():
    raw=prior.source()
    for a,b in [('pg2818-network-current-cold-frozen-v1.safe.json',FROZEN),('pg2820','pg2846'),('PG2820','PG2846'),(s.unused.current.TOOLS,s.TOOLS)]:
        if a not in raw:raise ValueError('explicit RO immutable family required')
        raw=raw.replace(a,b)
    compile(raw,'<newboot RO tool stage>','exec');return raw


def main():
    s.qualify();ns={**transport.__dict__,'OUT':transport.W/SLOT,'TOOLS':transport.W/s.TOOLS}
    exec(compile(source(),'<actual RO tools transport>','exec'),ns)
    with management_gate(transport.P/'current-management-critical.lock'):ns['main']()
    return 0


if __name__=='__main__':raise SystemExit(main())
