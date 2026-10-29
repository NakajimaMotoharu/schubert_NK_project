"""Three original Web Outbox26 suites, own JDBC proxy/SDK/threads only, no actual DB/clock."""
import re
from reviewed_jdbc_fixture_scope_v2 import eligible
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"WebOutboxMetricCollectorTest":8,"WebOutboxMetricRecorderTest":8,"WebOutboxObservationRepositoryTest":10}
SESSION='PG14416-ORIGINAL-WEB-OUTBOX-SUPPLIED26'
ROOT=run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring'
TESTS={n:run.host.ROOT/p for n,p in {"WebOutboxMetricCollectorTest":"src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebOutboxMetricCollectorTest.java","WebOutboxMetricRecorderTest":"src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebOutboxMetricRecorderTest.java","WebOutboxObservationRepositoryTest":"src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebOutboxObservationRepositoryTest.java"}.items()}
PINS={"WebOutboxMetricCollectorTest":"4c4596c912ef7772249b63e75becd7b396deb6defce9599bfb829e6e711240d5","WebOutboxMetricRecorderTest":"ff7e8faa0bc057eaa1a691b0ee855b7c37b65463d458a573667e3896e1a41b32","WebOutboxObservationRepositoryTest":"175d1c5385409c114cc2e8cf4d80f7028acf2c5bac6918e6293191a7d2f88078"}
REQUIRED={"WebOutboxObservationRepositoryTest":["Proxy.newProxyInstance(","Connection.class","PreparedStatement.class","ResultSet.class","borrowed connection must not be mutated or closed","FROM schubert_web_session.web_log_outbox GROUP BY status"],"WebOutboxMetricCollectorTest":["class WebOutboxMetricCollectorTest","new WebOutboxObservationRepository()","Thread.State.BLOCKED"],"WebOutboxMetricRecorderTest":["class WebOutboxMetricRecorderTest","SimpleMeterRegistry","90715647"]}
FIXTURES={}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14416-web-outbox-supplied-whole-twenty-six-pt-v1'
    run.OUT=run.host.BASE/'PG14416-web-outbox-supplied-whole-twenty-six-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalWebOutboxSuppliedMetricJunitLauncher.java'
    run.NEW_TEST=TESTS['WebOutboxMetricCollectorTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='WebOutboxMetricCollectorTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"dev.codex.schubert.nk.'+'web.'+'monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    fixture_texts={n:p.read_text() for n,p in TESTS.items()}
    jdbc_proof=data.read_checked(data.BASE/'PG14417-web-outbox-jdbc-profile-v1/manifest.json','5994ad9f1211e5b51894d1bc596a2b4aaba7b54430e1a95ffb673447e245ef74')
    assert jdbc_proof['actualExit']==jdbc_proof['productTestsExecuted']==0 and jdbc_proof['negativeVectors']==61 and jdbc_proof['positive']==1
    assert jdbc_proof['helperSha256']==run.host.sha(run.host.ROOT/'tools/quality/reviewed_jdbc_fixture_scope_v2.py')
    assert jdbc_proof['testHashes']=={n:dict(path=str(p.relative_to(run.host.ROOT)),sha256=PINS[n]) for n,p in TESTS.items()}
    assert jdbc_proof['required']==REQUIRED
    assert eligible(fixture_texts,REQUIRED) is True
    run.step=environmental_step
    run.main()
