"""Original Web inputs4 and MockMvc login4; nonsecret digest plus immutable packaged template only."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/web/'
MAIN_PINS={"controller/LoginController":"ef9bbc81c79799528840f70f65f55056d08fd1ea0f9fd1a93d8212b946f4e630","bootstrap/WebStartupInputs":"aacdcad0881ad85dee12ca67a92396bcfa4f0aefd91e24c033d7e46d1f840042"}
DECLARED={"controller/LoginControllerTest":["5255b728adf851b400649c9f0e9e107d9b8059df4e7a656cbbc6470c01e80a4d",4],"bootstrap/WebStartupInputsTest":["4994569f2e6c1dd29ceff084562a25818294e11be3c41bec23cb938422d84d18",4]}
ROOT=run.host.ROOT/'src/schubert-nk-web/src/test/java'/PREFIX
TESTS={p.rpartition('/')[2]:ROOT/(p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
FIXTURES={}
SESSION='PG15486-WEB-INPUTS-MOCKLOGIN-CURRENT-WHOLE8'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
RESOURCE='src/schubert-nk-web/src/main/resources/templates/login.html'
RESOURCE_PIN='ba814efffec4be98d17338cacd63927d50aa552958188ba3fb7db0b77171443a'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15486-web-inputs-mocklogin-eight-pt-v1';run.OUT=run.host.BASE/'PG15486-web-inputs-mocklogin-eight-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/WebInputsMockLoginCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['WebStartupInputsTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={name:path for name,path in TESTS.items() if name!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='e8ff7fa75cabf4ce3a0040de3feda3039ded04c2745ddeda456a840e4f3d4d54'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15478-current1831-disclosure-registry-v1/manifest.json','1f43f440ac2346b0a6d85fd615902197408fbeceba6a7cf7e79a2bca6d083c59')
    assert current['postDisclosureCorrections']['22f14eebdb3284e51c67d9b05b4ee8eaf4b01784006a76cae6d73b071c98bcb3']['effectiveDisclosure']['effectiveCryptoOrKeyOperationsInvoked'] is True
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(run.host.ROOT))
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'(?m)^  void [A-Za-z0-9_]+\(',text))==COUNTS[name]
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','System.getenv(','getConnection(','TemporaryInfrastructureException','WebStartupException','Class.forName(','HttpClient','Tomcat','ActiveMQ','.production('])
        assert ('dev.codex.schubert.nk.web.'+next(p for p in DECLARED if p.endswith('/'+name)).replace('/','.')) not in current['suiteNames']
    assert all(v in TESTS['LoginControllerTest'].read_text() for v in ['MockMvcBuilders.webAppContextSetup(context)','context.register(WebMvcConfiguration.class)','new MockServletContext()','new DefaultCsrfToken(','"safe-fixture-csrf"','assertEquals("schubert NK - ログイン", document.title())'])
    with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
        for short,pin in MAIN_PINS.items():
            name=PREFIX+short;path='src/schubert-nk-web/src/main/java/'+name+'.java'
            assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
            expected={name,name+'$Values'} if short=='bootstrap/WebStartupInputs' else {name}
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}==expected
        assert data.sha(jar.read('templates/login.html'))==normal['begin']['inputHashes'][RESOURCE]==run.host.sha(run.host.ROOT/RESOURCE)==RESOURCE_PIN
    run.step=environmental_step;run.main()
