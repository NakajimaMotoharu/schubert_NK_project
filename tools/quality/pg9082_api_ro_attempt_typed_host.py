"""New ROATTEMPT32 only, original returned XML; JDBC repository fixture outer compile-only."""
import re
import scoped_prometheus_host as run
SOURCE='b66e59ede8145586fbe2407881ff342aeee80d31'
COMPILE=run.host.W/'pg9080-api-ro-attempt-typed-six-compile-v1'
COMPILE_SHA='a57e600d9e8dcc6d2e83ddc1c02297043ed51cd63f6303692b6ecb9a22271f97'
COUNTS={'ApiReadOnlyObservationAttemptTest':32}

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9082-api-ro-attempt-typed-host-v1'
    run.OUT=run.host.BASE/'PG9082-api-ro-attempt-typed-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiReadOnlyAttemptJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiReadOnlyObservationAttemptTest.java'
    run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OutboxObservationRepositoryTest.java',)
    run.COUNTS=COUNTS
    run.SESSION_ID='PG9082-API-RO-ATTEMPT-TYPED'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])==['dev.codex.schubert.nk.api.monitoring.ApiReadOnlyObservationAttemptTest']
    cases=re.findall(r'void\s+(roAttempt\d{3})',run.NEW_TEST.read_text())
    assert len(cases)==32 and set(cases)=={'roAttempt'+str(i).zfill(3) for i in range(1,33)} and run.NEW_TEST.read_text().count('@Test')==32
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
