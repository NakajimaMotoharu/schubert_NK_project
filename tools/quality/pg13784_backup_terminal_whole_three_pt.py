"""Existing whole3 terminal data projection PT, not actual Backup/DB/Root authority."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
COMPILE = run.host.W/'pg13596-lgs-remaining-two-branches-v1'
COMPILE_SHA = '1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12'
COUNTS = {'BackupTerminalObservationTest':3}
SESSION = 'PG13784-BACKUP-TERMINAL-CURRENT-WHOLE3'
TESTS = {'BackupTerminalObservationTest':run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/BackupTerminalObservationTest.java'}
REPORTER = run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13784-backup-terminal-whole-three-pt-v1'
    run.OUT = run.host.BASE/'PG13784-backup-terminal-whole-three-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/BackupTerminalCurrentThreeJunitLauncher.java'
    run.NEW_TEST = TESTS['BackupTerminalObservationTest']
    run.TEST_SOURCE_OVERRIDES = {}
    run.EXTRA_TEST_SOURCES = (REPORTER,)
    run.FIXTURES = {}
    run.COUNTS = COUNTS
    run.SESSION_ID = SESSION
    proof = data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit'] == proof['productTestsExecuted'] == 0 and proof['toolChecksIndependentlyConfirmed'] == 12
    assert run.host.sha(REPORTER) == proof['toolSourceHashes'][str(REPORTER)] == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.NEW_TEST) == 'dc454eff471dd12976b0fd0acc6df8eb9c6edcbfcfbe71a9ace0087461b30311'
    text = run.NEW_TEST.read_text()
    assert text.count('@Test') == 3 and len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == 3
    assert not any(v in text for v in ['@BeforeAll','@BeforeEach','@TempDir','DriverManager','getConnection(', 'java.nio.file.','ProcessBuilder','Runtime.getRuntime','setAccessible','LinuxDirectoryCalls','NativeReader','RootStartupContext','TemporaryInfrastructureException','WebStartupException','new MorningDatabaseSession(','new BackupStepRepository(','BatchDatabaseFixture','MaintenanceOwnerFrame'])
    assert text.count('Proxy.newProxyInstance(') == 2 and 'BackupStepRepository.readTerminal(' in text
    helper = run.HELPER.read_text()
    assert re.findall(r'Map\.of\(\s*"([a-zA-Z0-9_.$]+)"\s*,\s*(\d+)\s*\)',helper,re.S) == [('dev.codex.schubert.nk.batch.repository.BackupTerminalObservationTest','3')]
    assert helper.count('SharedSelectedJunitReporterV1.run(args, Map.of(') == 1
    assert run.SLOT.name.upper() == run.OUT.name.upper()
    run.main()
