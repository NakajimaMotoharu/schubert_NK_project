"""Original snapshot seven and one independent public-values fixture; memory-only."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
P='dev/codex/schubert/nk/batch/platform/'
NAME=P+'MaintenanceStopSnapshot'
ENUM=P+'MaintenanceUnit'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='767e81698cf113cf65b1bd7a6d939dcff07dee94725d297dc78984d9817cc3b4'),ENUM:dict(module='batch',name=ENUM,sha256='e764ee58aacff2e95fbc30f9102fe40295a25ac0b41df0aaa3ef03a625e34733')}
CLOSURES={NAME:[NAME],ENUM:[ENUM]}
METADATA=set()
UNEXECUTED=set()
COUNTS={'MaintenanceStopSnapshotTest':7,'MaintenanceObservedValuesContractTest':1}
SESSION='PG16430-MAINTENANCE-STOP-PARSER-EIGHT'
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform'
TEST=ROOT/'MaintenanceStopSnapshotTest.java'
FIXTURE=data.ROOT/'tools/quality/architecture/MaintenanceObservedValuesContractTest.java'
FIXTURE_SHA='d22efaa6e89950af75dd650fe80173fa6546d88348d2ee6098afa3b9e0d6f0a7'
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
FIXTURES={}
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'

if __name__=='__main__':
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16430-maintenance-stop-parser-eight-pt-v1';run.OUT=data.BASE/'PG16430-maintenance-stop-parser-eight-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/MaintenanceSnapshotEightJunitLauncher.java'
    run.NEW_TEST=FIXTURE;run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.FIXTURES,run.COUNTS=FIXTURES,COUNTS;run.EXTRA_TEST_SOURCES=(REPORTER,);run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    previous=data.read_checked(data.BASE/'PG16420-current2189-process-scope-registry-v1/manifest.json','4346e90455e1497c5317a5388776ef8a8e519fc25262d114b79bec2e0936cbad')
    assert normal['source']==previous['source']==SOURCE
    relative=str(TEST.relative_to(data.ROOT))
    assert run.host.sha(TEST)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)=='6b33e77253864cbfafb6327be73022e2216eeaef9a2c3915c274604b950cfd39'
    assert run.host.sha(FIXTURE)==FIXTURE_SHA
    for path,count in [(TEST,7),(FIXTURE,1)]:
        text=path.read_text()
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==count
        assert 'dev.codex.schubert.nk.batch.platform.'+path.stem not in previous['suiteNames']
        assert not any(v in text for v in ['@Before','@TempDir','ProcessBuilder','DriverManager','HttpClient','KeyStore','java.sql','java.net.','java.nio.file.','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec','SystemctlStateSource','NativeReader','RootStartupContext'])
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert normal['begin']['inputHashes'][path]==run.host.sha(data.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==row['sha256']
        with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    assert NAME not in previous['fullSourceUnits'] and ENUM in previous['fullSourceUnits']
    run.step=environmental_step;run.main()
