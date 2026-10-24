"""Same-source refresh to HTTP: actual104, new16/necessary88, ordinary own JVM only."""
import re
import scoped_prometheus_host as run

SOURCE='32041eafe19116bba7b90431f522371f0bcd8d53'
COMPILE=run.host.W/'pg8820-metric-refresh-fixed-six-compile-v1'
COMPILE_SHA='8107b7e202b684ba02a3fedda816ef40f3a4dcb1fbe7dd7fb785508b6d4c3d54'
COUNTS={'ApiMetricContextTest':33,'WebMetricContextTest':33,'ApiMetricHttpHandlerTest':19,'WebMetricHttpHandlerTest':19}

def fixture_order(fragment,role):
    start=fragment.index('void '+role+'mctx033')
    fragment=fragment[start:]
    assert fragment.index('await(entered);')<fragment.index('context::close')<fragment.index('proceed.countDown();')<fragment.index('future.get(30, TimeUnit.SECONDS)')<fragment.index('assertThrows(IllegalStateException.class, context::bindings);')
    assert 'worker.awaitTermination(30, TimeUnit.SECONDS)' in fragment and 'context.close();' in fragment

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8822-metric-refresh-fixed-host-v1'
    run.OUT=run.host.BASE/'PG8822-metric-refresh-fixed-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/MetricRefreshJunitLauncher.java'
    paths={role+kind:run.host.ROOT/f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{role.title()}{kind}Test.java' for role in ('api','web') for kind in ('MetricContext','MetricHttpHandler')}
    run.NEW_TEST=paths['apiMetricContext']
    run.TEST_SOURCE_OVERRIDES={path.stem:path for path in paths.values() if path!=run.NEW_TEST}
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8822-METRIC-REFRESH'
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
        if kind=='MetricContext':
            fixture_order(body,role)
            statement='assertThrows(IllegalStateException.class, context::bindings);'
            begin=body.index('void '+role+'mctx033')
            fragment=body[begin:]
            changed=fragment.replace(statement,'',1).replace('await(entered);','await(entered);'+statement,1)
            assert changed!=fragment
            try: fixture_order(changed,role)
            except (AssertionError,ValueError): pass
            else: raise AssertionError('getter-before-release fixture mutation must reject')
        assert 'nk_metric_http_fixture' not in body
        assert 'nk_db_pool_connections' in body and '.tags("service", "'+role.upper()+'", "state", "active")' in body
    assert sum(COUNTS.values())==104 and run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
