"""Original whole synthetic inode guards and public filename/mode catalogs, no Backup or native action."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME='dev/codex/schubert/nk/batch/file/MorningBackupArtifacts'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='6adcab52b4556a1ad56dfef2a5e98dfb986773793b1b32f85c11fea7f459d35e')}
CLOSURES={NAME:[NAME,NAME+'$Work',NAME+'$Writer']}
METADATA={NAME+'$Work',NAME+'$Writer'}
UNEXECUTED=set()
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file'
DECLARED={'MorningBackupMetadataTest':('94c57452f8470e76c030d0d9638379682f5e53521708215aecf49f18441e6d8f',4),
          'MorningBackupCatalogTest':('f3ad19855c688c2a4b9156cbb419876fe4d6445f1b13d44ad6317813eedc823c',1),
          'MorningBackupInputModeTest':('17f6aa73693e38b8c98a8737ea97462924b7de06ad02fb8c06822f13a1f7ae58',3)}
TESTS={n:ROOT/(n+'.java') for n in DECLARED}
COUNTS={n:v[1] for n,v in DECLARED.items()}
FIXTURES={}
SESSION='PG16176-ORIGINAL-MORNING-BACKUP-VALUES-EIGHT'
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

def source_path(row):
    return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'

if __name__=='__main__':
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16176-morning-backup-value-eight-pt-v1';run.OUT=data.BASE/'PG16176-morning-backup-value-eight-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/MorningBackupValueEightJunitLauncher.java'
    run.NEW_TEST=TESTS['MorningBackupMetadataTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='MorningBackupMetadataTest'}
    run.FIXTURES,run.COUNTS=FIXTURES,COUNTS;run.EXTRA_TEST_SOURCES,run.SESSION_ID=(REPORTER,),SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    previous=data.read_checked(data.BASE/'PG16166-current2136-caddy-config-registry-v1/manifest.json','8f4646787f63d7060a25143c36c8250ffc650086d591ce413f5a477f7d8a3842')
    assert normal['source']==previous['source']==SOURCE
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(data.ROOT))
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==DECLARED[name][0]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.file.'+name not in previous['suiteNames']
        assert not any(v in text for v in ['@Before','Files.','ProcessBuilder','DriverManager','HttpClient','RootStartupContext','KeyStore','MessageDigest','java.sql','Linux','new MorningBackupArtifacts','TemporaryInfrastructureException','WebStartupException'])
    require_path=source_path(MAIN_UNITS[NAME])
    assert normal['begin']['inputHashes'][require_path]==run.host.sha(data.ROOT/require_path)==run.host.sha(COMPILE/'snapshot'/require_path)==MAIN_UNITS[NAME]['sha256']
    assert NAME not in previous['fullSourceUnits']
    with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
        assert {n[:-6] for n in jar.namelist() if n==NAME+'.class' or n.startswith(NAME+'$') and n.endswith('.class')}==set(CLOSURES[NAME])
    run.step=environmental_step;run.main()
