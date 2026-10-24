"""New OBSOWN26 own JVM/fake observation only; supporting fixture outers are compile-only."""
import re
import scoped_prometheus_host as run
SOURCE='ca4254abd2517d41a84b832bc9c09a980b96c4de'
COMPILE=run.host.W/'pg9154-api-observation-context-six-compile-v1'
COMPILE_SHA='d76c6ca21fa277a564dede6c14f437f47bbe6eb760938132cff30e19cec9a21e'
COUNTS={'ApiObservationContextTest':26}

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9156-api-observation-context-host-v1'
    run.OUT=run.host.BASE/'PG9156-api-observation-context-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiObservationContextJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiObservationContextTest.java'
    run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=tuple(run.host.ROOT/f'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/{name}.java' for name in ('DbPoolMetricObservationTest','OutboxObservationRepositoryTest','ApiReadOnlyObservationAttemptTest','ApiOutboxObservationPumpTest','OwnedApiObservationWorkerTest'))
    run.COUNTS=COUNTS
    run.SESSION_ID='PG9156-API-OBSERVATION-CONTEXT'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])==['dev.codex.schubert.nk.api.monitoring.ApiObservationContextTest']
    cases=re.findall(r'void\s+(obsCtx\d{3})',run.NEW_TEST.read_text())
    assert len(cases)==26 and set(cases)=={'obsCtx'+str(i).zfill(3) for i in range(1,27)} and run.NEW_TEST.read_text().count('@Test')==26
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
