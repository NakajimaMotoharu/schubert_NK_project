"""Entire original Scenario detail template8 with pinned Main resources and owned-slot CSS/trace only."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'ScenarioDetailTemplateTest':8}
SESSION='PG14618-ORIGINAL-DETAIL-TEMPLATE8'
ROOT=run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view'
TESTS={'ScenarioDetailTemplateTest':ROOT/'ScenarioDetailTemplateTest.java'}
PINS={'ScenarioDetailTemplateTest':'3c82696d0420cc1fce18e59a39e6709c488e86d9ab8e9b4cf60993d76f40a630'}
FIXTURES={}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'


RESOURCES={
 'templates/scenario.html':'b9709c596a3f98653d854f637ae48e742704b80537460c6f3acc5d6bd342a245',
 'templates/fragments/layout.html':'a48bda151f893e28858afb26d1c636a564b8bd0cb3c3a16bc63bbb97f0e414bd',
 'static/css/schubert.css':'1466825b3caeb2654a181cd88356e4b6599e0549bf527a81f5826fef6d34a11d'}
EXPECTED_TRACE='template=scenario\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumEntries=10000\nmaximumVoices=999\nactualNkGate=false\n'

def resource_inputs():
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    jar=normal['jars']['web'];assert run.host.sha(__import__('pathlib').Path(jar['path']))==jar['sha256']
    with zipfile.ZipFile(jar['path']) as archive:
        for rel,pin in RESOURCES.items():
            path='src/schubert-nk-web/src/main/resources/'+rel
            assert normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==pin
            assert data.sha(archive.read(rel))==run.host.sha(COMPILE/'snapshot'/path)==pin
    return dict(RESOURCES)

def reviewed_resource_step(name,command):
    pins=resource_inputs()
    if name=='selected-junit':
        css=run.SLOT/'src/main/resources/static/css/schubert.css'
        assert not css.exists()
        css.parent.mkdir(parents=True)
        payload=(COMPILE/'snapshot/src/schubert-nk-web/src/main/resources/static/css/schubert.css').read_bytes()
        with css.open('xb') as stream:stream.write(payload)
        assert run.host.sha(css)==RESOURCES['static/css/schubert.css']
    result=environmental_step(name,command)
    if name=='selected-junit':
        result['reviewedMainResourceHashes']=pins
        result['ownedCssReadPath']=str(css)
        assert run.host.sha(css)==RESOURCES['static/css/schubert.css']
        if result['actualExit']==0:
            output=run.SLOT/'target/scenario-screen-traces/PT-SCR-024.txt'
            assert output.read_text()==EXPECTED_TRACE
            result['ownedSyntheticTrace']=dict(path=str(output),sha256=run.host.sha(output))
    assert resource_inputs()==pins
    return result

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14618-detail-template-whole-eight-pt-v1'
    run.OUT=run.host.BASE/'PG14618-detail-template-whole-eight-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalDetailTemplateJunitLauncher.java'
    run.NEW_TEST=TESTS['ScenarioDetailTemplateTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='ScenarioDetailTemplateTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"'+str(path.relative_to(run.host.ROOT)).split('/src/test/java/',1)[1][:-5].replace('/','.')+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    text=TESTS['ScenarioDetailTemplateTest'].read_text()
    assert text.count('Files.readString(')==text.count('Files.createDirectories(')==text.count('Files.writeString(')==1
    assert 'Path.of("src/main/resources/static/css/schubert.css")' in text
    assert 'Path.of("target/scenario-screen-traces")' in text
    assert 'root.resolve("PT-SCR-024.txt")' in text
    assert 'context.register(WebMvcConfiguration.class)' in text
    resource_inputs()
    run.step=reviewed_resource_step
    run.main()
