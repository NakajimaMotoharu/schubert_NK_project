"""Eight original whole pure policy suites/55 cases; public catalog and own bounded threads only."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'AlertLifecycleTest':12,'ContinuousConditionWindowTest':8,'MetricContractTest':6,'BatchMetricContractTest':5,'MonitoringModePolicyTest':7,'GeneratedBatchValueContractTest':7,'AlertContinuityTest':2,'MonitoringRetentionConfigurationTest':8}
SESSION='PG14928-ORIGINAL-BATCH-MONITORING-PURE55'
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={'AlertLifecycleTest':'92024d5360a1198fa8a99a31886ab09fe763761d0fc9b6cc4d697809948b7b71','ContinuousConditionWindowTest':'3ff6279428c41c81db795a689c3dea66bbe9372f4014dff0ffb7e18568ece92c','MetricContractTest':'29605f7776c85226dd130a55a06b7e9f17f6e7f8799915c7ec2ecab602c61f84','BatchMetricContractTest':'f8226e2f192c011942bab5a024bc23d3e0f9cd0210cbb177edf864543bb4bc67','MonitoringModePolicyTest':'525d72e00ac97b3510537e62426e91f25e0129f3d8812e34380f1efda4b4663c','GeneratedBatchValueContractTest':'f0b39e57c0a7cf7982ffb87442ef4bad5ea6e16faead94e17af90e7d22c036af','AlertContinuityTest':'07b790376ed5c47504e3a6be9e6fbd011c0575f827456f804b91fbbca4ec2811','MonitoringRetentionConfigurationTest':'34c225d054f02940c9b2c9f8a7e1825f5c189389e089c9b40a0298dcc49bd8ab'}
FIXTURES={'src/schubert-nk-batch/src/test/resources/monitoring/metric-catalog.tsv':'1447faabc6f056120561e4356dd75696ace4df613b6379246af29f9837fc43dc'}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14928-batch-monitoring-pure-fifty-five-pt-v1';run.OUT=data.BASE/'PG14928-batch-monitoring-pure-fifty-five-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalBatchMonitoringPureJunitLauncher.java';run.NEW_TEST=TESTS['AlertLifecycleTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='AlertLifecycleTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','Files.','Linux','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','FileStore','HttpClient','Clock.system'])
        assert '"dev.codex.schubert.nk.batch.monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    rows=next(iter(FIXTURES));data_bytes=(data.ROOT/rows).read_bytes();assert len(data_bytes.splitlines())==26 and all(len(line.split(b'\t'))==3 for line in data_bytes.splitlines())
    run.step=environmental_step;run.main()
