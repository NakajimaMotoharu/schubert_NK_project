"""API resource-free factory new6/necessary30, ordinary own JVM only, no Main startup."""
import re
import scoped_prometheus_host as run
SOURCE='0f065c63fe1667e014fa4b985579d4146c3d91c5'
COMPILE=run.host.W/'pg8854-api-caller-metric-six-compile-v1'
COMPILE_SHA='7aa656748674bd692a4d6132bff0c60e3470f70435f556b750eb67fc64aa0ba1'
COUNTS={'ApiDbPoolMetricBindingTest':15,'ApiMetricHttpHandlerTest':21}
if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8856-api-caller-metric-host-v1'
    run.OUT=run.host.BASE/'PG8856-api-caller-metric-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiCallerMetricJunitLauncher.java'
    paths={name:run.host.ROOT/f'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/{name}.java' for name in COUNTS}
    run.NEW_TEST=paths['ApiDbPoolMetricBindingTest']
    run.TEST_SOURCE_OVERRIDES={'ApiMetricHttpHandlerTest':paths['ApiMetricHttpHandlerTest']}
    run.EXTRA_TEST_SOURCES=(run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/DbPoolMetricObservationTest.java',)
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8856-API-CALLER-METRIC'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1
    assert set(re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0]))=={'dev.codex.schubert.nk.api.monitoring.'+name for name in COUNTS}
    for name,path in paths.items():
        prefix='apipoolb' if name=='ApiDbPoolMetricBindingTest' else 'apimhttp'
        cases=re.findall(r'void\s+('+prefix+r'\d{3})',path.read_text())
        assert len(cases)==COUNTS[name] and set(cases)=={prefix+str(i).zfill(3) for i in range(1,COUNTS[name]+1)}
        assert path.read_text().count('@Test')==COUNTS[name]
    assert sum(COUNTS.values())==36 and run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
