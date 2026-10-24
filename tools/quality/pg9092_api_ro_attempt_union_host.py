"""New ROATTEMPT32 only, original returned XML; JDBC repository fixture outer compile-only."""
import re
import scoped_prometheus_host as run
SOURCE='e87ab6ec893fa461dc98e6525e6bbc9885701f32'
COMPILE=run.host.W/'pg9090-api-ro-attempt-union-six-compile-v1'
COMPILE_SHA='897bae9e89031afe883755b1e502b356b0a76f00ed3a60e505f4f5e974d823ad'
COUNTS={'ApiReadOnlyObservationAttemptTest':32}

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9092-api-ro-attempt-union-host-v1'
    run.OUT=run.host.BASE/'PG9092-api-ro-attempt-union-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiReadOnlyAttemptJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiReadOnlyObservationAttemptTest.java'
    run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OutboxObservationRepositoryTest.java',)
    run.COUNTS=COUNTS
    run.SESSION_ID='PG9092-API-RO-ATTEMPT-UNION'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])==['dev.codex.schubert.nk.api.monitoring.ApiReadOnlyObservationAttemptTest']
    cases=re.findall(r'void\s+(roAttempt\d{3})',run.NEW_TEST.read_text())
    assert len(cases)==32 and set(cases)=={'roAttempt'+str(i).zfill(3) for i in range(1,33)} and run.NEW_TEST.read_text().count('@Test')==32
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
