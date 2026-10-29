"""Entire original User core4/response4 and Log plain8; no backend receiver, DB or crypto."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"UserQueryCanonicalCoreTest":4,"UserQueryResponseBoundaryTest":4,"LogPlainContractTest":8}
SESSION='PG14630-ORIGINAL-API-PLAIN16'
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application'
TEST_PATHS={"UserQueryCanonicalCoreTest":"src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/UserQueryCanonicalCoreTest.java","UserQueryResponseBoundaryTest":"src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/UserQueryResponseBoundaryTest.java","LogPlainContractTest":"src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/log/LogPlainContractTest.java"}
TESTS={n:run.host.ROOT/p for n,p in TEST_PATHS.items()}
PINS={"UserQueryCanonicalCoreTest":"bff3bdd906735fc3b2b49d52f7a00ac7f1dad8a2ae515535eee09cb2660b42a1","UserQueryResponseBoundaryTest":"72a9ccd0477fd81896d59d24224f14fb9e261ca9ad6a23a1d8e992ae8e93a1a1","LogPlainContractTest":"e573d36edd918941ebf66c6070401f74b382e022eff0b5108f716192fd0d9a94"}
FIXTURES={}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

def preflight():
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    for name,path in TESTS.items():
        relative=TEST_PATHS[name]
        assert path.parent.parent==ROOT and path.stem==name and path.parent.name in {'admin','log'} and '..' not in path.parts
        assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text()
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','@AfterAll','@TempDir','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Mac.','Cipher.'])
        fq=relative.split('/src/test/java/',1)[1][:-5].replace('/','.')
        assert '"'+fq+'", '+str(COUNTS[name]) in run.HELPER.read_text()

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14630-api-plain-whole-sixteen-pt-v1'
    run.OUT=run.host.BASE/'PG14630-api-plain-whole-sixteen-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalApiPlainJunitLauncher.java'
    run.NEW_TEST=TESTS['UserQueryCanonicalCoreTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='UserQueryCanonicalCoreTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    preflight();run.step=environmental_step;run.main()
