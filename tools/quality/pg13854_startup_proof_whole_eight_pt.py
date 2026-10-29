"""Whole public placeholder frame tests: no actual startup authority, FD or Root operation."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE = '0061d178cda80c2ce3926290619c64db125dbcfc'
COMPILE = run.host.W/'pg13832-snapshot-program-six-compile-v1'
COMPILE_SHA = '8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
COUNTS = {'StartupProofFrameTest':8}
SESSION = 'PG13854-STARTUP-PROOF-FRAME-CURRENT-WHOLE8'
TESTS = {'StartupProofFrameTest':run.host.ROOT/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/StartupProofFrameTest.java'}
REPORTER = run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__ == '__main__':
    run.SOURCE = SOURCE;run.COMPILE = COMPILE;run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13854-startup-proof-whole-eight-pt-v1'
    run.OUT = run.host.BASE/'PG13854-startup-proof-whole-eight-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/StartupProofFrameCurrentJunitLauncher.java'
    run.NEW_TEST = TESTS['StartupProofFrameTest']
    run.TEST_SOURCE_OVERRIDES = {};run.EXTRA_TEST_SOURCES = (REPORTER,);run.FIXTURES = {}
    run.COUNTS = COUNTS;run.SESSION_ID = SESSION
    proof = data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit'] == proof['productTestsExecuted'] == 0 and proof['toolChecksIndependentlyConfirmed'] == 12
    assert run.host.sha(REPORTER) == proof['toolSourceHashes'][str(REPORTER)] == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.NEW_TEST) == '658c1736b4d4d0927d4db12eac869c5bf66dd8a29c862993d26780d52341fa59'
    text = run.NEW_TEST.read_text()
    assert text.count('@Test') == len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == 8
    assert not any(term in text for term in ['@BeforeAll','@BeforeEach','@TempDir','Files.','ProcessBuilder','Runtime.getRuntime','setAccessible','LinuxDirectoryCalls','NativeReader','RootStartupContext','TemporaryInfrastructureException','WebStartupException'])
    assert 'Map.of("dev.codex.schubert.nk.bootstrap.StartupProofFrameTest", 8)' in run.HELPER.read_text()
    run.main()
