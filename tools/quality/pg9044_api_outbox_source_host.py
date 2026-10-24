"""New20/necessary16 API immutable source PT36; both JDBC/pool fixture outers compile-only."""
import re
import scoped_prometheus_host as run
SOURCE='2ed81b14bb41512e1cda720a446ed7b261121605'
COMPILE=run.host.W/'pg9042-api-outbox-source-six-compile-v1'
COMPILE_SHA='8680b2ac1059c8acb365d32f48f984124b13d6aeefa0632a6f9a546360290397'
COUNTS={'ApiServiceMetricBindingTest':16,'ApiOutboxObservationSourceTest':20}
if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9044-api-outbox-source-host-v1'
    run.OUT=run.host.BASE/'PG9044-api-outbox-source-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiOutboxSourceJunitLauncher.java'
    paths={name:run.host.ROOT/f'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/{name}.java' for name in COUNTS}
    run.NEW_TEST=paths['ApiOutboxObservationSourceTest']
    run.TEST_SOURCE_OVERRIDES={'ApiServiceMetricBindingTest':paths['ApiServiceMetricBindingTest']}
    run.EXTRA_TEST_SOURCES=(run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/DbPoolMetricObservationTest.java',run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OutboxObservationRepositoryTest.java')
    run.COUNTS=COUNTS
    run.SESSION_ID='PG9044-API-OUTBOX-SOURCE'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and set(re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0]))=={'dev.codex.schubert.nk.api.monitoring.'+name for name in COUNTS}
    for name,path in paths.items():
        prefix='apiservice' if name=='ApiServiceMetricBindingTest' else 'outboxSource'
        cases=re.findall(r'void\s+('+prefix+r'\d{3})',path.read_text())
        assert len(cases)==COUNTS[name] and set(cases)=={prefix+str(i).zfill(3) for i in range(1,COUNTS[name]+1)}
        assert path.read_text().count('@Test')==COUNTS[name]
    assert sum(COUNTS.values())==36 and run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
