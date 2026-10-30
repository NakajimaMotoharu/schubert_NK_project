"""Original pure authorization matrix2; synthetic actor values only, no authentication or database."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'AuthorizationServiceTest':2}
SESSION='PG15390-ORIGINAL-AUTHORIZATION2'
ROOT=data.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={"AuthorizationServiceTest":"f290e044393ebbdd7778fdf474aaff8a211987c8f9c7686cba60591ef1aa465b"}
MAIN_PINS={"AuthorizationService":"8aa174fe39b5d71afe07443beb133063418edd1de095c16b3e288ac26d1faebb","AuthorizationException":"d380238db3295ef027da57f23eb88cc7ade4c319aefe5f73d7bd71392bce4ffa","AuthenticatedActor":"830a87635d2782354fe9c03e5d7612a2ab88364cdc31157b501fbf7baf361469"}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15390-pure-authorization-two-pt-v1';run.OUT=data.BASE/'PG15390-pure-authorization-two-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalAuthorizationMatrixJunitLauncher.java';run.NEW_TEST=TESTS['AuthorizationServiceTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='AuthorizationServiceTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG15374-current1795-time-login-registry-v1/manifest.json','d245e0fbad5b2b3436b4d2338e82318352ffd0e457190aaccd33fc98f1218f17')
    assert not {'dev.codex.schubert.nk.api.security.'+name for name in COUNTS}&set(registry['suiteNames'])
    prefix='dev/codex/schubert/nk/api/security/'
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for name,pin in MAIN_PINS.items():
            target=prefix+name;main='src/schubert-nk-api/src/main/java/'+target+'.java'
            assert target not in registry['fullSourceUnits']
            assert normal['begin']['inputHashes'][main]==run.host.sha(data.ROOT/main)==run.host.sha(COMPILE/'snapshot'/main)==pin
            assert {p[:-6] for p in jar.namelist() if p==target+'.class' or p.startswith(target+'$') and p.endswith('.class')}=={target}
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert len(re.findall(r'@Test\b',text))==COUNTS[name]
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','FileSystems.','getFileStore(','Linux','getenv(','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','HttpClient','Clock.system','TemporaryInfrastructureException','getSuppressed(','@BeforeAll','@BeforeEach','@TempDir','getConnection(','DataSource','PreparedStatement','.production('])
        assert not re.search(r'\.\s*(?:gc|setVerbose|dumpHeap)\s*\(',text)
        assert not re.search(r'(?<![A-Za-z0-9_])Files\s*\.',text)
        assert '"dev.codex.schubert.nk.api.security.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
        assert 'new ApiProcessMain(' not in text and '.run(' not in text and '.main(' not in text
    run.step=environmental_step;run.main()
