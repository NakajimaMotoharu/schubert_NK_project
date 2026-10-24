"""Exact new role-context52/2 ordinary own JVM, no native/service startup."""
import re
import scoped_prometheus_host as run

SOURCE='f1b570e45f072b6001ad7e8e250ffbc5686c494a'
COMPILE=run.host.W/'pg8740-metric-context-six-compile-v1'
COMPILE_SHA='45fda0573fcd8709921be8374a6c77bbb598c7a51dab7b6faa9eb01c3fda3aff'
COUNTS={'ApiMetricContextTest':26,'WebMetricContextTest':26}

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8742-metric-context-host-v1'
    run.OUT=run.host.BASE/'PG8742-metric-context-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/MetricContextJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiMetricContextTest.java'
    web=run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebMetricContextTest.java'
    run.TEST_SOURCE_OVERRIDES={'WebMetricContextTest':web}
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8742-METRIC-CONTEXT'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1
    actual=re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])
    assert len(actual)==2 and set(actual)=={'dev.codex.schubert.nk.'+role+'.monitoring.'+title+'MetricContextTest' for role,title in (('api','Api'),('web','Web'))}
    for role,path in (('api',run.NEW_TEST),('web',web)):
        body=path.read_text()
        cases=re.findall(r'void\s+('+role+r'mctx\d{3})',body)
        assert len(cases)==26 and set(cases)=={role+'mctx'+str(i).zfill(3) for i in range(1,27)}
        assert body.count('@Test')==26 and 'org.junit.jupiter.api.Test' in body
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
