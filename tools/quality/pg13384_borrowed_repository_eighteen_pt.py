"""Whole two changed Test classes/18 cases with owned JDBC doubles; no real DB or held graph."""
import re
import scoped_prometheus_host as run
SOURCE = 'a75a490666973b2d1fc9b4901290074aa1c32a0f'
COMPILE = run.host.W/'pg13362-api-maintenance-literal-v1'
COMPILE_SHA = '44e2344df9c30086f80a2fcecb59103373f79e4feed09e0915e1da0bb560f5ae'
COUNTS = {'AsyncJobCountRepositoryTest':8,'OutboxObservationRepositoryTest':10}
SESSION = 'PG13384-BORROWED-REPOSITORY-WHOLE18'
ROOT = run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
if __name__ == '__main__':
    run.SOURCE = SOURCE;run.COMPILE = COMPILE;run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13384-borrowed-repository-eighteen-pt-v1';run.OUT = run.host.BASE/'PG13384-borrowed-repository-eighteen-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/BorrowedRepositoryJunitLauncher.java'
    run.NEW_TEST = ROOT/'AsyncJobCountRepositoryTest.java';run.TEST_SOURCE_OVERRIDES = {'OutboxObservationRepositoryTest':ROOT/'OutboxObservationRepositoryTest.java'}
    run.EXTRA_TEST_SOURCES = ();run.FIXTURES = {};run.COUNTS = COUNTS;run.SESSION_ID = SESSION
    for name,count in COUNTS.items():
        text = (ROOT/(name+'.java')).read_text();prefix = 'asyncDb' if name.startswith('Async') else 'outboxDb';cases = re.findall(r'void\s+('+prefix+r'\d{3}\w*)\s*\(',text)
        assert len(cases) == text.count('@Test') == count and {m[len(prefix):len(prefix)+3] for m in cases} == {str(i).zfill(3) for i in range(1,count+1)}
        assert not any(v in text for v in ['@BeforeAll','TemporaryInfrastructureException','DriverManager','getConnection(','java.net.','java.nio.file.','ProcessBuilder','Runtime.getRuntime'])
        assert 'Proxy.newProxyInstance' in text and 'Connection.class' in text
    selected = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected) == 1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0]) == ['dev.codex.schubert.nk.api.monitoring.'+name for name in COUNTS]
    assert run.SLOT.name.upper() == run.OUT.name.upper()
    run.main()
