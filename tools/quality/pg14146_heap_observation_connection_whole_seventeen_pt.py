"""Original whole9/8 heap observation and connection, fixed getter-only proxy, no actual management."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='0061d178cda80c2ce3926290619c64db125dbcfc'
COMPILE=run.host.W/'pg13832-snapshot-program-six-compile-v1'
COMPILE_SHA='8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
COUNTS={'JvmHeapHealthObservationTest':9,'JvmHeapHealthMonitorTest':8}
SESSION='PG14146-HEAP-OBSERVATION-CONNECTION-CURRENT-WHOLE17'
ROOT=run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={'JvmHeapHealthObservationTest':'9a160707461f978bc9cb972aa8fb9b886b5b02264614b98819c1d4f0673bd69e','JvmHeapHealthMonitorTest':'25cdfa418c2332c29ead8b3f3f60f084ff0ad5d7a8aec0042c715c1d3b8730ce'}
HELPER_PINS={'MonitoringObservationClockTest':'4612f486d88e111f2927330c0d227b00395d60e51993351896ab510cf6496e9d','FilesystemHealthObservationTest':'a1925aaa21a6bfe9db25d6dc8c83156f190ac980d1af0c2dadca624929f81dca'}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14146-heap-observation-connection-whole-seventeen-pt-v1'
    run.OUT=run.host.BASE/'PG14146-heap-observation-connection-whole-seventeen-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/HeapObservationCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['JvmHeapHealthObservationTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/(name+'.java') for name in HELPER_PINS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,h in HELPER_PINS.items():
        assert run.host.sha(ROOT/(name+'.java'))==h
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory'])
        assert '"dev.codex.schubert.nk.batch.monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.main()
