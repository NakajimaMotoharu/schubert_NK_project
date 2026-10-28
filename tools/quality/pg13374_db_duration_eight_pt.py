"""Existing whole8 changed Test, own SDK/threads only; fixed fresh normal and no held graph/DB."""
import re
import scoped_prometheus_host as run
SOURCE = 'a75a490666973b2d1fc9b4901290074aa1c32a0f'
COMPILE = run.host.W/'pg13362-api-maintenance-literal-v1'
COMPILE_SHA = '44e2344df9c30086f80a2fcecb59103373f79e4feed09e0915e1da0bb560f5ae'
COUNTS = {'DbQueryDurationMetricCollectorTest':8}
SESSION = 'PG13374-DB-DURATION-EXISTING-WHOLE8'
if __name__ == '__main__':
    run.SOURCE = SOURCE;run.COMPILE = COMPILE;run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13374-db-duration-eight-pt-v1';run.OUT = run.host.BASE/'PG13374-db-duration-eight-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/DbDurationCollectorJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/DbQueryDurationMetricCollectorTest.java'
    run.TEST_SOURCE_OVERRIDES = {};run.EXTRA_TEST_SOURCES = ();run.FIXTURES = {};run.COUNTS = COUNTS;run.SESSION_ID = SESSION
    text = run.NEW_TEST.read_text();cases = re.findall(r'void\s+(dbConn\d{3}\w*)\s*\(',text)
    assert len(cases) == text.count('@Test') == 8 and {m[:9] for m in cases} == {'dbConn'+str(i).zfill(3) for i in range(1,9)}
    assert not any(v in text for v in ['@BeforeAll','TemporaryInfrastructureException','java.sql.','java.net.','java.nio.file.','ProcessBuilder','Runtime.getRuntime'])
    selected = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected) == 1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0]) == ['dev.codex.schubert.nk.api.monitoring.DbQueryDurationMetricCollectorTest']
    assert run.SLOT.name.upper() == run.OUT.name.upper()
    run.main()
