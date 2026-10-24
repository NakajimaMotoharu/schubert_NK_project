"""New17/necessary21 ordinary API metadata/HTTP38 only; fixture outer compile-only."""
import re
import scoped_prometheus_host as run
SOURCE='73d94fc525c6ea8828ca82d906ec583146fee7bf'
COMPILE=run.host.W/'pg9028-api-service-six-compile-v1'
COMPILE_SHA='370a39dc80cf8c1cd90997526b6377f1f68aa8b82c7c69b4a04b71c3e66d9f98'
COUNTS={'ApiServiceMetricBindingTest':16,'ApiMetricHttpHandlerTest':22}
if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9030-api-service-host-v1'
    run.OUT=run.host.BASE/'PG9030-api-service-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiServiceMetricJunitLauncher.java'
    paths={name:run.host.ROOT/f'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/{name}.java' for name in COUNTS}
    run.NEW_TEST=paths['ApiServiceMetricBindingTest']
    run.TEST_SOURCE_OVERRIDES={'ApiMetricHttpHandlerTest':paths['ApiMetricHttpHandlerTest']}
    run.EXTRA_TEST_SOURCES=(run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/DbPoolMetricObservationTest.java',)
    run.COUNTS=COUNTS
    run.SESSION_ID='PG9030-API-SERVICE'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and set(re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0]))=={'dev.codex.schubert.nk.api.monitoring.'+name for name in COUNTS}
    for name,path in paths.items():
        prefix='apiservice' if name=='ApiServiceMetricBindingTest' else 'apimhttp'
        cases=re.findall(r'void\s+('+prefix+r'\d{3})',path.read_text())
        assert len(cases)==COUNTS[name] and set(cases)=={prefix+str(i).zfill(3) for i in range(1,COUNTS[name]+1)}
        assert path.read_text().count('@Test')==COUNTS[name]
    assert sum(COUNTS.values())==38 and run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
