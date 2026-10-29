"""Existing original finite-proxy five only; no listener broker or held graph substitute."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'InboundTransactionsPrimaryContractTest':5}
SESSION='PG14252-ORIGINAL-INBOUND-PRIMARY-FIVE'
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/inbound'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={'InboundTransactionsPrimaryContractTest':'86c393968624410459270b52718aeefb37093b75db6e6ad2f5d891d506c582aa'}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14252-inbound-primary-whole-five-pt-v1'
    run.OUT=run.host.BASE/'PG14252-inbound-primary-whole-five-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalInboundPrimaryJunitLauncher.java'
    run.NEW_TEST=TESTS['InboundTransactionsPrimaryContractTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"dev.codex.schubert.nk.api.messaging.inbound.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.main()
