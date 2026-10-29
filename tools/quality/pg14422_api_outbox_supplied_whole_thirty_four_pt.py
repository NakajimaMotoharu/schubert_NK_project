"""Four original API Outbox34 suites, own JDBC proxy/SDK/threads only, no actual DB/clock."""
import re
from reviewed_jdbc_fixture_scope_v2 import eligible
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'OutboxMetricCollectorTest': 8, 'OutboxObservationRepositoryTest': 10, 'OutboxRowsMetricRecorderTest': 8, 'OutboxAgeMetricRecorderTest': 8}
SESSION='PG14422-ORIGINAL-API-OUTBOX-SUPPLIED34'
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
TESTS={n:run.host.ROOT/p for n,p in {'OutboxMetricCollectorTest': 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OutboxMetricCollectorTest.java', 'OutboxObservationRepositoryTest': 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OutboxObservationRepositoryTest.java', 'OutboxRowsMetricRecorderTest': 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OutboxRowsMetricRecorderTest.java', 'OutboxAgeMetricRecorderTest': 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OutboxAgeMetricRecorderTest.java'}.items()}
PINS={'OutboxMetricCollectorTest': '2c7b20b6944018b912d5f6ad0419e069b93c4a1d704d3958609043464f9d0bb4', 'OutboxObservationRepositoryTest': '60de5831df6c273130930756bef2d5551c265d17eda8e2b7d80a0eb27bd2b9e8', 'OutboxRowsMetricRecorderTest': '193ecfb3b0fd738452560f52fbe0a069aa097162fc75b74d53dfc804d160eb36', 'OutboxAgeMetricRecorderTest': 'f782006859ef273e9cb498a97ec8c20fc050de47c0ab1e53ca46d9ea8f9de2cf'}
REQUIRED={'OutboxMetricCollectorTest': ['class OutboxMetricCollectorTest', 'new OutboxObservationRepository()'], 'OutboxObservationRepositoryTest': ['Proxy.newProxyInstance(', 'Connection.class', 'PreparedStatement.class', 'ResultSet.class', 'borrowed connection must not be mutated or closed', 'FROM schubert.mq_outbox GROUP BY status'], 'OutboxRowsMetricRecorderTest': ['class OutboxRowsMetricRecorderTest', 'SimpleMeterRegistry'], 'OutboxAgeMetricRecorderTest': ['class OutboxAgeMetricRecorderTest', 'SimpleMeterRegistry', '3045']}
FIXTURES={}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14422-api-outbox-supplied-whole-thirty-four-pt-v1'
    run.OUT=run.host.BASE/'PG14422-api-outbox-supplied-whole-thirty-four-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalApiOutboxSuppliedMetricJunitLauncher.java'
    run.NEW_TEST=TESTS['OutboxMetricCollectorTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='OutboxMetricCollectorTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"dev.codex.schubert.nk.'+'api.'+'monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    fixture_texts={n:p.read_text() for n,p in TESTS.items()}
    jdbc_proof=data.read_checked(data.BASE/'PG14421-api-outbox-jdbc-profile-v1/manifest.json','2f529006365c1c7f63ccce26007f79955e0e69ba9dc5ab6b5e7b22e72f63e2e2')
    assert jdbc_proof['actualExit']==jdbc_proof['productTestsExecuted']==0 and jdbc_proof['negativeVectors']==77 and jdbc_proof['positive']==1
    assert jdbc_proof['helperSha256']==run.host.sha(run.host.ROOT/'tools/quality/reviewed_jdbc_fixture_scope_v2.py')
    assert jdbc_proof['testHashes']=={n:dict(path=str(p.relative_to(run.host.ROOT)),sha256=PINS[n]) for n,p in TESTS.items()}
    assert jdbc_proof['required']==REQUIRED
    assert eligible(fixture_texts,REQUIRED) is True
    run.step=environmental_step
    run.main()
