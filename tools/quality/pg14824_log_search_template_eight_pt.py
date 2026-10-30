"""Whole original Logs DOM/resource8, no actual log backend and no invented trace file."""
import re
from pathlib import Path
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run
import pg14790_music_hierarchy_template_six_pt as resource
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step

SOURCE=resource.SOURCE
COMPILE=resource.COMPILE
COMPILE_SHA=resource.COMPILE_SHA
COUNTS={'LogSearchTemplateTest':8}
SESSION='PG14824-ORIGINAL-LOG-SEARCH-TEMPLATE8'
ROOT=data.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view'
TESTS={'LogSearchTemplateTest':ROOT/'LogSearchTemplateTest.java'}
PINS={'LogSearchTemplateTest':'c9912665cba2dccc7d4273d07cda9ebd2344ccf6e9c76e9e7630575aeac64527'}
FIXTURES={}
REPORTER=resource.REPORTER
RESOURCES={
 'templates/logs.html':'7bbd176e40d8a9f5b67be8f57cd27d42ccafd5e3bcabc95a56d75c370ce62708',
 'templates/fragments/log-pagination.html':'4b3908ed49684bf3acb35457656802e9e2e1a8dac5a84073b2f213413c543ee2',
 'templates/fragments/layout.html':'a48bda151f893e28858afb26d1c636a564b8bd0cb3c3a16bc63bbb97f0e414bd',
 'static/js/log-search-validation.js':'b5cfbc9a689c91d0f14461e3e46dadb88844b5d0c38358d762dd241a5458efad',
 'static/css/schubert.css':'1466825b3caeb2654a181cd88356e4b6599e0549bf527a81f5826fef6d34a11d'}
READ_COPIES=['templates/logs.html','static/js/log-search-validation.js']
TRACE=None
EXPECTED_TRACE=None
resource.RESOURCES=RESOURCES
resource_inputs=resource.resource_inputs

def resource_step(name,command):
    resource_inputs()
    if name=='selected-junit':
        for rel in READ_COPIES:
            target=run.SLOT/'src/main/resources'/rel;assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as stream:stream.write((COMPILE/'snapshot/src/schubert-nk-web/src/main/resources'/rel).read_bytes())
            assert run.host.sha(target)==RESOURCES[rel]
    result=environmental_step(name,command)
    if name=='selected-junit':
        result['reviewedMainResourceHashes']=dict(RESOURCES)
        result['ownedResourceReadCopies']={str(run.SLOT/'src/main/resources'/rel):RESOURCES[rel] for rel in READ_COPIES}
        assert all(run.host.sha(Path(p))==h for p,h in result['ownedResourceReadCopies'].items())
        assert 'ownedSyntheticTrace' not in result
    resource_inputs();return result

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14824-log-search-template-eight-pt-v1';run.OUT=data.BASE/'PG14824-log-search-template-eight-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalLogSearchTemplateJunitLauncher.java'
    run.NEW_TEST=TESTS['LogSearchTemplateTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG14822-resource-dom-post-v2-independent-v1/manifest.json','3a4495e18b0f585da83bfcd584ed58739148cd92382f125341a53416f9b765fe')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['allSubstantivePriorReceiptValuesEqual'] is True and proof['toolChecks']==26 and proof['independentNegativeVectors']==13 and proof['noTraceProfilePositive'] is True
    reporter=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert reporter['actualExit']==reporter['productTestsExecuted']==0 and reporter['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==reporter['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=resource_inputs();p=run.NEW_TEST;relative=str(p.relative_to(data.ROOT))
    assert relative=='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/LogSearchTemplateTest.java' and normal['begin']['inputHashes'][relative]==run.host.sha(p)==run.host.sha(COMPILE/'snapshot'/relative)==PINS['LogSearchTemplateTest']
    text=p.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==8
    assert '"dev.codex.schubert.nk.web.view.LogSearchTemplateTest", 8' in run.HELPER.read_text()
    assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','preserveFatal(','Files.createDirectories(','Files.writeString('])
    assert text.count('Files.readString(')==2 and 'c.register(WebMvcConfiguration.class)' in text and 'get(10, TimeUnit.SECONDS)' in text and 'Executors.newFixedThreadPool(8)' in text
    run.step=resource_step;run.main()
