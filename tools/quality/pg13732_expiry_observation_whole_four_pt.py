"""Existing whole four data-only record invariants; synthetic gate ports are not native authority."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
COMPILE = run.host.W/'pg13596-lgs-remaining-two-branches-v1'
COMPILE_SHA = '1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12'
COUNTS = {'MorningExpiryObservationInvariantTest':4}
SESSION = 'PG13732-EXPIRY-OBSERVATION-CURRENT-WHOLE4'
TESTS = {'MorningExpiryObservationInvariantTest':run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningExpiryObservationInvariantTest.java'}
FIXTURE = run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ExpiryReceiptFixture.java'
REPORTER = run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13732-expiry-observation-whole-four-pt-v1'
    run.OUT = run.host.BASE/'PG13732-expiry-observation-whole-four-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/ExpiryObservationCurrentFourJunitLauncher.java'
    run.NEW_TEST = TESTS['MorningExpiryObservationInvariantTest']
    run.TEST_SOURCE_OVERRIDES = {}
    run.EXTRA_TEST_SOURCES = (FIXTURE,REPORTER)
    run.FIXTURES = {}
    run.COUNTS = COUNTS
    run.SESSION_ID = SESSION
    proof = data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit'] == proof['productTestsExecuted'] == 0 and proof['toolChecksIndependentlyConfirmed'] == 12 and proof['reporterReexecuted'] is False
    assert run.host.sha(REPORTER) == proof['toolSourceHashes'][str(REPORTER)] == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.NEW_TEST) == '7daa2c142d09b03d16033551d7601352b51540ceadcba5eaf16d0455d7ee912f'
    assert run.host.sha(FIXTURE) == 'abf309d8c2126bbad37c7c2024c95aa6a59965f74053f306fd7ed337c7747375'
    text = run.NEW_TEST.read_text();fixture = FIXTURE.read_text()
    assert text.count('@Test') == 4 and len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == 4
    assert not any(v in text+fixture for v in ['@BeforeAll','@BeforeEach','@TempDir','DriverManager','getConnection(', 'java.nio.file.','ProcessBuilder','Runtime.getRuntime','setAccessible','LinuxDirectoryCalls','NativeReader','RootStartupContext','TemporaryInfrastructureException','WebStartupException','requireStillPresent('])
    assert 'new BackupUnitReceiptGate(\n            () -> {}, () -> Optional.of(state.get()), () -> Optional.of(state.get()), target)' in fixture
    helper = run.HELPER.read_text()
    assert re.findall(r'Map\.of\(\s*"([a-zA-Z0-9_.$]+)"\s*,\s*(\d+)\s*\)',helper,re.S) == [('dev.codex.schubert.nk.batch.repository.MorningExpiryObservationInvariantTest','4')]
    assert helper.count('SharedSelectedJunitReporterV1.run(args, Map.of(') == 1
    assert run.SLOT.name.upper() == run.OUT.name.upper()
    run.main()
