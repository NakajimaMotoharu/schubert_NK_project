"""Two complete existing memory-only owner Tests; fake integer descriptors, no OS/native resource."""
import re
import scoped_prometheus_host as run

SOURCE = 'df0c755d82564f2a637206a1bda5c33c7df7006c'
COMPILE = run.host.W/'pg13506-main-assignment-seven-v1'
COMPILE_SHA = '821f7dee356d4af38311c7cac5f79254e06f6aa8d4d3cf9bfd70e65be018595b'
COUNTS = {'StartupAdmissionViewOwnerTest':8,'CgroupPrimitiveOwnerTest':8}
SESSION = 'PG13520-PRIMITIVE-OWNER-CURRENT-WHOLE16'
TESTS = {
    'StartupAdmissionViewOwnerTest':run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/StartupAdmissionViewOwnerTest.java',
    'CgroupPrimitiveOwnerTest':run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/CgroupPrimitiveOwnerTest.java',
}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13520-primitive-owner-sixteen-pt-v1'
    run.OUT = run.host.BASE/'PG13520-primitive-owner-sixteen-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/PrimitiveOwnerCurrentJunitLauncher.java'
    run.NEW_TEST = TESTS['StartupAdmissionViewOwnerTest']
    run.TEST_SOURCE_OVERRIDES = {'CgroupPrimitiveOwnerTest':TESTS['CgroupPrimitiveOwnerTest']}
    run.EXTRA_TEST_SOURCES = ()
    run.FIXTURES = {}
    run.COUNTS = COUNTS
    run.SESSION_ID = SESSION
    for name,path in TESTS.items():
        text = path.read_text()
        assert text.count('@Test') == COUNTS[name] and len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == COUNTS[name]
        assert not any(value in text for value in ['@BeforeAll','@BeforeEach','@TempDir','DriverManager','getConnection(','java.net.','java.nio.file.','ProcessBuilder','Runtime.getRuntime','setAccessible','LinuxDirectoryCalls','LinuxInodeSecurity','getDeclared'])
        assert 'Proxy.newProxyInstance(' in text and 'no other native capability' in text
    selected = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected) == 1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0]) == ['dev.codex.schubert.nk.batch.file.StartupAdmissionViewOwnerTest','dev.codex.schubert.nk.batch.platform.CgroupPrimitiveOwnerTest']
    assert run.SLOT.name.upper() == run.OUT.name.upper()
    run.main()
