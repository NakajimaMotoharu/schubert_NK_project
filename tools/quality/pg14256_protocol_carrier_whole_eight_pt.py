"""Eight existing original scalar carrier cases only; never held graph9 or listener broker."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'FailedJmsIsolationExceptionTest':4,'UnconfirmedJmsRollbackExceptionTest':4}
SESSION='PG14256-ORIGINAL-PROTOCOL-CARRIERS-EIGHT'
ROOT=run.host.ROOT/'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/transport'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={'FailedJmsIsolationExceptionTest':'4b38735c88ffee065f3499688a29df85d1d3e97a51401d9f9ce0805f75e41cca','UnconfirmedJmsRollbackExceptionTest':'189a8e5fc185e9cf70c22a72ff25be675ab284e5dc62bfd7920988456829bda9'}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14256-protocol-carrier-whole-eight-pt-v1'
    run.OUT=run.host.BASE/'PG14256-protocol-carrier-whole-eight-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalProtocolCarrierJunitLauncher.java'
    run.NEW_TEST=TESTS['FailedJmsIsolationExceptionTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"dev.codex.schubert.nk.protocol.transport.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.main()
