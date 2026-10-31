"""Original public RFC signature8; real public-only JCA verification, no signer or private/runtime keys."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME='dev/codex/schubert/nk/bootstrap/ReleaseSignatureVerifier'
MAIN_UNITS={NAME:dict(module='bootstrap',name=NAME,sha256='1579d05037690746840b972c8b7c694b3aa3967c93f1e76bf5cf5dc48449a6e7')}
CLOSURES={NAME:[NAME,NAME+'$Crypto',NAME+'$NativeCrypto']}
METADATA={NAME+'$Crypto'}
UNEXECUTED=set()
COUNTS={'ReleaseSignatureVerifierTest':8}
SESSION='PG16524-RELEASE-PUBLIC-SIGNATURE-ORIGINAL-EIGHT'
ROOT=data.ROOT/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
TEST_PINS={'ReleaseSignatureVerifierTest':'2f02b94bd908ca395000a05b8bc9928e184539f8a512d39ec30290f7cc65dd06'}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16524-release-public-signature-original-eight-pt-v1';run.OUT=data.BASE/'PG16524-release-public-signature-original-eight-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/ReleasePublicSignatureEightCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['ReleaseSignatureVerifierTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.FIXTURES,run.COUNTS={},COUNTS;run.EXTRA_TEST_SOURCES=(REPORTER,);run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    previous=data.read_checked(data.BASE/'PG16514-current2252-release-inventory-registry-v1/manifest.json','14e8a27f44cfaed103801f6a098b2b78e2ce7937800bceb9fc619f3c06b50ce6')
    assert normal['source']==previous['source']==SOURCE
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));text=path.read_text()
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==TEST_PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.bootstrap.ReleaseSignatureVerifierTest' not in previous['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','ProcessBuilder','DriverManager','HttpClient','KeyStore','java.sql','RootStartupContext','RootFailedStartRecovery','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec'])
    assert not set(MAIN_UNITS)&previous['fullSourceUnits'].keys()
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert normal['begin']['inputHashes'][path]==run.host.sha(data.ROOT/path)==row['sha256']
        with zipfile.ZipFile(normal['jars']['bootstrap']['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    run.step=environmental_step;run.main()
