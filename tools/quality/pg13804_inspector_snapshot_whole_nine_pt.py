"""Whole9 fixed-text parser PT with committed golden and own-CWD scalar trace only."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
COMPILE = run.host.W/'pg13596-lgs-remaining-two-branches-v1'
COMPILE_SHA = '1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12'
COUNTS = {'InspectorUnitSnapshotTest':9}
SESSION = 'PG13804-INSPECTOR-SNAPSHOT-CURRENT-WHOLE9'
TESTS = {'InspectorUnitSnapshotTest':run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshotTest.java'}
REPORTER = run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
FIXTURE = 'src/schubert-nk-batch/src/test/resources/inspector/unit-golden.txt'
GOLDEN_SHA = '2170fc2e71a4ba50519bc2f123d0bf75fcc46adab033645b7b68b5c513c345f6'

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13804-inspector-snapshot-whole-nine-pt-v1'
    run.OUT = run.host.BASE/'PG13804-inspector-snapshot-whole-nine-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/InspectorSnapshotCurrentNineJunitLauncher.java'
    run.NEW_TEST = TESTS['InspectorUnitSnapshotTest']
    run.TEST_SOURCE_OVERRIDES = {}
    run.EXTRA_TEST_SOURCES = (REPORTER,)
    run.FIXTURES = {FIXTURE:GOLDEN_SHA}
    run.COUNTS = COUNTS
    run.SESSION_ID = SESSION
    proof = data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit'] == proof['productTestsExecuted'] == 0 and proof['toolChecksIndependentlyConfirmed'] == 12
    assert run.host.sha(REPORTER) == proof['toolSourceHashes'][str(REPORTER)] == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.NEW_TEST) == '8867d83662dfdd84a72b5bfe60e4bbd0b0d0877fb3590b08a7f4f9f45f1e7da5'
    assert len((run.host.ROOT/FIXTURE).read_bytes()) == 373 and run.host.sha(run.host.ROOT/FIXTURE) == GOLDEN_SHA
    text = run.NEW_TEST.read_text()
    assert text.count('@Test') == 9 and len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == 9
    assert not any(v in text for v in ['@BeforeAll','@BeforeEach','@TempDir','DriverManager','getConnection(', 'ProcessBuilder','Runtime.getRuntime','setAccessible','LinuxDirectoryCalls','NativeReader','RootStartupContext','TemporaryInfrastructureException','WebStartupException','InspectorUnitProbe','MaintenanceOwnerFrame','/proc/','/run/'])
    assert 'Path target = Path.of("target", "inspector-unit-traces");' in text and text.count('Files.writeString(') == text.count('Files.createDirectories(') == 1
    assert 'getResourceAsStream("/inspector/unit-golden.txt")' in text
    helper = run.HELPER.read_text()
    assert re.findall(r'Map\.of\(\s*"([a-zA-Z0-9_.$]+)"\s*,\s*(\d+)\s*\)',helper,re.S) == [('dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshotTest','9')]
    assert helper.count('SharedSelectedJunitReporterV1.run(args, Map.of(') == 1
    assert run.SLOT.name.upper() == run.OUT.name.upper()
    run.main()
