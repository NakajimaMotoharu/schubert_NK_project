"""Original whole ProcessScope seven at current frozen Source; fake Process/own threads only."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME='dev/codex/schubert/nk/batch/platform/ProcessResourceScope'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='6ea511aa08b6182d29cc67da0b7d6ea77112a612ff31c57bee36306042bf2313')}
CLOSURES={NAME:[NAME,NAME+'$OwnedQuery',NAME+'$QueryWork']}
METADATA={NAME+'$OwnedQuery',NAME+'$QueryWork'}
UNEXECUTED=set()
COUNTS={'ProcessResourceScopeTest':7}
SESSION='PG16414-PROCESS-SCOPE-CURRENT-SEVEN'
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform'
TEST=ROOT/'ProcessResourceScopeTest.java'
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
FIXTURES={}
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'

if __name__=='__main__':
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16414-process-scope-original-seven-pt-v1';run.OUT=data.BASE/'PG16414-process-scope-original-seven-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/ProcessScopeSevenCurrentJunitLauncher.java'
    run.NEW_TEST=TEST;run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.FIXTURES,run.COUNTS=FIXTURES,COUNTS;run.EXTRA_TEST_SOURCES=(REPORTER,);run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    previous=data.read_checked(data.BASE/'PG16404-current2182-legacy-policy-registry-v1/manifest.json','34386ddf6c7fe6c067f5b5909735d8f487de5a8fc0b95d959bedb201b8ed9889')
    assert normal['source']==previous['source']==SOURCE
    relative=str(TEST.relative_to(data.ROOT));text=TEST.read_text()
    assert run.host.sha(TEST)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)=='cf94df05fa8559b35af74879256271b41df718f7f5eb1b5251cc0a9f42d99d06'
    assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==7
    assert 'dev.codex.schubert.nk.batch.platform.ProcessResourceScopeTest' not in previous['suiteNames']
    assert not any(v in text for v in ['@Before','@TempDir','ProcessBuilder','DriverManager','HttpClient','RootStartupContext','KeyStore','java.sql','java.net.','java.nio.file.','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec','new SystemctlStateSource()','new InspectorUnitProbe.NativeReader()','NativeReader.forTarget('])
    assert 'new SystemctlStateSource(command -> child)' in text and 'class Child extends Process' in text and 'class StreamingChild extends Process' in text
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert normal['begin']['inputHashes'][path]==run.host.sha(data.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==row['sha256']
        assert name in previous['fullSourceUnits'] and previous['fullSourceUnits'][name]['four100'] is False
        with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    run.step=environmental_step;run.main()
