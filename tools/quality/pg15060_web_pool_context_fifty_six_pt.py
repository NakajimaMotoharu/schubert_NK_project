"""Original whole Web pool/context56, fake getter interfaces and owned SDK lifecycle only, no realDB or external actions."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"WebDbPoolMetricRecorderTest":8,"WebDbPoolMetricBindingTest":15,"WebMetricContextTest":33}
SESSION='PG15060-ORIGINAL-WEB-POOL-CONTEXT56'
ROOT=data.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={"WebDbPoolMetricRecorderTest":"de0eaa8e849ae7ade1a4ceab7a554e32fe3ec169e097c457fef5c74191da1e8b","WebDbPoolMetricBindingTest":"08c7e9360f37ae80c349c72b1171dc362eba8ec692e76cfed84fbb7eeccdecbf","WebMetricContextTest":"5611b2a69cd9728890bddc6712d71f851c8d967c72dbaa45ff12e089f75dd545"}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15060-web-pool-context-fifty-six-pt-v1';run.OUT=data.BASE/'PG15060-web-pool-context-fifty-six-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalWebPoolContextJunitLauncher.java';run.NEW_TEST=TESTS['WebDbPoolMetricRecorderTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='WebDbPoolMetricRecorderTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,ROOT/'WebDbPoolMetricObservationTest.java');run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG15050-current1367-web-exporter-registry-v1/manifest.json','6524ae373d11f4eb8cb691deaff85aee31dc7a64b1839a59ae69bb79a923b0f6')
    assert not {'dev.codex.schubert.nk.web.monitoring.'+name for name in COUNTS}&set(registry['suiteNames'])
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','Files.','FileSystems.','getFileStore(','Linux','getenv(','import java.sql','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','HttpClient','Clock.system','OutOfMemoryError'])
        assert not re.search(r'\.\s*(?:gc|setVerbose|dumpHeap)\s*\(',text)
        assert '"dev.codex.schubert.nk.web.monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step;run.main()
