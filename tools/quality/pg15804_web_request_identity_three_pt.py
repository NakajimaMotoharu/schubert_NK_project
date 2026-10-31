"""Whole original mock request identity3, fixed public UUIDs and numeric IPs, no real HTTP."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/web/'
MAIN_PINS={"security/WebRequestContext":"b14439675537e10360d052246415ed3addcb68a757a78452d3127af767f6c9eb","security/CaddyTransportContextFilter":"3fa8bd5ce5e2af1341085c78fb909041951bd82c17c094377da6dcb66765c1b1","security/CaddyClientAddressResolver":"f5b117c9d9a9473a45b602c3ce97a6e92198b27490ac284e7281956cd7b42f37","logging/WebSecurityAudit":"ce6fc0f8c9031c15077b7fd929837641e38fd9ac5b33683468e63224d53cd1f3"}
CLOSURES={"security/WebRequestContext":["security/WebRequestContext"],"security/CaddyTransportContextFilter":["security/CaddyTransportContextFilter"],"security/CaddyClientAddressResolver":["security/CaddyClientAddressResolver"],"logging/WebSecurityAudit":["logging/WebSecurityAudit","logging/WebSecurityAudit$Event","logging/WebSecurityAudit$Route"]}
DECLARED={"security/WebRequestIdentityConsistencyTest":["08d59588104456e4f6b20f35166c9b8e899ae12cb08031ff2bffd5a70f419864",3]}
ROOT=run.host.ROOT/'src/schubert-nk-web/src/test/java'/PREFIX
TESTS={p.rpartition('/')[2]:ROOT/(p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
FIXTURES={}
SUPPORT_PINS={"security/LoginClientAddress":"4e6cfb538744d81daf4c5e132b729b6800b1ee3f3aa6682ad06e46c9aabb56c5"}
SESSION='PG15804-WEB-REQUEST-IDENTITY-WHOLE3'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15804-web-request-identity-three-pt-v1';run.OUT=run.host.BASE/'PG15804-web-request-identity-three-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/WebRequestIdentityThreeJunitLauncher.java'
    run.NEW_TEST=TESTS['WebRequestIdentityConsistencyTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={name:path for name,path in TESTS.items() if name!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='e48b0abf902fa9090bcf05ec464d225162157124207b9207d154d75bed6fe9e7'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15794-current2028-acceptor-json-registry-v1/manifest.json','d1484938af6778e1d3e019eb792de2d60d094ef56c10f56c425788a80f4396b3')
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
    for short,pin in SUPPORT_PINS.items():
        name=PREFIX+short;path='src/schubert-nk-web/src/main/java/'+name+'.java'
        assert name in current['fullSourceUnits'] and (current['fullSourceUnits'][name]['four100'] is True or current['fullSourceUnits'][name]['branchNaturallyZero'] is True)
        assert normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
    with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
        for short,pin in MAIN_PINS.items():
            name=PREFIX+short;path='src/schubert-nk-web/src/main/java/'+name+'.java'
            assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
            expected={PREFIX+p for p in CLOSURES[short]}
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}==expected
    run.step=environmental_step;run.main()
