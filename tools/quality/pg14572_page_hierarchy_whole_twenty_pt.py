"""Entire original Page and Scenario hierarchy view-model20, in-memory StringTemplate/DOM and own finite threads only."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"PageViewModelTest":8,"ScenarioHierarchyViewModelTest":12}
SESSION='PG14572-ORIGINAL-PAGE-HIERARCHY20'
ROOT=run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view'
TESTS={n:run.host.ROOT/p for n,p in {"PageViewModelTest":"src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/PageViewModelTest.java","ScenarioHierarchyViewModelTest":"src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/ScenarioHierarchyViewModelTest.java"}.items()}
PINS={"PageViewModelTest":"e9d36a9203d325fa80592387334c95d526874ae4ceca62b0b910b3d945082f0e","ScenarioHierarchyViewModelTest":"682eca930953d9ec5baaa196f4b4a79bc35c9ea1cdee419c1fed7c025ea3fdc5"}
FIXTURES={}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14572-page-hierarchy-whole-twenty-pt-v1'
    run.OUT=run.host.BASE/'PG14572-page-hierarchy-whole-twenty-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalPageHierarchyJunitLauncher.java'
    run.NEW_TEST=TESTS['PageViewModelTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='PageViewModelTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+(?:@DisplayName\("[^"\n]*"\)\s+)?void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"'+str(path.relative_to(run.host.ROOT)).split('/src/test/java/',1)[1][:-5].replace('/','.')+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    previous=data.read_checked(data.BASE/'PG14562-catalog-two-source-proof-resolution-v1/manifest.json','0eade5a1336d0c4a01bd6a951e1c1310278ee6a3376ee448a95903b904ec68ab')
    assert previous['source']==SOURCE and not any(c['classname'].rsplit('.',1)[-1] in COUNTS for c in previous['cases'])
    run.step=environmental_step
    run.main()
