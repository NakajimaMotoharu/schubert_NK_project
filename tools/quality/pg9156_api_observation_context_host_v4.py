"""New OBSOWN26 own JVM/fake observation only; supporting fixture outers are compile-only."""
import re
import scoped_prometheus_host as run
SOURCE='c06a72ef46bb65c091de329468f70dd5d347ce4e'
COMPILE=run.host.W/'pg9154-api-observation-context-six-compile-v2'
COMPILE_SHA='4f5c3cdc95cf46316121d7d95e3ab4fbb5779805337a71aacbbf01133f45fa6d'
COUNTS={'ApiObservationContextTest':26}

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9156-api-observation-context-host-v3'
    run.OUT=run.host.BASE/'PG9156-api-observation-context-host-v3'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiObservationContextJunitLauncherV2.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiObservationContextTest.java'
    run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=tuple(run.host.ROOT/f'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/{name}.java' for name in ('DbPoolMetricObservationTest','OutboxObservationRepositoryTest','ApiReadOnlyObservationAttemptTest','ApiOutboxObservationPumpTest','OwnedApiObservationWorkerTest'))
    run.COUNTS=COUNTS
    run.SESSION_ID='PG9156-API-OBSERVATION-CONTEXT-V3'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])==['dev.codex.schubert.nk.api.monitoring.ApiObservationContextTest']
    cases=re.findall(r'void\s+(obsCtx\d{3})',run.NEW_TEST.read_text())
    assert len(cases)==26 and set(cases)=={'obsCtx'+str(i).zfill(3) for i in range(1,27)} and run.NEW_TEST.read_text().count('@Test')==26
    compact=''.join(run.HELPER.read_text().split())
    checks=('value.getTestsFoundCount()','value.getTestsStartedCount()','value.getTestsSucceededCount()','results.size()')
    counts=[compact.count(name+'==26') for name in checks]
    assert counts==[1]*4 and sum(COUNTS.values())==26
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
