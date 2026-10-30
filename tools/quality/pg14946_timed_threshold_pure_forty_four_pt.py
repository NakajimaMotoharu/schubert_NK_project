"""Five original whole pure supplied-value suites/44 cases, own threads and no actual observations."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'TimedFilesystemMonitorTest':6,'TimedJvmHeapMonitorTest':8,'TimedDbPoolMonitorTest':8,'TimedSyncLatencyMonitorTest':8,'AlertThresholdsTest':14}
SESSION='PG14946-ORIGINAL-TIMED-THRESHOLD-PURE44'
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={'TimedFilesystemMonitorTest':'eaf75929cad6da6e663b4cac164f48c435bba6014d198d7c6d2b40eae6f04387','TimedJvmHeapMonitorTest':'6c654c0265ccf82895fd97e0dbabe675a712f3df890ef4eedda810d82e6384e8','TimedDbPoolMonitorTest':'65990100bc09653891f48b72ff72381cb107e5710d318318fdc6eaf1bec9dfbe','TimedSyncLatencyMonitorTest':'e66960b94d962ed57ae90283d72c7b68cbda003cb4be4c18496fbe597396005d','AlertThresholdsTest':'1eb5325c675acfaf86c7d02c6b1815943c0d35dee68fd6ef0a65f48a7c067c27'}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14946-timed-threshold-pure-forty-four-pt-v1';run.OUT=data.BASE/'PG14946-timed-threshold-pure-forty-four-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalTimedThresholdJunitLauncher.java';run.NEW_TEST=TESTS['TimedFilesystemMonitorTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='TimedFilesystemMonitorTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG14936-current989-monitoring-registry-v1/manifest.json','7a9b71bd5c381cd56b2adf0cf741911289da53194f8ad11213ab0661a46ec093')
    assert not {'dev.codex.schubert.nk.batch.monitoring.'+name for name in COUNTS}&set(registry['suiteNames'])
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','Files.','Linux','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','FileStore','HttpClient','Clock.system','OutOfMemoryError'])
        assert '"dev.codex.schubert.nk.batch.monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step;run.main()
