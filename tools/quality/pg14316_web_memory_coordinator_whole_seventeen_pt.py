"""Original memory coordinator8/registry5/terminal4 whole suites; no JMS connection or held graph execution."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'JmsRequestReplyClientTest':8,'ReplyCorrelationRegistryTest':5,'ReplyCorrelationTerminalRaceTest':4}
SESSION='PG14316-ORIGINAL-WEB-MEMORY-COORDINATOR17'
ROOT=run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={'JmsRequestReplyClientTest':'3a115c2a3508f914b58a9b4702ae718abd6234b185a6df1996d32bec98da9c3d','ReplyCorrelationRegistryTest':'2b35e3a19dd33b72ba123a7e2f5d098499e9257b1dd90e080139b81e7a160461','ReplyCorrelationTerminalRaceTest':'ded026184e89c0427125c85b513742d4c3863e769d5bbb818ee474788a86b1d1'}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14316-web-memory-coordinator-whole-seventeen-pt-v1'
    run.OUT=run.host.BASE/'PG14316-web-memory-coordinator-whole-seventeen-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalWebMemoryCoordinatorJunitLauncher.java'
    run.NEW_TEST=TESTS['JmsRequestReplyClientTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"dev.codex.schubert.nk.web.messaging.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step
    run.main()
