"""Three whole existing binding suites10; unchanged original static fixtures, no keyring or query."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/api/'
MAIN_PINS={"application/media/MediaRequest":"73abe09934880c7aaae1d0db57c471788fc9d988c77791d7c876d8567b0cb55a","application/scenario/ScenarioRequest":"5530667c85ed9345fbe13aa3c89eef8a3fd51a38b019e8b52f4aea13e818fa5a"}
CLOSURES={"application/media/MediaRequest":["application/media/MediaRequest","application/media/MediaRequest$Kind"],"application/scenario/ScenarioRequest":["application/scenario/ScenarioRequest","application/scenario/ScenarioRequest$Kind"]}
DECLARED={"application/media/MediaRequestDescriptorBindingTest":["21b6d6830f46eb260d7b64b01b2b8863e913bbe9115049dd6c12fbb648b49a1b",4],"application/scenario/ScenarioScriptFileBindingTest":["a7fe439fdbcab85e7d783ce4904cc32d2c5f1ba90111909720cf118972ce9706",2],"application/question/QuestionQueryResponseBindingTest":["9b04113db75e98c0ecbaccd5e5b10987c93036b4183ebf7dc223a8cf35ab5205",4]}
HELPER_PINS={"application/media/MediaRequestFixture":"4f1fb62819c2a7ea91d5c0d3706f3d78415fdc4bd2259b74d87bc89274a25dc8","application/scenario/ScenarioRequestFixture":"59b79a09aa45f9878e551e4f7943c9f88b597b1f5976f46daa038a9811ae23f8","application/question/QuestionQueryRequestTest":"9388f89830fff72af50ca24c30ed9508d1e417d836819755f42580d9131ff953"}
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java'/PREFIX
TESTS={p.rpartition('/')[2]:ROOT/(p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
FIXTURES={}
SESSION='PG15662-REQUEST-BINDINGS-CURRENT-WHOLE10'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15662-request-bindings-ten-pt-v1';run.OUT=run.host.BASE/'PG15662-request-bindings-ten-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/RequestBindingsCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MediaRequestDescriptorBindingTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={name:path for name,path in TESTS.items() if name!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,*[ROOT/(p+'.java') for p in HELPER_PINS]);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='5e09ecd93b29eecda44f1859e594609d87dc247d2ab2d2d769af9d6fde611fb7'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15652-current1950-lgs-reply-registry-v1/manifest.json','a7f69e546495618e04fb9df177da6fd70e6571262d3920f4b93186c47373dd2c')
    assert current['postDisclosureCorrections']['22f14eebdb3284e51c67d9b05b4ee8eaf4b01784006a76cae6d73b071c98bcb3']['effectiveDisclosure']['effectiveCryptoOrKeyOperationsInvoked'] is True
    def files_operation(text):return re.search(r'(?<![A-Za-z0-9_$])Files\s*\.',text) is not None
    assert not files_operation('ServiceConfigFiles.Service.WEB')
    assert not files_operation('ServiceConfigFiles.Contents values')
    assert all(files_operation(v) for v in ['Files.readString(path)','java.nio.file.Files.readAllBytes(path)','Files \n .readString(path)'])
    for name,pin in HELPER_PINS.items():
        path=ROOT/(name+'.java');relative=str(path.relative_to(run.host.ROOT))
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==pin
    helper=current['fullSourceUnits'][PREFIX+'application/question/QuestionQueryRequest']
    assert helper['post']=='PG14762-question-sql-joint-eighteen-post-v1' and helper['four100'] is True
    assert 'QuestionQueryRequestTest' not in COUNTS
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(run.host.ROOT))
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'(?m)^  void [A-Za-z0-9_]+\(',text))==COUNTS[name]
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','System.getenv(','getConnection(','TemporaryInfrastructureException','WebStartupException','Class.forName(','HttpClient','Tomcat','createConnection(','createContext(','createRetainingUnknown(','configureOwned(','.production('])
        assert not files_operation(text)
        assert ('dev.codex.schubert.nk.api.'+next(p for p in DECLARED if p.endswith('/'+name)).replace('/','.')) not in current['suiteNames']
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for short,pin in MAIN_PINS.items():
            name=PREFIX+short;path='src/schubert-nk-api/src/main/java/'+name+'.java'
            assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
            expected={PREFIX+p for p in CLOSURES[short]}
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}==expected
    run.step=environmental_step;run.main()
