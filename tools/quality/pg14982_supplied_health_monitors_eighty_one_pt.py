"""Original whole supplied-health monitors81, no real provider/system clock/management/Root operations."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"AsyncQueueMonitorTest":9,"BackupHealthMonitorTest":8,"DlqHealthMonitorTest":8,"ExpiryBacklogMonitorTest":8,"IntegrityHealthMonitorTest":8,"JvmHeapHealthMonitorTest":8,"RestartHealthMonitorTest":8,"TransferHealthMonitorTest":8,"WebLogBacklogMonitorTest":8,"TransferMetricRecorderTest":8}
SESSION='PG14982-ORIGINAL-SUPPLIED-HEALTH81'
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={"AsyncQueueMonitorTest":"7128ed500fce38c80558829fe62e7f7bf5309e9f5f933642b6f252c9796e8407","BackupHealthMonitorTest":"fa96ad8b693632dcf0040e5f0676d596f913822197ea22afaf85289251e09c33","DlqHealthMonitorTest":"b7b530c0a01f5229cc69d534d8bb824a417eaf1f25fbddb5017ef9dc96c81b75","ExpiryBacklogMonitorTest":"38761025731fef2a215b5f5d87db3bcfb51e2ed0b12f7faf421dc5218ce097a5","IntegrityHealthMonitorTest":"6c300a98e70cf25296285e8b3685a530725d43f8be3afb9aacd6f4789ec40154","JvmHeapHealthMonitorTest":"25cdfa418c2332c29ead8b3f3f60f084ff0ad5d7a8aec0042c715c1d3b8730ce","RestartHealthMonitorTest":"622d59e35f7798b155136d96a06d45c61561f6149df9e5bb2c2d724cc1e9e2fa","TransferHealthMonitorTest":"d4f6fee797ad71fc762dc23c3d58575fd9f5eb4767ae4410836189ac2e5d9d9e","WebLogBacklogMonitorTest":"ba5578f1227f7349a0dc2cc6feba66e9c05d786acd6046329570e556050ffb26","TransferMetricRecorderTest":"9775f5889a8cc51f5de943c227e8f6dabb255f7f1a6a380d1fd12a0861d1e58e"}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14982-supplied-health-monitors-eighty-one-pt-v1';run.OUT=data.BASE/'PG14982-supplied-health-monitors-eighty-one-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalSuppliedHealthJunitLauncher.java';run.NEW_TEST=TESTS['AsyncQueueMonitorTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='AsyncQueueMonitorTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,ROOT/'JvmHeapHealthObservationTest.java',ROOT/'MonitoringObservationClockTest.java',ROOT/'FilesystemHealthObservationTest.java');run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG14972-current1090-fake-source-registry-v1/manifest.json','6351ecee87a03d9c3442af3794e35f42615d19420c23f884ed62f123f0daacc6')
    assert not {'dev.codex.schubert.nk.batch.monitoring.'+name for name in COUNTS}&set(registry['suiteNames'])
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        if name=='JvmHeapHealthMonitorTest':
            synthetic='new OutOfMemoryError("synthetic-test-only-no-allocation")';assert text.count(synthetic)==1;text=text.replace(synthetic,'')
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','Files.','FileSystems.','getFileStore(','Linux','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','HttpClient','Clock.system','OutOfMemoryError'])
        assert not re.search(r'\.\s*(?:gc|setVerbose|dumpHeap)\s*\(',text)
        assert '"dev.codex.schubert.nk.batch.monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step;run.main()
