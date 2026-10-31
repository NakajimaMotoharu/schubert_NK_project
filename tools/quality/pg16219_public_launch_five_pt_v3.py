"""Original public correlation whole four plus independently authored DEL/EOF boundary one."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME='dev/codex/schubert/nk/batch/file/StartupLaunchRecord'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='2d5590794349337b7351f97582511f4c2244b8ae3fe42a7976202eb766cf05d5')}
CLOSURES={NAME:[NAME,NAME+'$DigestFactory']}
METADATA={NAME+'$DigestFactory'}
UNEXECUTED=set()
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file'
TESTS={'StartupLaunchRecordTest':ROOT/'StartupLaunchRecordTest.java',
       'PublicLaunchFramingBoundaryTest':data.ROOT/'tools/quality/architecture/PublicLaunchFramingBoundaryTest.java'}
COUNTS={'StartupLaunchRecordTest':4,'PublicLaunchFramingBoundaryTest':1}
FIXTURES={}
SESSION='PG16219-PUBLIC-LAUNCH-FIVE'
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

def source_path(row):
    return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'

def files_call(text):
    return re.search(r'(?<![A-Za-z0-9_$])Files\s*\.',text) is not None

if __name__=='__main__':
    assert not any(files_call(v) for v in ['ServiceConfigFiles.Service.values()', 'PublicServiceConfigFiles.Service'])
    assert all(files_call(v) for v in ['Files.readAllBytes(p)', 'java.nio.file.Files.readAllBytes(p)', 'Files  .  readAllBytes(p)'])
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16219-public-launch-five-pt-v1';run.OUT=data.BASE/'PG16219-public-launch-five-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/PublicLaunchFiveJunitLauncher.java'
    run.NEW_TEST=TESTS['StartupLaunchRecordTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={'PublicLaunchFramingBoundaryTest':TESTS['PublicLaunchFramingBoundaryTest']}
    run.FIXTURES,run.COUNTS=FIXTURES,COUNTS;run.EXTRA_TEST_SOURCES,run.SESSION_ID=(REPORTER,),SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    previous=data.read_checked(data.BASE/'PG16182-current2144-backup-values-registry-v1/manifest.json','11c34b85628be56cb0365f3889a747953e5540746b3484014650752de9f0597e')
    assert normal['source']==previous['source']==SOURCE
    original=TESTS['StartupLaunchRecordTest'];relative=str(original.relative_to(data.ROOT))
    assert run.host.sha(original)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)=='cfb3ced853e96604d7746b195727258106aa75ec5af6d0f010dc7539f99f648d'
    for name,path in TESTS.items():
        text=path.read_text()
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.file.'+name not in previous['suiteNames']
        assert not files_call(text)
        assert not any(v in text for v in ['@Before','ProcessBuilder','DriverManager','HttpClient','RootStartupContext','KeyStore','java.sql','Linux','parentsGuard','ChildStartupContext','TemporaryInfrastructureException','WebStartupException'])
    parent='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame.java'
    assert normal['begin']['inputHashes'][parent]==run.host.sha(data.ROOT/parent)=='48645538321f59775ceca14b6c4ee201db6cbad142e7ca7551e35145f886f4e7'
    require_path=source_path(MAIN_UNITS[NAME])
    assert normal['begin']['inputHashes'][require_path]==run.host.sha(data.ROOT/require_path)==run.host.sha(COMPILE/'snapshot'/require_path)==MAIN_UNITS[NAME]['sha256']
    assert NAME not in previous['fullSourceUnits']
    with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
        assert {n[:-6] for n in jar.namelist() if n==NAME+'.class' or n.startswith(NAME+'$') and n.endswith('.class')}==set(CLOSURES[NAME])
    assert run.host.sha(TESTS['PublicLaunchFramingBoundaryTest'])=='512b867e5f11992ea0a37bfb3693aa7a36a1a59719d7f51e4b658a4da152c1eb'
    assert run.host.sha(run.HELPER)=='de98df7d731b4af07a65395b3211d7ce28fd04351576e51441106d6a7f9c9a22'
    assert not any('ServiceConfigFiles' in (ROOT/(name+'.java')).read_text() for name in ['MorningBackupMetadataTest','MorningBackupCatalogTest','MorningBackupInputModeTest'])
    run.step=environmental_step;run.main()
