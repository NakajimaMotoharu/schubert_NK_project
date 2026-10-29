"""Three original Async metric24 suites, own JDBC proxy/SDK/threads only, no actual DB/worker."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"AsyncJobMetricCollectorTest":8,"AsyncJobMetricRecorderTest":8,"AsyncJobCountRepositoryTest":8}
SESSION='PG14396-ORIGINAL-ASYNC-SUPPLIED-METRIC24'
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
TESTS={n:run.host.ROOT/p for n,p in {"AsyncJobMetricCollectorTest":"src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/AsyncJobMetricCollectorTest.java","AsyncJobMetricRecorderTest":"src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/AsyncJobMetricRecorderTest.java","AsyncJobCountRepositoryTest":"src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/AsyncJobCountRepositoryTest.java"}.items()}
PINS={"AsyncJobMetricCollectorTest":"e91c368880999ba74d2157210ecaa3c80f4388ee80a4d94f1862a0efc1c973ed","AsyncJobMetricRecorderTest":"714b91b3dd34aed6cc3379bf02d161f6f12f0216bffbb9859822efb4ee5aa3d6","AsyncJobCountRepositoryTest":"3f6c16ee0a85788b96746a87d870d2874d4ee753e639abb89796f0fcba632042"}
FIXTURES={}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14396-async-supplied-metric-whole-twenty-four-pt-v1'
    run.OUT=run.host.BASE/'PG14396-async-supplied-metric-whole-twenty-four-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalAsyncSuppliedMetricJunitLauncher.java'
    run.NEW_TEST=TESTS['AsyncJobMetricCollectorTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='AsyncJobMetricCollectorTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"dev.codex.schubert.nk.'+'api.'+'monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step
    run.main()
