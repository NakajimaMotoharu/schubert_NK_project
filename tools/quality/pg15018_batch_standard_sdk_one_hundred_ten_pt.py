"""Original whole Batch standard SDK110 on own child JVM; no target, forced GC, service or Root operations."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"BatchMetricTextTest":37,"BatchStandardMetricSourceTest":16,"BatchJvmMetricsTest":14,"BatchSystemMetricsTest":14,"BatchGcMetricRegistrationTest":16,"BatchStandardMetricsTest":13}
SESSION='PG15018-ORIGINAL-BATCH-STANDARD110'
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={"BatchMetricTextTest":"807f6a61dc2e350348bf0f4d8f0200375756cc1e59671c8fcb87799c0111739e","BatchStandardMetricSourceTest":"4b9330ecc92623e0a076424ae23ac6b6290a0d2a39b4e9c7aa91e8ff800b0326","BatchJvmMetricsTest":"35d80a7aeec82cd14328b687fc9310417d716868215c332a7d6e90456df29f11","BatchSystemMetricsTest":"5f8ac6fd1110c61069702fba98985c37b4a4676fa0c096617a393e6ebd8bf000","BatchGcMetricRegistrationTest":"fa6654fc3a8a6a2da39fe23f0c92e0067f0e06af025bc561d9a6ecd8c4b6108c","BatchStandardMetricsTest":"4ba0ab0918cf1ea8d14fe5fb3daec5be31b49decaa74a3f77ae78764ddf1ebad"}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15018-batch-standard-sdk-one-hundred-ten-pt-v1';run.OUT=data.BASE/'PG15018-batch-standard-sdk-one-hundred-ten-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalBatchStandardSdkJunitLauncher.java';run.NEW_TEST=TESTS['BatchMetricTextTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='BatchMetricTextTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG15008-current1209-batch-meter-registry-v1/manifest.json','7ada341961c699e1b65222ed52e2e3a345f3a71971d33febcf3dd344400d9de2')
    assert not {'dev.codex.schubert.nk.batch.monitoring.'+name for name in COUNTS}&set(registry['suiteNames'])
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','Files.','FileSystems.','getFileStore(','Linux','getenv(','import java.sql','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','HttpClient','Clock.system','OutOfMemoryError'])
        assert not re.search(r'\.\s*(?:gc|setVerbose|dumpHeap)\s*\(',text)
        assert '"dev.codex.schubert.nk.batch.monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step;run.main()
