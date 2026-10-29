"""Three original supplied-value whole8 suites, no JDBC/actual heap or endpoint observation."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='0061d178cda80c2ce3926290619c64db125dbcfc'
COMPILE=run.host.W/'pg13832-snapshot-program-six-compile-v1'
COMPILE_SHA='8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
COUNTS={'TimedDbPoolMonitorTest':8,'TimedJvmHeapMonitorTest':8,'TimedSyncLatencyMonitorTest':8}
SESSION='PG14110-BATCH-TIMED-STATE-CURRENT-WHOLE24'
ROOT=run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={'TimedDbPoolMonitorTest':'65990100bc09653891f48b72ff72381cb107e5710d318318fdc6eaf1bec9dfbe','TimedJvmHeapMonitorTest':'6c654c0265ccf82895fd97e0dbabe675a712f3df890ef4eedda810d82e6384e8','TimedSyncLatencyMonitorTest':'e66960b94d962ed57ae90283d72c7b68cbda003cb4be4c18496fbe597396005d'}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14110-batch-timed-state-whole-twenty-four-pt-v1'
    run.OUT=run.host.BASE/'PG14110-batch-timed-state-whole-twenty-four-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/BatchTimedStateCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['TimedDbPoolMonitorTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory'])
        assert '"dev.codex.schubert.nk.batch.monitoring.'+name+'", 8' in run.HELPER.read_text()
    run.main()
