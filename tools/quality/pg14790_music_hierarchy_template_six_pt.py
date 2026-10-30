"""Whole original Music hierarchy template6 with own resource reads and synthetic trace."""
import re
import zipfile
from pathlib import Path
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'MusicHierarchyTemplateTest':6}
SESSION='PG14790-ORIGINAL-MUSIC-HIERARCHY-TEMPLATE6'
ROOT=data.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view'
TESTS={'MusicHierarchyTemplateTest':ROOT/'MusicHierarchyTemplateTest.java'}
PINS={'MusicHierarchyTemplateTest':'6469d3a588ea7ae9ba6cd7a93524e16ef2cd293631c58f0a24013b86e8d5502c'}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
RESOURCES={
 'templates/music.html':'fbbf5a79417693cff98acdc75eef97fd30561362ce95fff4ad2d8b703d68743f',
 'templates/music-sections.html':'62b31b622da8c27fbfe8c238ea9a4579d12d22247bd2390b5dbfbbc88650d2e4',
 'templates/fragments/layout.html':'a48bda151f893e28858afb26d1c636a564b8bd0cb3c3a16bc63bbb97f0e414bd',
 'static/css/schubert.css':'1466825b3caeb2654a181cd88356e4b6599e0549bf527a81f5826fef6d34a11d'}
READ_COPIES=['templates/music.html','templates/music-sections.html','static/css/schubert.css']
TRACE='target/scenario-screen-traces/PT-SCR-071.txt'
EXPECTED_TRACE='templates=music|music-sections\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumCategories=20\nmaximumSections=100\nactualNkGate=false\n'

def resource_inputs():
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    jar=normal['jars']['web'];assert run.host.sha(Path(jar['path']))==jar['sha256']
    with zipfile.ZipFile(jar['path']) as archive:
        for rel,pin in RESOURCES.items():
            path='src/schubert-nk-web/src/main/resources/'+rel
            assert normal['begin']['inputHashes'][path]==run.host.sha(data.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin==data.sha(archive.read(rel))
    return normal

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
        if result['actualExit']==0:
            output=run.SLOT/TRACE;assert output.read_text()==EXPECTED_TRACE
            result['ownedSyntheticTrace']=dict(path=str(output),sha256=run.host.sha(output))
    resource_inputs();return result

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14790-music-hierarchy-template-six-pt-v1';run.OUT=data.BASE/'PG14790-music-hierarchy-template-six-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalMusicHierarchyTemplateJunitLauncher.java'
    run.NEW_TEST=TESTS['MusicHierarchyTemplateTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=resource_inputs();p=run.NEW_TEST;relative=str(p.relative_to(data.ROOT))
    assert relative=='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/MusicHierarchyTemplateTest.java'
    assert normal['begin']['inputHashes'][relative]==run.host.sha(p)==run.host.sha(COMPILE/'snapshot'/relative)==PINS['MusicHierarchyTemplateTest']
    text=p.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==6
    assert '"dev.codex.schubert.nk.web.view.MusicHierarchyTemplateTest", 6' in run.HELPER.read_text()
    assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','preserveFatal('])
    assert text.count('Files.readString(')==2 and text.count('Files.createDirectories(')==text.count('Files.writeString(')==1
    assert 'c.register(WebMvcConfiguration.class)' in text and 'task.get(10, TimeUnit.SECONDS)' in text and 'Executors.newFixedThreadPool(8)' in text
    run.step=resource_step;run.main()
