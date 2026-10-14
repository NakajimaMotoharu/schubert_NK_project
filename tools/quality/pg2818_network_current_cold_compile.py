"""Compile fixed helper ABI against actual current signed PG2654; no VM action."""
import inspect
import pg1442_current_cold_compile as prior
from pg2816_network_current_cold_sources import CLASS,TOOLS,SOURCE,java,observer,qualify_before


def main():
    qualify_before();raw=inspect.getsource(prior.main)
    for a,b in [('Pg1441CurrentColdPreparation',CLASS),('pg1441_current_cold_refs.py','pg2816_network_current_cold_refs.py'),
      ('pg1441_current_cold_sources_test.py','pg2816_network_current_cold_sources_test.py'),
      ('PG1442-current-cold-compile-v1','PG2818-network-current-cold-compile-v1'),
      ('pg1442-current-cold-frozen-v1.safe.json','pg2818-network-current-cold-frozen-v1.safe.json'),
      ('pg1292-release-v1','pg2654-release-v1')]:
        if a not in raw:raise ValueError('exact current compiler input boundary required')
        raw=raw.replace(a,b)
    old="'productionSource':'769ddb15cd735c25fef581b5f9850ef9d0053c0f'"
    if raw.count(old)!=1:raise ValueError('one production result source required')
    raw=raw.replace(old,"'productionSource':SOURCE")
    ns={**prior.__dict__,'OUT':prior.W/TOOLS,'SOURCE':SOURCE,'java':java,'observer':observer}
    exec(compile(raw,'<current042 cold ABI compile>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
