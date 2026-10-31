"""Current-source original synthetic Observed wrapper case only; no permit/root operation."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME='dev/codex/schubert/nk/batch/file/RootCurrentPermitPreflight'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='a2b964d8af4c22513a2b6e3b4645602d8778a1cda28b38aedf40ee2521c6ad89')}
CLOSURES={NAME:[NAME,NAME+'$Observed']}
METADATA=set()
UNEXECUTED={NAME}
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file'
TESTS={'CurrentObservationValueTest':ROOT/'CurrentObservationValueTest.java'}
COUNTS={'CurrentObservationValueTest':1}
FIXTURES={}
SESSION='PG16328-CURRENT-OBSERVATION-ONE'
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

def source_path(row):
    return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'

if __name__=='__main__':
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16328-current-observation-one-pt-v1';run.OUT=data.BASE/'PG16328-current-observation-one-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/CurrentObservationOneJunitLauncher.java'
    run.NEW_TEST=TESTS['CurrentObservationValueTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.FIXTURES,run.COUNTS=FIXTURES,COUNTS;run.EXTRA_TEST_SOURCES,run.SESSION_ID=(REPORTER,),SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    previous=data.read_checked(data.BASE/'PG16318-current2173-bootstrap-enum-registry-v1/manifest.json','7c618826ff3db2244157c3b1df5fe0c7af7790db3e7d6c45176fbf0b7549e6be')
    assert normal['source']==previous['source']==SOURCE
    path=TESTS['CurrentObservationValueTest'];relative=str(path.relative_to(data.ROOT));text=path.read_text()
    assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)=='527f57cd6b2068338c965c939e9a04bdace62ac71c6fe4a481a9ffd56a82a1d4'
    assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==1
    assert 'dev.codex.schubert.nk.batch.file.CurrentObservationValueTest' not in previous['suiteNames']
    assert not any(v in text for v in ['@Before','ProcessBuilder','DriverManager','HttpClient','RootStartupContext','KeyStore','java.sql','Linux','parentsGuard','ChildStartupContext','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec'])
    assert re.search(r'(?<![A-Za-z0-9_$])Files\s*\.',text) is None
    assert re.search(r'RootCurrentPermitPreflight\.(?!Observed\b)',text) is None
    assert re.search(r'StartupPermitRecords\.(?!(?:Epoch|Permit|State)\b)',text) is None
    require_path=source_path(MAIN_UNITS[NAME])
    assert normal['begin']['inputHashes'][require_path]==run.host.sha(data.ROOT/require_path)==run.host.sha(COMPILE/'snapshot'/require_path)==MAIN_UNITS[NAME]['sha256']
    assert NAME not in previous['fullSourceUnits']
    with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
        assert {n[:-6] for n in jar.namelist() if n==NAME+'.class' or n.startswith(NAME+'$') and n.endswith('.class')}==set(CLOSURES[NAME])
    run.step=environmental_step;run.main()
