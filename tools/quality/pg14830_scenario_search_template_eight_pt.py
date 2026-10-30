"""Explicit original Search8, fixed mock resource mapping and own public trace, no media operation."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run
import pg14790_music_hierarchy_template_six_pt as resource

SOURCE=resource.SOURCE
COMPILE=resource.COMPILE
COMPILE_SHA=resource.COMPILE_SHA
COUNTS={'ScenarioSearchTemplateTest':8}
SESSION='PG14830-ORIGINAL-SCENARIO-SEARCH-TEMPLATE8'
ROOT=data.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view'
TESTS={'ScenarioSearchTemplateTest':ROOT/'ScenarioSearchTemplateTest.java'}
PINS={'ScenarioSearchTemplateTest':'d05eea8b4a2ba3c1656abcd0eb5b9521da251498e5b119360416c80927df7650'}
FIXTURES={}
REPORTER=resource.REPORTER
RESOURCES={
 'templates/search.html':'e3db4ebdc9372eb396d2fe95cf56aced827d400503cca1317b3572e53a69c4a7',
 'templates/fragments/pagination.html':'ddf3ccc9a1f88adf5bd61c8c9aa8928022f97c6e8f314c48941aad267bd5cb80',
 'templates/fragments/layout.html':'a48bda151f893e28858afb26d1c636a564b8bd0cb3c3a16bc63bbb97f0e414bd',
 'static/js/search-speaker-submit.js':'dcf25a57a0e304391a0d3c880c263db246e296d6a7af0322283ddb72fa3e48fa',
 'static/css/schubert.css':'1466825b3caeb2654a181cd88356e4b6599e0549bf527a81f5826fef6d34a11d'}
READ_COPIES=['static/css/schubert.css','static/js/search-speaker-submit.js']
TRACE='target/scenario-screen-traces/PT-SCR-033.txt'
EXPECTED_TRACE='template=search\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumRows=100\nmaximumSpeakers=500\nactualNkGate=false\n'
resource.RESOURCES=RESOURCES;resource.READ_COPIES=READ_COPIES
resource.TRACE=TRACE;resource.EXPECTED_TRACE=EXPECTED_TRACE
resource_inputs=resource.resource_inputs

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14830-scenario-search-template-eight-pt-v1';run.OUT=data.BASE/'PG14830-scenario-search-template-eight-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalScenarioSearchTemplateJunitLauncher.java'
    run.NEW_TEST=TESTS['ScenarioSearchTemplateTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG14822-resource-dom-post-v2-independent-v1/manifest.json','3a4495e18b0f585da83bfcd584ed58739148cd92382f125341a53416f9b765fe')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['allSubstantivePriorReceiptValuesEqual'] is True and proof['toolChecks']==26 and proof['independentNegativeVectors']==13
    reporter=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert reporter['actualExit']==reporter['productTestsExecuted']==0 and reporter['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==reporter['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=resource_inputs();p=run.NEW_TEST;relative=str(p.relative_to(data.ROOT))
    assert relative=='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/ScenarioSearchTemplateTest.java' and normal['begin']['inputHashes'][relative]==run.host.sha(p)==run.host.sha(COMPILE/'snapshot'/relative)==PINS['ScenarioSearchTemplateTest']
    text=p.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==8
    assert '"dev.codex.schubert.nk.web.view.ScenarioSearchTemplateTest", 8' in run.HELPER.read_text()
    assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','preserveFatal('])
    assert text.count('Files.readString(')==2 and text.count('Files.createDirectories(')==text.count('Files.writeString(')==1
    assert 'context.register(WebMvcConfiguration.class)' in text and 'task.get(20, TimeUnit.SECONDS)' in text and 'Executors.newFixedThreadPool(8)' in text
    run.step=resource.resource_step;run.main()
