"""Original media streamer two; Test-owned temporary file and borrowed channels, no retained native authority."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
MAIN_UNITS={'dev/codex/schubert/nk/web/media/MediaBodyStreamer':dict(module='web',name='dev/codex/schubert/nk/web/media/MediaBodyStreamer',sha256='5d5869e2c2edeafcfcd1251a9b5ea0f7eb2ebe31e79a89544e799bd5dd9976a6')}
CLOSURES={n:[n] for n in MAIN_UNITS}
FIXTURES={}
METADATA=set()
UNEXECUTED=set()
COUNTS={'MediaBodyStreamerTest':2}
SESSION='PG16572-MEDIA-BODY-STREAM-ORIGINAL-TWO'
ROOT=data.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/media'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
TEST_PINS={'MediaBodyStreamerTest':'28a2c1f1f66e23da72e4cde4c0090ea73afd5675708b2a1474075895ce82d4aa'}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16572-media-body-stream-original-two-pt-v1';run.OUT=data.BASE/'PG16572-media-body-stream-original-two-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/MediaBodyTwoCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MediaBodyStreamerTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.FIXTURES,run.COUNTS={},COUNTS;run.EXTRA_TEST_SOURCES=(REPORTER,);run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    previous=data.read_checked(data.BASE/'PG16562-current2267-management-encoder-registry-v1/manifest.json','4ed1fa5d5c1a4297d884710c05a76905bc279b12d2c1ff9f35022d3250a18bef')
    assert normal['source']==previous['source']==SOURCE
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));text=path.read_text()
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==TEST_PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.web.media.MediaBodyStreamerTest' not in previous['suiteNames']
        assert not any(v in text for v in ['@Before','@After','ProcessBuilder','DriverManager','HttpClient','KeyStore','java.sql','RootStartupContext','RootFailedStartRecovery','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec'])
    assert set(MAIN_UNITS)&previous['fullSourceUnits'].keys()==set()
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert normal['begin']['inputHashes'][path]==run.host.sha(data.ROOT/path)==row['sha256']
        with zipfile.ZipFile(normal['jars']['web']['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    run.step=environmental_step;run.main()
