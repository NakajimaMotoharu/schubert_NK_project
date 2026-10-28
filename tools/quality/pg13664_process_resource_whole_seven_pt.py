"""Existing whole seven: own fake Process/streams/threads; no actual native process start or command."""
import re
import scoped_prometheus_host as run

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
COMPILE = run.host.W/'pg13596-lgs-remaining-two-branches-v1'
COMPILE_SHA = '1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12'
COUNTS = {'ProcessResourceScopeTest': 7}
SESSION = 'PG13664-PROCESS-RESOURCE-CURRENT-WHOLE7'
TESTS = {'ProcessResourceScopeTest':run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ProcessResourceScopeTest.java'}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13664-process-resource-whole-seven-pt-v1'
    run.OUT = run.host.BASE/'PG13664-process-resource-whole-seven-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/ProcessResourceCurrentJunitLauncher.java'
    run.NEW_TEST = TESTS['ProcessResourceScopeTest']
    run.TEST_SOURCE_OVERRIDES = {}
    run.EXTRA_TEST_SOURCES = ()
    run.FIXTURES = {}
    run.COUNTS = COUNTS
    run.SESSION_ID = SESSION
    text = run.NEW_TEST.read_text()
    assert run.host.sha(run.NEW_TEST) == 'cf94df05fa8559b35af74879256271b41df718f7f5eb1b5251cc0a9f42d99d06'
    assert text.count('@Test') == 7 and len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == 7
    assert not any(value in text for value in ['@BeforeAll','@BeforeEach','@TempDir','DriverManager','getConnection(', 'java.net.','java.nio.file.','ProcessBuilder','Runtime.getRuntime','setAccessible','LinuxDirectoryCalls','LinuxInodeSecurity','getDeclared','new SystemctlStateSource()','new InspectorUnitProbe.NativeReader()','NativeReader.forTarget('])
    assert 'new SystemctlStateSource(command -> child)' in text
    assert 'class Child extends Process' in text and 'class StreamingChild extends Process' in text
    selected = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected) == 1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0]) == ['dev.codex.schubert.nk.batch.platform.ProcessResourceScopeTest']
    assert run.SLOT.name.upper() == run.OUT.name.upper()
    run.main()
