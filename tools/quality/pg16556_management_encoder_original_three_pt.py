"""Whole encoder3, supplied remaining-time lambda only; no native or actual owner authority."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME='dev/codex/schubert/nk/batch/mq/ArtemisManagementReadinessClient'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='3eb82d01455cf8d2932baf0bc9ed57c2d843a5bd7e071cdc285958a370413f73')}
CLOSURES={NAME:["dev/codex/schubert/nk/batch/mq/ArtemisManagementReadinessClient","dev/codex/schubert/nk/batch/mq/ArtemisManagementReadinessClient$Exchange","dev/codex/schubert/nk/batch/mq/ArtemisManagementReadinessClient$MessageWriter","dev/codex/schubert/nk/batch/mq/ArtemisManagementReadinessClient$OperationEncoder","dev/codex/schubert/nk/batch/mq/ArtemisManagementReadinessClient$OwnedOperation","dev/codex/schubert/nk/batch/mq/ArtemisManagementReadinessClient$Reader"]}
FIXTURES={}
METADATA=set(CLOSURES[NAME])-{NAME}
UNEXECUTED=set()
COUNTS={'ArtemisManagementEncoderBoundaryTest':3}
SESSION='PG16556-MANAGEMENT-ENCODER-ORIGINAL-THREE'
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
TEST_PINS={'ArtemisManagementEncoderBoundaryTest':'ee3da610da96cae066ee32e1ee49a4999605291cfd5ab4d5b6d65e2a775a64ee'}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16556-management-encoder-original-three-pt-v1';run.OUT=data.BASE/'PG16556-management-encoder-original-three-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/ManagementEncoderThreeCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['ArtemisManagementEncoderBoundaryTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.FIXTURES,run.COUNTS={},COUNTS;run.EXTRA_TEST_SOURCES=(REPORTER,);run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    previous=data.read_checked(data.BASE/'PG16547-current2264-artemis-unknown-registry-v2/manifest.json','a0adfe5eea43bfa8ee31dee06915388363e4ffdb839878c03689aca59c25b2db')
    assert normal['source']==previous['source']==SOURCE
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));text=path.read_text()
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==TEST_PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.mq.ArtemisManagementEncoderBoundaryTest' not in previous['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','ProcessBuilder','DriverManager','HttpClient','KeyStore','java.sql','RootStartupContext','RootFailedStartRecovery','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec'])
    assert set(MAIN_UNITS)<=previous['fullSourceUnits'].keys()
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert normal['begin']['inputHashes'][path]==run.host.sha(data.ROOT/path)==row['sha256']
        with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    run.step=environmental_step;run.main()
