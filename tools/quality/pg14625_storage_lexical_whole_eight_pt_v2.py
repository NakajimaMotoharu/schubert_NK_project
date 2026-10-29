"""Entire original lexical location/layout/exception8: synthetic Map/Path values and finite own threads, no IO."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"ServiceCredentialLocationTest":5,"StorageRootLayoutTest":2,"ExceptionValueContractTest":1}
SESSION='PG14625-ORIGINAL-STORAGE-LEXICAL8'
ROOT=run.host.ROOT/'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={"ServiceCredentialLocationTest":"142442145de98b7c09bf0fc47db0aa9b8861b1613a14efa300d63c17179207bb","StorageRootLayoutTest":"bd23afae98cccd71ae899630db2d623a8c5546207187c44cab5a1cff311e6745","ExceptionValueContractTest":"8ac03445ece99fffd8b515073a5c1fcfbefaec4d3b3191b6307f220116cd8f86"}
FIXTURES={}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'


def exact_test_path(name,path):
    expected=run.host.ROOT/('src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/'+name+'.java')
    return name in COUNTS and path==expected and '..' not in path.parts

def path_prevention():
    name='ServiceCredentialLocationTest';path=TESTS[name]
    assert exact_test_path(name,path)
    wrong=[
        run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/storage/ServiceCredentialLocationTest.java',
        ROOT/'foreign/ServiceCredentialLocationTest.java',
        ROOT/'ServiceCredentialIdTest.java',
        ROOT/'nested/../ServiceCredentialLocationTest.java']
    assert all(not exact_test_path(name,p) for p in wrong)
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    for n,p in TESTS.items():
        relative=str(p.relative_to(run.host.ROOT))
        assert exact_test_path(n,p) and run.host.sha(p)==run.host.sha(COMPILE/'snapshot'/relative)==normal['begin']['inputHashes'][relative]==PINS[n]
    return len(wrong)

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14625-storage-lexical-whole-eight-pt-v2'
    run.OUT=run.host.BASE/'PG14625-storage-lexical-whole-eight-pt-v2'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalStorageLexicalJunitLauncher.java'
    run.NEW_TEST=TESTS['ServiceCredentialLocationTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='ServiceCredentialLocationTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"'+str(path.relative_to(run.host.ROOT)).split('/src/test/java/',1)[1][:-5].replace('/','.')+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    assert path_prevention()==4
    run.step=environmental_step
    run.main()
