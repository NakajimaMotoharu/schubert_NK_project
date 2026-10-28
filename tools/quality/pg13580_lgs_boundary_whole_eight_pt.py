"""One existing whole memory-only LGS Test, with two independent boundary subvectors."""
import re
import scoped_prometheus_host as run

SOURCE = 'e8e06bedba3311c8335dbb5ba9c4fdffafd86acf'
COMPILE = run.host.W/'pg13572-lgs-boundary-two-vectors-v1'
COMPILE_SHA = '849422e3b3794d6c1d580ffc016c36e1bc83b8864eefd33ab1eae10b3793db7a'
COUNTS = {'LogSearchWireClientTest': 8}
SESSION = 'PG13580-LGS-BOUNDARY-CURRENT-WHOLE8'
TESTS = {'LogSearchWireClientTest': run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/LogSearchWireClientTest.java'}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13580-lgs-boundary-whole-eight-pt-v1'
    run.OUT = run.host.BASE/'PG13580-lgs-boundary-whole-eight-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/LgsBoundaryCurrentJunitLauncher.java'
    run.NEW_TEST = TESTS['LogSearchWireClientTest']
    run.TEST_SOURCE_OVERRIDES = {}
    run.EXTRA_TEST_SOURCES = ()
    run.FIXTURES = {}
    run.COUNTS = COUNTS
    run.SESSION_ID = SESSION
    text = run.NEW_TEST.read_text()
    assert text.count('@Test') == 8 and len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(', text)) == 8
    assert not any(value in text for value in ['@BeforeAll', '@BeforeEach', '@TempDir', 'DriverManager', 'getConnection(', 'java.net.', 'java.nio.file.', 'ProcessBuilder', 'Runtime.getRuntime', 'setAccessible', 'LinuxDirectoryCalls', 'LinuxInodeSecurity', 'getDeclared'])
    selected = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);', run.HELPER.read_text(), re.S)
    assert len(selected) == 1 and re.findall(r'"([a-zA-Z0-9_.]+)"', selected[0]) == ['dev.codex.schubert.nk.web.messaging.LogSearchWireClientTest']
    assert run.SLOT.name.upper() == run.OUT.name.upper()
    run.main()
