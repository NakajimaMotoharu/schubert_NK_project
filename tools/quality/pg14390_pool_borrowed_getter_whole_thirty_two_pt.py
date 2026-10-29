"""Four original pool borrowed-getter32 suites, own interfaces/SDK/finite threads, no actual pool/DB/JMX."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"DbPoolMetricCollectorTest":8,"DbPoolMetricObservationTest":8,"WebDbPoolMetricCollectorTest":8,"WebDbPoolMetricObservationTest":8}
SESSION='PG14390-ORIGINAL-POOL-BORROWED-GETTER32'
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
TESTS={n:run.host.ROOT/p for n,p in {"DbPoolMetricCollectorTest":"src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/DbPoolMetricCollectorTest.java","DbPoolMetricObservationTest":"src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/DbPoolMetricObservationTest.java","WebDbPoolMetricCollectorTest":"src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebDbPoolMetricCollectorTest.java","WebDbPoolMetricObservationTest":"src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebDbPoolMetricObservationTest.java"}.items()}
PINS={"DbPoolMetricCollectorTest":"440f20404376afcb7a29fef1f2bac01ac7ffea23d203e14c537cb685e9afdacd","DbPoolMetricObservationTest":"13a68e4303e1870494f463ba6ef89e32d8807082594ccc11709f497668d5e14f","WebDbPoolMetricCollectorTest":"bd3ce9b76065aa929036b629f5b1d9d1aec4ba0c773e965809dd398ff97b25f4","WebDbPoolMetricObservationTest":"a23735273bf31a1c8b7c68737355364b19bc5d20e18ab3c422448de4016ed98b"}
FIXTURES={}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14390-pool-borrowed-getter-whole-thirty-two-pt-v1'
    run.OUT=run.host.BASE/'PG14390-pool-borrowed-getter-whole-thirty-two-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalPoolGetterJunitLauncher.java'
    run.NEW_TEST=TESTS['DbPoolMetricCollectorTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='DbPoolMetricCollectorTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"dev.codex.schubert.nk.'+('web.' if name.startswith('Web') else 'api.')+'monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step
    run.main()
