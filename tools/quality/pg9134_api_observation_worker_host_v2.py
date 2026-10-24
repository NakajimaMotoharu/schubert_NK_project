"""New OBSOWN44 own JVM/fake observation only; supporting fixture outers are compile-only."""
import re
import scoped_prometheus_host as run
SOURCE='fdc229c9a7b7759cea106d1126c8da0f27a70e09'
COMPILE=run.host.W/'pg9132-api-observation-worker-six-compile-v4'
COMPILE_SHA='e0ffc872d61a2eb6b4556de13eabcd0173e957ed9b832d2df29088f6308e4ac1'
COUNTS={'OwnedApiObservationWorkerTest':44}

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9134-api-observation-worker-host-v2'
    run.OUT=run.host.BASE/'PG9134-api-observation-worker-host-v2'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiObservationWorkerJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OwnedApiObservationWorkerTest.java'
    run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=tuple(run.host.ROOT/f'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/{name}.java' for name in ('DbPoolMetricObservationTest','OutboxObservationRepositoryTest','ApiReadOnlyObservationAttemptTest','ApiOutboxObservationPumpTest'))
    run.COUNTS=COUNTS
    run.SESSION_ID='PG9134-API-OBSERVATION-WORKER-V2'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])==['dev.codex.schubert.nk.api.monitoring.OwnedApiObservationWorkerTest']
    cases=re.findall(r'void\s+(obsOwn\d{3})',run.NEW_TEST.read_text())
    assert len(cases)==44 and set(cases)=={'obsOwn'+str(i).zfill(3) for i in range(1,45)} and run.NEW_TEST.read_text().count('@Test')==44
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
