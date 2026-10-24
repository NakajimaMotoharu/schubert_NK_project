"""New ROATTEMPT32 only, original returned XML; JDBC repository fixture outer compile-only."""
import re
import scoped_prometheus_host as run
SOURCE='42411011d8d7f5e2a70af11a6f8855313adbe1b8'
COMPILE=run.host.W/'pg9064-api-ro-attempt-six-compile-v1'
COMPILE_SHA='5a3e67a929927fa982a6a0f44064b21bf930ad2ff1bf20d97ad9d17c971a3858'
COUNTS={'ApiReadOnlyObservationAttemptTest':32}

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9066-api-ro-attempt-host-v1'
    run.OUT=run.host.BASE/'PG9066-api-ro-attempt-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiReadOnlyAttemptJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiReadOnlyObservationAttemptTest.java'
    run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OutboxObservationRepositoryTest.java',)
    run.COUNTS=COUNTS
    run.SESSION_ID='PG9066-API-RO-ATTEMPT'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])==['dev.codex.schubert.nk.api.monitoring.ApiReadOnlyObservationAttemptTest']
    cases=re.findall(r'void\s+(roAttempt\d{3})',run.NEW_TEST.read_text())
    assert len(cases)==32 and set(cases)=={'roAttempt'+str(i).zfill(3) for i in range(1,33)} and run.NEW_TEST.read_text().count('@Test')==32
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
