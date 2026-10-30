"""Original whole Batch meter contracts38, no real provider/system clock/management/Root operations."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"BatchMetricLabelPolicyTest":14,"BatchMetricRecorderTest":8,"IntegrityFailureMetricRecorderTest":8,"ProcessRestartMetricRecorderTest":8}
SESSION='PG15000-ORIGINAL-BATCH-METER38'
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={"BatchMetricLabelPolicyTest":"4f935d811be32eb92b80013f3700272cf43c24c12d6e08005e81eff19b81b5b1","BatchMetricRecorderTest":"dfdba45c2ee1ddf1106c8cab898d3fb65f7b8a9c5cd81007dc3024612ab294b1","IntegrityFailureMetricRecorderTest":"2ae67a8f4d3d949d5420cb4e3c2b2868ff305b2bb09ee4a19871305f99e2aa6c","ProcessRestartMetricRecorderTest":"0307b249231e497b0c91dd502cc64e6167b83eb019a68d9195ac72c16275f7bd"}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15000-batch-meter-contracts-thirty-eight-pt-v1';run.OUT=data.BASE/'PG15000-batch-meter-contracts-thirty-eight-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalBatchMeterContractsJunitLauncher.java';run.NEW_TEST=TESTS['BatchMetricLabelPolicyTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='BatchMetricLabelPolicyTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,ROOT/'BatchMetricContractTest.java');run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG14990-current1171-health-registry-v1/manifest.json','d3b36ed6061ad1724a6a8b5acebbfd2975ed942ebb06ef3f0aa657611b04e07d')
    assert not {'dev.codex.schubert.nk.batch.monitoring.'+name for name in COUNTS}&set(registry['suiteNames'])
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        if name=='BatchMetricRecorderTest':
            synthetic='new OutOfMemoryError("synthetic-test-only-no-allocation")';assert text.count(synthetic)==1;text=text.replace(synthetic,'')
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','Files.','FileSystems.','getFileStore(','Linux','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','HttpClient','Clock.system','OutOfMemoryError'])
        assert not re.search(r'\.\s*(?:gc|setVerbose|dumpHeap)\s*\(',text)
        assert '"dev.codex.schubert.nk.batch.monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step;run.main()
