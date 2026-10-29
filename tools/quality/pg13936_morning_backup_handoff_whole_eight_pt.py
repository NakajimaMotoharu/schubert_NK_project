"""Original whole8 literal backup handoff/completion tests; no real backup or DB."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE = '0061d178cda80c2ce3926290619c64db125dbcfc'
COMPILE = run.host.W/'pg13832-snapshot-program-six-compile-v1'
COMPILE_SHA = '8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
COUNTS = {'MorningBackupPreparationTest':6,'MorningBackupCompletionTest':2}
SESSION = 'PG13936-MORNING-BACKUP-HANDOFF-CURRENT-WHOLE8'
ROOT = run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch'
TESTS = {name:ROOT/'file'/(name+'.java') for name in COUNTS}
PINS = {'MorningBackupPreparationTest':'88b9b065043bbec45d836635cab6c7119f740a888abc0e068f396d622f11984a',
    'MorningBackupCompletionTest':'8c04d23af4a8b217c6132716630c0d3318c8a44584a29004aec2bdbe07ecb939'}
EXTRAS = {
    'platform/ExpiryReceiptFixture.java':'abf309d8c2126bbad37c7c2024c95aa6a59965f74053f306fd7ed337c7747375',
    'repository/BackupStepFixture.java':'c41b963d540a369a519b5a3b3504faf8187ab6f63f3dde5d72f59aad3e3171ec',
    'repository/BatchDatabaseFixture.java':'ad3567863c78e5cbbbe28cd1c2b38c2005113abb3bd0f9184cda190d0c886023'}
REPORTER = run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__ == '__main__':
    run.SOURCE = SOURCE;run.COMPILE = COMPILE;run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13936-morning-backup-handoff-whole-eight-pt-v1'
    run.OUT = run.host.BASE/'PG13936-morning-backup-handoff-whole-eight-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/MorningBackupHandoffCurrentJunitLauncher.java'
    run.NEW_TEST = TESTS['MorningBackupPreparationTest']
    run.TEST_SOURCE_OVERRIDES = {'MorningBackupCompletionTest':TESTS['MorningBackupCompletionTest']}
    run.EXTRA_TEST_SOURCES = (REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES = {};run.COUNTS = COUNTS;run.SESSION_ID = SESSION
    proof = data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit'] == proof['productTestsExecuted'] == 0 and proof['toolChecksIndependentlyConfirmed'] == 12
    assert run.host.sha(REPORTER) == proof['toolSourceHashes'][str(REPORTER)] == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert all(run.host.sha(ROOT/p) == sha for p,sha in EXTRAS.items())
    for name,path in TESTS.items():
        text = path.read_text();assert run.host.sha(path) == PINS[name]
        assert text.count('@Test') == len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','new BatchDatabaseFixture','MorningParentBudget.create(','MorningProcessMain.runCompleted(','MorningProcessMain.main('])
        assert '"dev.codex.schubert.nk.batch.file.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.main()
