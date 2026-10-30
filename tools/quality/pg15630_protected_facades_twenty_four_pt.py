"""Three whole facade originals24; in-memory sender/codec, public contexts, no actual JMS or auth."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/web/'
MAIN_PINS={"messaging/AnimationWireClient":"b329258fb34ba289506b9026f3852565b84de3591a6479889cb83b11ac280348","messaging/MusicWireClient":"f72dc90a27ee19b3e9f575a70702f1bc08d48f3bfc23eb13ddae888129080137","messaging/ScenarioWireClient":"7e3709a36bc952b9c0f3cefdeddc51eb43df92a77021848456b87578dbf75315"}
CLOSURES={"messaging/AnimationWireClient":["messaging/AnimationWireClient"],"messaging/MusicWireClient":["messaging/MusicWireClient"],"messaging/ScenarioWireClient":["messaging/ScenarioWireClient","messaging/ScenarioWireClient$Result"]}
DECLARED={"messaging/AnimationWireClientTest":["b0404e82cfcf5d9054c4f586c873b1e72a63b8d115f111b436235c12f7afe41c",8],"messaging/MusicWireClientTest":["218128c6532fed2727b9ba9d72fde5d1c28b18209e8d0d95b3694dc51f99939e",8],"messaging/ScenarioWireClientTest":["3266789f948395e10f7106980eb9113af280046184338aeb0cd37a96bf7cb0b8",8]}
ROOT=run.host.ROOT/'src/schubert-nk-web/src/test/java'/PREFIX
TESTS={p.rpartition('/')[2]:ROOT/(p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
FIXTURES={}
SESSION='PG15630-PROTECTED-FACADES-CURRENT-WHOLE24'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15630-protected-facades-twenty-four-pt-v1';run.OUT=run.host.BASE/'PG15630-protected-facades-twenty-four-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ProtectedFacadesCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['AnimationWireClientTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={name:path for name,path in TESTS.items() if name!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='796551c40fee59ada0652b91beb25f64291bb91cf6724314a7f94a616e910d22'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15620-current1912-dlq-web-health-registry-v1/manifest.json','60495269d8b2f1ef5e0096b18a30f22806dcd145c755624c27ad75455f4859ce')
    assert current['postDisclosureCorrections']['22f14eebdb3284e51c67d9b05b4ee8eaf4b01784006a76cae6d73b071c98bcb3']['effectiveDisclosure']['effectiveCryptoOrKeyOperationsInvoked'] is True
    def files_operation(text):return re.search(r'(?<![A-Za-z0-9_$])Files\s*\.',text) is not None
    assert not files_operation('ServiceConfigFiles.Service.WEB')
    assert not files_operation('ServiceConfigFiles.Contents values')
    assert all(files_operation(v) for v in ['Files.readString(path)','java.nio.file.Files.readAllBytes(path)','Files \n .readString(path)'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(run.host.ROOT))
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'(?m)^  void [A-Za-z0-9_]+\(',text))==COUNTS[name]
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','System.getenv(','getConnection(','TemporaryInfrastructureException','WebStartupException','Class.forName(','HttpClient','Tomcat','createConnection(','createContext(','createRetainingUnknown(','configureOwned(','.production('])
        assert not files_operation(text)
        assert ('dev.codex.schubert.nk.web.'+next(p for p in DECLARED if p.endswith('/'+name)).replace('/','.')) not in current['suiteNames']
    with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
        for short,pin in MAIN_PINS.items():
            name=PREFIX+short;path='src/schubert-nk-web/src/main/java/'+name+'.java'
            assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
            expected={PREFIX+p for p in CLOSURES[short]}
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}==expected
    run.step=environmental_step;run.main()
