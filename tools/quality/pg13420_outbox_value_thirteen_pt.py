"""Whole existing four pure value Test classes/13 cases; no DB/JMS/held graph invocation."""
import re
import scoped_prometheus_host as run

SOURCE = '8a518b2535a1d29ce1493fa56ed7be285a540201'
COMPILE = run.host.W/'pg13406-remaining-test-literal-v1'
COMPILE_SHA = '9e2d9cb725eb737281649a7eebeab2ca8ab561c41d2bdf5eef9e6b1a6436debe'
COUNTS = {'OutboxPolicyTest':4,'OutboxModelTest':4,'OutboxDlqMetadataTest':2,'OutboxDispatchReportBoundaryTest':3}
SESSION = 'PG13420-OUTBOX-CURRENT-WHOLE13'
ROOT = run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound'

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13420-outbox-value-thirteen-pt-v1'
    run.OUT = run.host.BASE/'PG13420-outbox-value-thirteen-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/OutboxCurrentValueJunitLauncher.java'
    run.NEW_TEST = ROOT/'OutboxModelTest.java'
    run.TEST_SOURCE_OVERRIDES = {name:ROOT/(name+'.java') for name in COUNTS if name != run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES = ()
    run.FIXTURES = {}
    run.COUNTS = COUNTS
    run.SESSION_ID = SESSION
    for name,count in COUNTS.items():
        text = (ROOT/(name+'.java')).read_text()
        assert text.count('@Test') == count and len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == count
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','@TempDir','TemporaryInfrastructureException','DriverManager','getConnection(','java.net.','java.nio.file.','ProcessBuilder','Runtime.getRuntime','getSuppressed('])
    selected = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected) == 1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0]) == ['dev.codex.schubert.nk.api.messaging.outbound.'+name for name in COUNTS]
    assert run.SLOT.name.upper() == run.OUT.name.upper()
    run.main()
