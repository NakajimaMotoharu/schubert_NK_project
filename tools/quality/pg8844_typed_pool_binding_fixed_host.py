"""Typed borrowed bean60/4: new22/necessary38, helper fixture outer tests not selected."""
import re
import scoped_prometheus_host as run
SOURCE='1e4f4049881c158760d285ce798dd3c4b6d0abbd'
COMPILE=run.host.W/'pg8842-typed-pool-binding-fixed-six-compile-v1'
COMPILE_SHA='067a5c46b02c9b99119cfc8837e83fa652ab7c8d3fa30e98eb67da3c4ac35e4d'
COUNTS={'ApiDbPoolMetricBindingTest':10,'WebDbPoolMetricBindingTest':10,'ApiMetricHttpHandlerTest':20,'WebMetricHttpHandlerTest':20}
if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8844-typed-pool-binding-fixed-host-v1'
    run.OUT=run.host.BASE/'PG8844-typed-pool-binding-fixed-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/TypedPoolBindingJunitLauncher.java'
    paths={role+kind:run.host.ROOT/f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{role.title()}{kind}Test.java' for role in ('api','web') for kind in ('DbPoolMetricBinding','MetricHttpHandler')}
    run.NEW_TEST=paths['apiDbPoolMetricBinding']
    run.TEST_SOURCE_OVERRIDES={path.stem:path for path in paths.values() if path!=run.NEW_TEST}
    run.EXTRA_TEST_SOURCES=tuple(run.host.ROOT/f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{name}DbPoolMetricObservationTest.java' for role,name in (('api',''),('web','Web')))
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8844-TYPED-POOL-BINDING'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1
    actual=re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])
    assert len(actual)==4 and set(actual)=={'dev.codex.schubert.nk.'+role+'.monitoring.'+role.title()+kind+'Test' for role in ('api','web') for kind in ('DbPoolMetricBinding','MetricHttpHandler')}
    for key,path in paths.items():
        role='api' if key.startswith('api') else 'web'
        kind=key[len(role):];prefix=role+('poolb' if kind=='DbPoolMetricBinding' else 'mhttp')
        count=COUNTS[path.stem];body=path.read_text()
        cases=re.findall(r'void\s+('+prefix+r'\d{3})',body)
        assert len(cases)==count and set(cases)=={prefix+str(i).zfill(3) for i in range(1,count+1)}
        assert body.count('@Test')==count and 'org.junit.jupiter.api.Test' in body
        if kind=='DbPoolMetricBinding':
            assert 'class Registry extends SimpleMeterRegistry implements AutoCloseable' in body and 'super.close();' in body
            assert body.count('new Registry()')==9 and 'new SimpleMeterRegistry()' not in body
    assert sum(COUNTS.values())==60 and all(path.is_file() for path in run.EXTRA_TEST_SOURCES)
    assert not any(path.stem in COUNTS for path in run.EXTRA_TEST_SOURCES)
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
