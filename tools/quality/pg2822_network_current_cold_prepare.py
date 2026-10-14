"""One owned SSC264 finite cold prepare with fresh locks/DB/Ref ownership; no business start."""
import inspect
import pg2212_current_newboot_cold_dispatch as prior
from pg2816_network_current_cold_sources import CLASS,TOOLS,BOOT,qualify_before
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate


def source():
    raw=prior.source()
    for a,b in [('Pg2208CurrentColdPreparation',CLASS),('pg2208-current-newboot-cold-tools-v1',TOOLS),
      ('pg2214-current-newboot-cold-stage-v2','pg2820-network-current-cold-stage-v1'),
      ('pg2212-current-newboot-cold-owned-prepare-v1','pg2822-network-current-cold-owned-prepare-v1'),
      ('PG2212-current-newboot-cold-owned-prepare-v1','PG2822-network-current-cold-owned-prepare-v1'),
      ('pg2212-current-newboot-cold-prepared-v1','pg2822-network-current-cold-prepared-v1'),
      ('b2d6f605-61cf-425f-8fbd-12d606f6ee66',BOOT),('0.1.0-PG2126','0.1.0-PG2654')]:
        if a not in raw:raise ValueError('new cold dispatch all exact roles required')
        raw=raw.replace(a,b)
    compile(raw,'<one current cold finite preparation>','exec');return raw


def main():
    ns={**prior.prior.__dict__,'qualify_before':qualify_before,'FROZEN':W/'pg2818-network-current-cold-frozen-v1.safe.json'}
    exec(compile(source(),'<actual new cold prepare dispatcher>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['prepare']()


if __name__=='__main__':raise SystemExit(main())
