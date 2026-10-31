"""Original whole request trace10, Mock-only and normal public Source read."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
MAIN_UNITS={"dev/codex/schubert/nk/web/logging/WebRequestTrace":{"module":"web","name":"dev/codex/schubert/nk/web/logging/WebRequestTrace","sha256":"e913d995a5cd7443c96fede3171b2cc241b5340f952532c382e5246180382ad1"},"dev/codex/schubert/nk/web/logging/WebRequestRouteInterceptor":{"module":"web","name":"dev/codex/schubert/nk/web/logging/WebRequestRouteInterceptor","sha256":"cca61d521d8e4bf246f63e0821aa5a134d853f2240161707d947cf9f4071878f"},"dev/codex/schubert/nk/web/config/RequestLogMvcConfiguration":{"module":"web","name":"dev/codex/schubert/nk/web/config/RequestLogMvcConfiguration","sha256":"a07d0f37eaca52eb2037816617c9a9d4fab82386ddb67af1310f9208291c3238"},"dev/codex/schubert/nk/web/security/WebRequestContext":{"module":"web","name":"dev/codex/schubert/nk/web/security/WebRequestContext","sha256":"b14439675537e10360d052246415ed3addcb68a757a78452d3127af767f6c9eb"}}
CLOSURES={n:([n,n+'$Scope'] if n.endswith('/WebRequestTrace') else [n]) for n in MAIN_UNITS}
METADATA=set()
UNEXECUTED=set()
COUNTS={'WebRequestTraceTest':10}
SESSION='PG16492-WEB-REQUEST-TRACE-ORIGINAL-TEN'
ROOT=data.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
TEST_PINS={'WebRequestTraceTest':'77a76f532dca84015b825dcb6e280a13e3b435a3dc07380efe81cd572ae44e19'}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PUBLIC_READS={"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/config/WebMvcConfiguration.java":"72ac4fcc161a85182e17d6167640cb18c93faed174fdd142225eaf1d84912d30","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/AnimationController.java":"e300e90c29d74117905de30f3e64dc99b5044a6bc5100648cdc1d5c2dc987e12","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/ContentDetailController.java":"2105ba833b33c91ac13129f4bae373a390f2e691115c7b08dc4ac64a5a543fc3","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/ErrorController.java":"ccc4587c76195542436f708aa6f87ee93b2d32e14d3d81350417c3f4e7b07fd5","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/LogController.java":"918e32335e79eb0f7d093e4fdb3c08f093d92ecfcfcaa8d853caf3ee53d41eb7","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/LoginController.java":"ef9bbc81c79799528840f70f65f55056d08fd1ea0f9fd1a93d8212b946f4e630","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/LogoutController.java":"93f164a1a35e675de653bf1d2638647482cc21332a8dca7bf2b72d8cf321e0f3","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/MediaController.java":"e3d5ab3db698c38d1b825a09b5197dea8e490ef6bef1cc1f8a394b658b081d34","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/MenuController.java":"b8fc0125b76a6f02f9d262e24f2636c61a20605668edcaefad389ad1e8f7a1f0","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/MusicController.java":"43714d9f59017f118ec095eacedc852b8b850a7282ce5df0847db70405a973f9","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/NotificationController.java":"24483e135ee03f1a9c6bb3bfe8736c60f646d6fa3e1a418d0d932cb072c90ac9","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/QuestionController.java":"b638c01e7c6a4992be893928ffc191cdc1f92220a7918bb4bd1c9552e18bdd33","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/ScenarioController.java":"f0ad9e4805f46f1ac0dca0d3fee940eda4a060bb540ba16d71748406b40335b2","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller/UserAdminController.java":"3cca5368ead598ac9ae648891702ff818aac1d77b464b3cb9a92299c24648cb3"}
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
def owned_step(name,command):
    if name=='selected-junit':
        command=list(command);command.insert(1,'-Dnk.pt.repository='+str(COMPILE/'snapshot'))
        assert all(run.host.sha(COMPILE/'snapshot'/p)==h for p,h in PUBLIC_READS.items())
    result=environmental_step(name,command)
    if name=='selected-junit' and result['actualExit']==0:
        assert all(run.host.sha(COMPILE/'snapshot'/p)==h for p,h in PUBLIC_READS.items())
        result['publicSourceReadHashes']=PUBLIC_READS
    return result
if __name__=='__main__':
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16492-web-request-trace-original-ten-pt-v1';run.OUT=data.BASE/'PG16492-web-request-trace-original-ten-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/WebRequestTraceTenCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['WebRequestTraceTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.FIXTURES,run.COUNTS={},COUNTS;run.EXTRA_TEST_SOURCES=(REPORTER,);run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    previous=data.read_checked(data.BASE/'PG16482-current2226-batch-enum-registry-v1/manifest.json','71620afa247589ff1dc183dc822d7d0ab562eac1f47794b540a44cc37fcfa8f1')
    assert normal['source']==previous['source']==SOURCE
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));text=path.read_text()
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==TEST_PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.web.logging.WebRequestTraceTest' not in previous['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','ProcessBuilder','DriverManager','HttpClient','KeyStore','java.sql','RootStartupContext','RootFailedStartRecovery','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec'])
    assert len(PUBLIC_READS)==14 and all(normal['begin']['inputHashes'][p]==h for p,h in PUBLIC_READS.items())
    assert set(MAIN_UNITS)-previous['fullSourceUnits'].keys()=={n for n in MAIN_UNITS if not n.endswith('/WebRequestContext')}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert normal['begin']['inputHashes'][path]==run.host.sha(data.ROOT/path)==row['sha256']
        with zipfile.ZipFile(normal['jars']['web']['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    run.step=owned_step;run.main()
