"""Original borrowed typed JDBC observation Source20; proxies only, owned Attempt overload untested/HOLD."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"ApiOutboxObservationSourceTest":20}
SESSION='PG15204-ORIGINAL-API-OUTBOX-SOURCE20'
ROOT=data.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={"ApiOutboxObservationSourceTest":"7bf403ccc605f19ed94c5aef2db9f77977c260af748a1da34d14cc4fa1794f7f"}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15204-api-outbox-source-twenty-pt-v1';run.OUT=data.BASE/'PG15204-api-outbox-source-twenty-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalApiOutboxSourceJunitLauncher.java';run.NEW_TEST=TESTS['ApiOutboxObservationSourceTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='ApiOutboxObservationSourceTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,ROOT/'DbPoolMetricObservationTest.java',ROOT/'OutboxObservationRepositoryTest.java');run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG15194-current1677-web-metric-http-registry-v1/manifest.json','9debc9d9d3e3695ecc216e5315c2046e885b15d856e9017ad5ce9e882192e129')
    assert not {'dev.codex.schubert.nk.api.monitoring.'+name for name in COUNTS}&set(registry['suiteNames'])
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','Files.','FileSystems.','getFileStore(','Linux','getenv(','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','HttpClient','Clock.system','OutOfMemoryError'])
        assert not re.search(r'\.\s*(?:gc|setVerbose|dumpHeap)\s*\(',text)
        assert '"dev.codex.schubert.nk.api.monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step;run.main()
