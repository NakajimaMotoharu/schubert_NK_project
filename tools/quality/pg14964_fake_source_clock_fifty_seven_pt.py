"""Original whole fake-source pipeline57, no real provider/system clock/management/Root operations."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'MonitoringPolicyEngineTest':9,'MonitoringStatusTextTest':6,'MonitoringPollerTest':8,'MonitoringObservationClockTest':8,'FilesystemHealthObservationTest':10,'JvmHeapHealthObservationTest':9,'MonitoringMissingObservationTest':3,'AlertRegistryTest':4}
SESSION='PG14964-ORIGINAL-FAKE-SOURCE-CLOCK57'
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={'MonitoringPolicyEngineTest':'64b3ee74b7b5f66464594169332d5806ec7f77436c2797fe76607bcc7d6562d9','MonitoringStatusTextTest':'4b083f731a9c47f9d860fc4887ddfde17cd8bb842864d20efd0bca5c8df3f34c','MonitoringPollerTest':'8172e31aad995283e0a443399a5e75f419d22a5b69e0f8579161aaddd3b7ca01','MonitoringObservationClockTest':'4612f486d88e111f2927330c0d227b00395d60e51993351896ab510cf6496e9d','FilesystemHealthObservationTest':'a1925aaa21a6bfe9db25d6dc8c83156f190ac980d1af0c2dadca624929f81dca','JvmHeapHealthObservationTest':'9a160707461f978bc9cb972aa8fb9b886b5b02264614b98819c1d4f0673bd69e','MonitoringMissingObservationTest':'64bfbd2e4fd2f43d20097e81070629d6af8993323aeb88511f639ef2840ae677','AlertRegistryTest':'cda14d500331e2ca2b92e6308fb325c65c8bd9ea81da012cecc709533fcd66d8'}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14964-fake-source-clock-fifty-seven-pt-v1';run.OUT=data.BASE/'PG14964-fake-source-clock-fifty-seven-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalFakeSourceClockJunitLauncher.java';run.NEW_TEST=TESTS['MonitoringPolicyEngineTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='MonitoringPolicyEngineTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG14954-current1033-timed-registry-v1/manifest.json','b8b3d535d29704fd2290b0a74702121733d04f3d1f9cf74b6a5b4adfaef7483b')
    assert not {'dev.codex.schubert.nk.batch.monitoring.'+name for name in COUNTS}&set(registry['suiteNames'])
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        if name=='JvmHeapHealthObservationTest':
            synthetic='new OutOfMemoryError("synthetic-test-only-no-allocation")';assert text.count(synthetic)==1;text=text.replace(synthetic,'')
            assert 'Proxy.newProxyInstance(' in text and 'method.getName().equals("getHeapMemoryUsage")' in text
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','Files.','FileSystems.','getFileStore(','Linux','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','HttpClient','Clock.system','OutOfMemoryError'])
        assert not re.search(r'\.\s*(?:gc|setVerbose|dumpHeap)\s*\(',text)
        assert '"dev.codex.schubert.nk.batch.monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step;run.main()
