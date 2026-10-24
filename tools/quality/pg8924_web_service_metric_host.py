"""New service binding14/HTTP0221 + necessary HTTP21 =36; own unstarted HTTP metadata only."""
import re
import scoped_prometheus_host as run
SOURCE='96575ba67dc4fabb335df8481e2cb2fbe7ef233b'
COMPILE=run.host.W/'pg8922-web-service-metric-six-compile-v1'
COMPILE_SHA='aff1257f5996149f90ec3951d756a8ed28874b5fa9aab08433ca75cdb95100ff'
COUNTS={'WebServiceMetricBindingTest':14,'WebMetricHttpHandlerTest':22}
if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8924-web-service-metric-host-v1'
    run.OUT=run.host.BASE/'PG8924-web-service-metric-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/WebServiceMetricJunitLauncher.java'
    paths={name:run.host.ROOT/f'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/{name}.java' for name in COUNTS}
    run.NEW_TEST=paths['WebServiceMetricBindingTest']
    run.TEST_SOURCE_OVERRIDES={'WebMetricHttpHandlerTest':paths['WebMetricHttpHandlerTest']}
    run.EXTRA_TEST_SOURCES=(run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebDbPoolMetricObservationTest.java',)
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8924-WEB-SERVICE-METRIC'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and set(re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0]))=={'dev.codex.schubert.nk.web.monitoring.'+name for name in COUNTS}
    for name,path in paths.items():
        prefix='webservice' if name=='WebServiceMetricBindingTest' else 'webmhttp'
        cases=re.findall(r'void\s+('+prefix+r'\d{3})',path.read_text())
        assert len(cases)==COUNTS[name] and set(cases)=={prefix+str(i).zfill(3) for i in range(1,COUNTS[name]+1)}
        assert path.read_text().count('@Test')==COUNTS[name]
    assert sum(COUNTS.values())==36 and run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
