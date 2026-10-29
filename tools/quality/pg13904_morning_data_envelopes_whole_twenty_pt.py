"""Original whole20, existing literal fixtures and memory callbacks; no native/DB/Root execution."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE = '0061d178cda80c2ce3926290619c64db125dbcfc'
COMPILE = run.host.W/'pg13832-snapshot-program-six-compile-v1'
COMPILE_SHA = '8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
COUNTS = {'MorningPrestartEvidenceTest':5,'MorningCompletionEvidenceTest':11,'StoppedBackupCompletionTest':4}
SESSION = 'PG13904-MORNING-DATA-ENVELOPES-CURRENT-WHOLE20'
ROOT = run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch'
TESTS = {name:ROOT/'file'/(name+'.java') for name in COUNTS}
PINS = {
    'MorningPrestartEvidenceTest':'b58a35ec59e2f413756b7acb5bcf779939348df891d8cb12937b9af0fbc18440',
    'MorningCompletionEvidenceTest':'1f52f96a806c8d38bb2df64d2eb0376f25b344af6f3428e4ff00f009d86f3b0c',
    'StoppedBackupCompletionTest':'a01fc1385cdbf56e06787116be9178b1707314acee83a5a475541bcd6c80c49b',
}
EXTRAS = {
    'platform/StoppedBackupFixture.java':'11ef7eaebae015e6d42f8b8808c5e794be382b0e316b32e03253e426cd2c070b',
    'platform/ExpiryReceiptFixture.java':'abf309d8c2126bbad37c7c2024c95aa6a59965f74053f306fd7ed337c7747375',
    'file/MorningCompletedMainTest.java':'2ebc63c919fc2db084c905f67191f6927fc37bc45d80a10b60a52e792c0d04b6',
    'repository/BackupStepFixture.java':'c41b963d540a369a519b5a3b3504faf8187ab6f63f3dde5d72f59aad3e3171ec',
    'repository/BatchDatabaseFixture.java':'ad3567863c78e5cbbbe28cd1c2b38c2005113abb3bd0f9184cda190d0c886023',
}
FIXTURES = {
    'src/schubert-nk-batch/src/test/resources/ops/issuer-prestart-failed-v2-golden.txt':'eda4285f0df2c54a4ca10946013dbfc145440da6999637ca035f56ec86a66d4a',
    'src/schubert-nk-batch/src/test/resources/ops/issuer-prestart-new-v2-golden.txt':'842b41b0e1f131f65fef2127bee72ae840e94dfa67c4c3240799608d8a553b1c',
    'src/schubert-nk-batch/src/test/resources/ops/issuer-prestart-reused-v2-golden.txt':'f5877b39aece1cbbd31e9016fdb34ea65fb4ddc933e93428ab4d6b2f0ad6849e',
}
REPORTER = run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__ == '__main__':
    run.SOURCE = SOURCE;run.COMPILE = COMPILE;run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13904-morning-data-envelopes-whole-twenty-pt-v1'
    run.OUT = run.host.BASE/'PG13904-morning-data-envelopes-whole-twenty-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/MorningDataEnvelopeCurrentJunitLauncher.java'
    run.NEW_TEST = TESTS['MorningPrestartEvidenceTest']
    run.TEST_SOURCE_OVERRIDES = {n:p for n,p in TESTS.items() if n != run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES = (REPORTER,*(ROOT/p for p in EXTRAS))
    run.FIXTURES = FIXTURES;run.COUNTS = COUNTS;run.SESSION_ID = SESSION
    proof = data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit'] == proof['productTestsExecuted'] == 0 and proof['toolChecksIndependentlyConfirmed'] == 12
    assert run.host.sha(REPORTER) == proof['toolSourceHashes'][str(REPORTER)] == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert all(run.host.sha(ROOT/p) == sha for p,sha in EXTRAS.items())
    for name,path in TESTS.items():
        text = path.read_text()
        assert run.host.sha(path) == PINS[name]
        assert text.count('@Test') == len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningParentBudget.create','MorningProcessMain.runCompleted(','MorningProcessMain.main('])
        assert '"dev.codex.schubert.nk.batch.file.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.main()
