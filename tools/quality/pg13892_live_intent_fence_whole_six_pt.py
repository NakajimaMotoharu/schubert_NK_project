"""Existing whole6 memory ports only; never real service start, marker retirement or native clock."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE = '0061d178cda80c2ce3926290619c64db125dbcfc'
COMPILE = run.host.W/'pg13832-snapshot-program-six-compile-v1'
COMPILE_SHA = '8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
COUNTS = {'ServiceIntentReadyRetirementTest':3,'CaddyAdmissionFenceTest':3}
SESSION = 'PG13892-LIVE-INTENT-FENCE-MEMORY-CURRENT-WHOLE6'
ROOT = run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform'
TESTS = {name:ROOT/(name+'.java') for name in COUNTS}
PINS = {'ServiceIntentReadyRetirementTest':'ec35e75ff9142cd1482985be8348863e2787c4ca7f13b2c52828961bdca257f8',
    'CaddyAdmissionFenceTest':'2cf7d24a3c423a4d35bd7fb0b1e6caba7b4ce1585ab8c3c156c8d39afb4dcc23',
    'InspectorUnitProbeFixture':'75b62aea8f3e4fbc558ec24698c7ff7d1faf4f477f34addb17e5e58f1283da2b',
    'InspectorUnitSnapshotTest':'edf0ce67d649d340e2e61907cc8228cd9c44fe08a21a9f011d81cdcbef4d1a63'}
REPORTER = run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__ == '__main__':
    run.SOURCE = SOURCE;run.COMPILE = COMPILE;run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13892-live-intent-fence-whole-six-pt-v1'
    run.OUT = run.host.BASE/'PG13892-live-intent-fence-whole-six-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/LiveIntentFenceMemoryCurrentJunitLauncher.java'
    run.NEW_TEST = TESTS['ServiceIntentReadyRetirementTest']
    run.TEST_SOURCE_OVERRIDES = {'CaddyAdmissionFenceTest':TESTS['CaddyAdmissionFenceTest']}
    run.EXTRA_TEST_SOURCES = (REPORTER,ROOT/'InspectorUnitProbeFixture.java',ROOT/'InspectorUnitSnapshotTest.java')
    run.FIXTURES = {};run.COUNTS = COUNTS;run.SESSION_ID = SESSION
    proof = data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit'] == proof['productTestsExecuted'] == 0 and proof['toolChecksIndependentlyConfirmed'] == 12
    assert run.host.sha(REPORTER) == proof['toolSourceHashes'][str(REPORTER)] == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert all(run.host.sha(ROOT/(name+'.java')) == sha for name,sha in PINS.items())
    for name,path in TESTS.items():
        text = path.read_text()
        assert text.count('@Test') == len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == COUNTS[name]
        assert 'new BackupUnitStartClient(' in text and 'Optional.empty()' in text
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','Files.','DriverManager','ProcessBuilder','LinuxDirectoryCalls','MorningParentBudget.create','BackupUnitStartClient.create(','BackupUnitStartClient.createService(','BackupUnitStartClient.createCaddy('])
        assert '"dev.codex.schubert.nk.batch.platform.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.main()
