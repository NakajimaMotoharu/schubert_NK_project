"""Same-source refresh to HTTP: actual104, new16/necessary88, ordinary own JVM only."""
import re
import scoped_prometheus_host as run

SOURCE='c48bc1afbdcf0331be242051c7c9db1dbe36a04e'
COMPILE=run.host.W/'pg8806-metric-refresh-six-compile-v1'
COMPILE_SHA='43cbf64174401dde78c0e48fc7ecd3a43fee6f629755fe19ddc21945583bf334'
COUNTS={'ApiMetricContextTest':33,'WebMetricContextTest':33,'ApiMetricHttpHandlerTest':19,'WebMetricHttpHandlerTest':19}

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8808-metric-refresh-host-v1'
    run.OUT=run.host.BASE/'PG8808-metric-refresh-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/MetricRefreshJunitLauncher.java'
    paths={role+kind:run.host.ROOT/f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{role.title()}{kind}Test.java' for role in ('api','web') for kind in ('MetricContext','MetricHttpHandler')}
    run.NEW_TEST=paths['apiMetricContext']
    run.TEST_SOURCE_OVERRIDES={path.stem:path for path in paths.values() if path!=run.NEW_TEST}
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8808-METRIC-REFRESH'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1
    actual=re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])
    assert len(actual)==4 and set(actual)=={'dev.codex.schubert.nk.'+role+'.monitoring.'+role.title()+kind+'Test' for role in ('api','web') for kind in ('MetricContext','MetricHttpHandler')}
    for key,path in paths.items():
        role='api' if key.startswith('api') else 'web'
        kind=key[len(role):]
        prefix=role+('mctx' if kind=='MetricContext' else 'mhttp')
        count=COUNTS[path.stem]
        body=path.read_text()
        cases=re.findall(r'void\s+('+prefix+r'\d{3})',body)
        assert len(cases)==count and set(cases)=={prefix+str(i).zfill(3) for i in range(1,count+1)}
        assert body.count('@Test')==count and 'org.junit.jupiter.api.Test' in body
        assert 'nk_metric_http_fixture' not in body
        assert 'nk_db_pool_connections' in body and '.tags("service", "'+role.upper()+'", "state", "active")' in body
    assert sum(COUNTS.values())==104 and run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
