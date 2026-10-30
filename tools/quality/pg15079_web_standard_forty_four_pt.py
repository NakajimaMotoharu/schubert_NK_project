"""Original Web GC/JVM/System whole44; own child SDK only, no external actions."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"WebGcMetricRegistrationTest":16,"WebJvmMetricsTest":14,"WebSystemMetricsTest":14}
SESSION='PG15079-ORIGINAL-WEB-STANDARD44'
ROOT=data.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={"WebGcMetricRegistrationTest":"eef28181ac6bfa92a1947291ff28de45dfb46a70a164afad7d9ea0574750c732","WebJvmMetricsTest":"17ef23f2aba67dcec1fa659edb851f61f3317aedca7bee367868fc92ea2c258d","WebSystemMetricsTest":"c468da61ae6a63ada1435ce49fa04160f06f5aaaca99dfcc5f8aefd4e1176211"}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15079-web-standard-forty-four-pt-v1';run.OUT=data.BASE/'PG15079-web-standard-forty-four-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalWebStandard44JunitLauncher.java';run.NEW_TEST=TESTS['WebGcMetricRegistrationTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='WebGcMetricRegistrationTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG15068-current1423-web-pool-registry-v1/manifest.json','ca9843224a63a80910ecaffa5fc47ce92b8bf52a0f034fad490421d72edd4a99')
    assert not {'dev.codex.schubert.nk.web.monitoring.'+name for name in COUNTS}&set(registry['suiteNames'])
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','Files.','FileSystems.','getFileStore(','Linux','getenv(','import java.sql','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','HttpClient','Clock.system','OutOfMemoryError'])
        assert not re.search(r'\.\s*(?:gc|setVerbose|dumpHeap)\s*\(',text)
        assert '"dev.codex.schubert.nk.web.monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step;run.main()
