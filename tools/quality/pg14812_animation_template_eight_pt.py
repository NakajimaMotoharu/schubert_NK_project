"""Explicit Animation-only original8; reuse qualified own-resource copy runner, no playback."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run
import pg14790_music_hierarchy_template_six_pt as resource

SOURCE=resource.SOURCE
COMPILE=resource.COMPILE
COMPILE_SHA=resource.COMPILE_SHA
COUNTS={'AnimationTemplateTest':8}
SESSION='PG14812-ORIGINAL-ANIMATION-TEMPLATE8'
ROOT=data.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view'
TESTS={'AnimationTemplateTest':ROOT/'AnimationTemplateTest.java'}
PINS={'AnimationTemplateTest':'44192f04a5d5d37df05e231be8fb60fcf6d1bb7b8eb43060dbc691e2e5926945'}
FIXTURES={}
REPORTER=resource.REPORTER
RESOURCES={
 'templates/animation.html':'008fe35863ee9c48b82c674df78572573313b29c321686259a64e8191cbe5b4d',
 'templates/animation-list.html':'cfec2c00935f2af53ee51eb1726cfc676e1040312a0632d172f7e9ff283ac702',
 'templates/fragments/layout.html':'a48bda151f893e28858afb26d1c636a564b8bd0cb3c3a16bc63bbb97f0e414bd',
 'static/css/schubert.css':'1466825b3caeb2654a181cd88356e4b6599e0549bf527a81f5826fef6d34a11d'}
READ_COPIES=['static/css/schubert.css']
TRACE='target/scenario-screen-traces/PT-SCR-053.txt'
EXPECTED_TRACE='templates=animation|animation-list\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumRecords=50\nactualNkGate=false\n'
# Only explicit resource metadata varies; the frozen copy/ownership implementation is reused.
resource.RESOURCES=RESOURCES;resource.READ_COPIES=READ_COPIES
resource.TRACE=TRACE;resource.EXPECTED_TRACE=EXPECTED_TRACE
resource_inputs=resource.resource_inputs

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14812-animation-template-eight-pt-v1';run.OUT=data.BASE/'PG14812-animation-template-eight-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalAnimationTemplateJunitLauncher.java'
    run.NEW_TEST=TESTS['AnimationTemplateTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG14810-resource-dom-post-independent-v1/manifest.json','b56ddab4973f94102ebd4894fdb4f2759b6dd172c13f3e3afabdb0403c1e898f')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['allSubstantivePriorReceiptValuesEqual'] is True and proof['toolChecks']==23 and proof['independentNegativeVectors']==13
    reporter=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert reporter['actualExit']==reporter['productTestsExecuted']==0 and reporter['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==reporter['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=resource_inputs();p=run.NEW_TEST;relative=str(p.relative_to(data.ROOT))
    assert relative=='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/AnimationTemplateTest.java' and normal['begin']['inputHashes'][relative]==run.host.sha(p)==run.host.sha(COMPILE/'snapshot'/relative)==PINS['AnimationTemplateTest']
    text=p.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==8
    assert '"dev.codex.schubert.nk.web.view.AnimationTemplateTest", 8' in run.HELPER.read_text()
    assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','preserveFatal('])
    assert text.count('Files.readString(')==text.count('Files.createDirectories(')==text.count('Files.writeString(')==1 and 'c.register(WebMvcConfiguration.class)' in text
    assert 'task.get(10, TimeUnit.SECONDS)' in text and 'Executors.newFixedThreadPool(8)' in text
    run.step=resource.resource_step;run.main()
