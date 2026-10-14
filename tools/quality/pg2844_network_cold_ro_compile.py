"""Host-only fixed candidate RO current-JAR ABI/literal oracle compiler."""
import inspect
import pg1442_current_cold_compile as prior
import pg2842_network_cold_ro_sources as s

FROZEN='pg2844-network-cold-ro-frozen-v1.safe.json'


def main():
    s.qualify();raw=inspect.getsource(prior.main)
    for a,b in [('Pg1441CurrentColdPreparation',s.CLASS),('pg1441_current_cold_refs.py',s.REF),
        ('pg1441_current_cold_sources_test.py','pg2842_network_cold_ro_sources_test.py'),
        ('PG1442-current-cold-compile-v1','PG2844-network-cold-ro-compile-v1'),
        ('pg1442-current-cold-frozen-v1.safe.json',FROZEN),('pg1292-release-v1','pg2654-release-v1')]:raw=raw.replace(a,b)
    # Qualified helper provenance remains original1396; result identifies actual current ABI.
    raw=s.unused.one(raw,"'productionSource':'769ddb15cd735c25fef581b5f9850ef9d0053c0f'","'productionSource':CURRENT_SOURCE,'candidateSource':CANDIDATE_SOURCE")
    marker="    release=W/'pg2654-release-v1'"
    raw=s.unused.one(raw,marker,'    write(OUT/(CLASS+\'Test.java\'),java_test().encode())\n'+marker)
    raw=s.unused.one(raw,"str(OUT/'"+s.CLASS+".java')]]", "str(OUT/'"+s.CLASS+".java'),str(OUT/(CLASS+'Test.java'))],\n        [str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,CLASS+'Test']]")
    ns={**prior.__dict__,'OUT':prior.W/s.TOOLS,'java':s.java,'observer':s.observer,'java_test':s.java_test,
        'CLASS':s.CLASS,'CURRENT_SOURCE':s.unused.current.SOURCE,'CANDIDATE_SOURCE':s.unused.CANDIDATE}
    exec(compile(raw,'<actual fixed cold RO compiler>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
