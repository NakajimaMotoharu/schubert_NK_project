"""Existing whole API/Web loader Tests: memory sources, factory binding only, no actual file read."""
import re
import scoped_prometheus_host as run

SOURCE = 'a90e303fc59938d413c2d777380bdffbe3e7f9e7'
COMPILE = run.host.W/'pg13536-main-assignment-final-four-v1'
COMPILE_SHA = '12e04040d67762a748e6d7f9898604ee38717c75eb6a15fb92a762391d963a48'
COUNTS = {'ApiConfigurationLoaderTest':5,'WebConfigurationLoaderTest':5}
SESSION = 'PG13550-CONFIG-LOADERS-CURRENT-WHOLE10'
TESTS = {
 'ApiConfigurationLoaderTest':run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiConfigurationLoaderTest.java',
 'WebConfigurationLoaderTest':run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebConfigurationLoaderTest.java',
}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13550-config-loaders-ten-pt-v1'
    run.OUT = run.host.BASE/'PG13550-config-loaders-ten-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/ConfigLoadersCurrentJunitLauncher.java'
    run.NEW_TEST = TESTS['ApiConfigurationLoaderTest']
    run.TEST_SOURCE_OVERRIDES = {'WebConfigurationLoaderTest':TESTS['WebConfigurationLoaderTest']}
    run.EXTRA_TEST_SOURCES = ()
    run.FIXTURES = {}
    run.COUNTS = COUNTS
    run.SESSION_ID = SESSION
    for name,path in TESTS.items():
        text = path.read_text()
        assert text.count('@Test') == COUNTS[name] and len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == COUNTS[name]
        assert not any(value in text for value in ['@BeforeAll','@BeforeEach','@TempDir','DriverManager','getConnection(','java.net.','java.nio.file.','ProcessBuilder','Runtime.getRuntime','setAccessible','LinuxDirectoryCalls','LinuxInodeSecurity','getDeclared'])
        assert text.count('assertNotNull('+name.removesuffix('Test')+'.production());') == 1
        assert 'NonSecretConfigSource source' in text
    selected = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected) == 1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0]) == ['dev.codex.schubert.nk.api.bootstrap.ApiConfigurationLoaderTest','dev.codex.schubert.nk.web.bootstrap.WebConfigurationLoaderTest']
    assert run.SLOT.name.upper() == run.OUT.name.upper()
    run.main()
