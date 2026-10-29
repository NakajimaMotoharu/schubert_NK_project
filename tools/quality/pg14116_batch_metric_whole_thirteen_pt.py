"""Original whole metric contract5/recorder8; owned in-memory SDK registry only."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='0061d178cda80c2ce3926290619c64db125dbcfc'
COMPILE=run.host.W/'pg13832-snapshot-program-six-compile-v1'
COMPILE_SHA='8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
COUNTS={'BatchMetricContractTest':5,'BatchMetricRecorderTest':8}
SESSION='PG14116-BATCH-METRIC-CURRENT-WHOLE13'
ROOT=run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={'BatchMetricContractTest':'f8226e2f192c011942bab5a024bc23d3e0f9cd0210cbb177edf864543bb4bc67','BatchMetricRecorderTest':'dfdba45c2ee1ddf1106c8cab898d3fb65f7b8a9c5cd81007dc3024612ab294b1'}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14116-batch-metric-whole-thirteen-pt-v1'
    run.OUT=run.host.BASE/'PG14116-batch-metric-whole-thirteen-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/BatchMetricCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['BatchMetricRecorderTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory'])
        assert '"dev.codex.schubert.nk.batch.monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.main()
