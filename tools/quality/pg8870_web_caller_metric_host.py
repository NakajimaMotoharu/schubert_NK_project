"""API resource-free factory new6/necessary30, ordinary own JVM only, no Main startup."""
import re
import scoped_prometheus_host as run
SOURCE='28befbf2cac86840b6adef53b6c5f972e6f9610f'
COMPILE=run.host.W/'pg8868-web-caller-metric-six-compile-v1'
COMPILE_SHA='bf2a02c6a70f65d1bc002edafa02d4566f7aa8a8e5d1d1fc8d829e188492bc68'
COUNTS={'WebDbPoolMetricBindingTest':15,'WebMetricHttpHandlerTest':21}
if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8870-web-caller-metric-host-v1'
    run.OUT=run.host.BASE/'PG8870-web-caller-metric-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/WebCallerMetricJunitLauncher.java'
    paths={name:run.host.ROOT/f'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/{name}.java' for name in COUNTS}
    run.NEW_TEST=paths['WebDbPoolMetricBindingTest']
    run.TEST_SOURCE_OVERRIDES={'WebMetricHttpHandlerTest':paths['WebMetricHttpHandlerTest']}
    run.EXTRA_TEST_SOURCES=(run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebDbPoolMetricObservationTest.java',)
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8870-WEB-CALLER-METRIC'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1
    assert set(re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0]))=={'dev.codex.schubert.nk.web.monitoring.'+name for name in COUNTS}
    for name,path in paths.items():
        prefix='webpoolb' if name=='WebDbPoolMetricBindingTest' else 'webmhttp'
        cases=re.findall(r'void\s+('+prefix+r'\d{3})',path.read_text())
        assert len(cases)==COUNTS[name] and set(cases)=={prefix+str(i).zfill(3) for i in range(1,COUNTS[name]+1)}
        assert path.read_text().count('@Test')==COUNTS[name]
    assert sum(COUNTS.values())==36 and run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
