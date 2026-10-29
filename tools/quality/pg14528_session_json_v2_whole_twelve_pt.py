"""Original whole session JSON/v2 twelve with synthetic literal values only; no persistence or authorization."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'SessionAttributeCodecTest':7,'SessionOperationTokenV2Test':5}
SESSION='PG14528-ORIGINAL-SESSION-JSON-V2-12'
ROOT=run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session'
TESTS={n:run.host.ROOT/p for n,p in {"SessionAttributeCodecTest":"src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/SessionAttributeCodecTest.java","SessionOperationTokenV2Test":"src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/SessionOperationTokenV2Test.java"}.items()}
PINS={'SessionAttributeCodecTest':'54c9a088ec519b70dd19ed4a6f88c2640c0fb5b410f12e16e554e2d0f9170b02','SessionOperationTokenV2Test':'4a26d6e28fd142bbe6d18e406f6921225c743d7f81b94ce10e0296f08153047d'}
FIXTURES={}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14528-session-json-v2-whole-twelve-pt-v1'
    run.OUT=run.host.BASE/'PG14528-session-json-v2-whole-twelve-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalSessionJsonV2JunitLauncher.java'
    run.NEW_TEST=TESTS['SessionAttributeCodecTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='SessionAttributeCodecTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"'+str(path.relative_to(run.host.ROOT)).split('/src/test/java/',1)[1][:-5].replace('/','.')+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step
    run.main()
