"""New OUTBOXPUMP32 only; three supporting fixture outers are compile-only, never selected."""
import re
import scoped_prometheus_host as run
SOURCE='f82e3e1ee6d6090b1b81222d18fd35366d0637c1'
COMPILE=run.host.W/'pg9118-api-outbox-pump-six-compile-v2'
COMPILE_SHA='23bbd17c711949852ec9c71b7a7cf49caeef26f917e8f13328c4680c92fd0227'
COUNTS={'ApiOutboxObservationPumpTest':32}

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9120-api-outbox-pump-host-v1'
    run.OUT=run.host.BASE/'PG9120-api-outbox-pump-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiOutboxPumpJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiOutboxObservationPumpTest.java'
    run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=tuple(run.host.ROOT/f'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/{name}.java' for name in ('DbPoolMetricObservationTest','OutboxObservationRepositoryTest','ApiReadOnlyObservationAttemptTest'))
    run.COUNTS=COUNTS
    run.SESSION_ID='PG9120-API-OUTBOX-PUMP'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])==['dev.codex.schubert.nk.api.monitoring.ApiOutboxObservationPumpTest']
    cases=re.findall(r'void\s+(outboxPump\d{3})',run.NEW_TEST.read_text())
    assert len(cases)==32 and set(cases)=={'outboxPump'+str(i).zfill(3) for i in range(1,33)} and run.NEW_TEST.read_text().count('@Test')==32
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
