"""Four whole MQ/media32 suites; own Function/SDK/finite threads only, no actual broker/media/HTTP."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"MqPressureMetricCollectorTest":8,"MqPressureMetricRecorderTest":8,"MediaStreamsMetricCollectorTest":8,"MediaStreamsMetricRecorderTest":8}
SESSION='PG14384-ORIGINAL-MQ-MEDIA32'
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
TESTS={n:run.host.ROOT/p for n,p in {"MqPressureMetricCollectorTest":"src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/MqPressureMetricCollectorTest.java","MqPressureMetricRecorderTest":"src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/MqPressureMetricRecorderTest.java","MediaStreamsMetricCollectorTest":"src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/MediaStreamsMetricCollectorTest.java","MediaStreamsMetricRecorderTest":"src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/MediaStreamsMetricRecorderTest.java"}.items()}
PINS={"MqPressureMetricCollectorTest":"e427125e32b6b65234d2999587fd989f5a385fcb04c46be0948b0d01fd46ea5a","MqPressureMetricRecorderTest":"57603987ebe17531c44477797de3f021179ec27ccf9428ded76256fd571e8f99","MediaStreamsMetricCollectorTest":"a23aaa99c1586824701ebbb7335168a4d6d07a3edfbdde2fb1ec3bae53d5e93a","MediaStreamsMetricRecorderTest":"854f47b9789652a6fecd20071010c46a07ef8674423094294d85f615ddec428e"}
FIXTURES={}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14384-mq-media-whole-thirty-two-pt-v1'
    run.OUT=run.host.BASE/'PG14384-mq-media-whole-thirty-two-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalMqMediaObservationJunitLauncher.java'
    run.NEW_TEST=TESTS['MqPressureMetricCollectorTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='MqPressureMetricCollectorTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"dev.codex.schubert.nk.'+('api.' if name.startswith('Mq') else 'web.')+'monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step
    run.main()
