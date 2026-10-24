"""Typed borrowed bean60/4: new22/necessary38, helper fixture outer tests not selected."""
import re
import scoped_prometheus_host as run
SOURCE='70df4511236eccdbb01801bc16333be95dddae4f'
COMPILE=run.host.W/'pg8832-typed-pool-binding-six-compile-v1'
COMPILE_SHA='PENDING_NORMAL_HASH'
COUNTS={'ApiDbPoolMetricBindingTest':10,'WebDbPoolMetricBindingTest':10,'ApiMetricHttpHandlerTest':20,'WebMetricHttpHandlerTest':20}
if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8834-typed-pool-binding-host-v1'
    run.OUT=run.host.BASE/'PG8834-typed-pool-binding-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/TypedPoolBindingJunitLauncher.java'
    paths={role+kind:run.host.ROOT/f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{role.title()}{kind}Test.java' for role in ('api','web') for kind in ('DbPoolMetricBinding','MetricHttpHandler')}
    run.NEW_TEST=paths['apiDbPoolMetricBinding']
    run.TEST_SOURCE_OVERRIDES={path.stem:path for path in paths.values() if path!=run.NEW_TEST}
    run.EXTRA_TEST_SOURCES=tuple(run.host.ROOT/f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{name}DbPoolMetricObservationTest.java' for role,name in (('api',''),('web','Web')))
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8834-TYPED-POOL-BINDING'
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
    assert sum(COUNTS.values())==60 and all(path.is_file() for path in run.EXTRA_TEST_SOURCES)
    assert not any(path.stem in COUNTS for path in run.EXTRA_TEST_SOURCES)
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
