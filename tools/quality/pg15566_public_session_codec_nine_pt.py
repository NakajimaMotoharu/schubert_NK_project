"""Whole original session codec nine; unchanged JSON Test fixture helper compiled, not selected."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/web/'
MAIN_PINS={"session/SessionPayloadCodec":"9556be0630f6268cbe20da1d5f3ba37630376f653d954d90781c1ac69257f793","session/SessionPayloadIdentity":"f669b82c1ebce568c46198438b01ce65e9133eb1a50e7d94725ef060d3e1e25d","session/EncryptedSessionPayload":"b2d8816f5704d9d5d879908bf6ae5f4e95d436c1397b5e6ad71b78d09c45d799"}
HELPER_PINS={"session/SessionPayloadException":"93cef186b470be817f36dff0f390ee5b71a3f2b2a0299dac5c694e16b8bf374e","session/SessionAttributeCodec":"241ede8923818ae7690ad9dd09a5ea55df972c106ce4ae4f39cd27fc458e7314"}
DECLARED={"session/SessionPayloadCodecTest":["198d18af56d8c557d6c183c85829afe07d63956c3ff91a43f0a47c7ab1ff48f3",9]}
ROOT=run.host.ROOT/'src/schubert-nk-web/src/test/java'/PREFIX
TESTS={p.rpartition('/')[2]:ROOT/(p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
FIXTURES={}
SESSION='PG15566-PUBLIC-SESSION-CODEC-CURRENT-WHOLE9'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15566-public-session-codec-nine-pt-v1';run.OUT=run.host.BASE/'PG15566-public-session-codec-nine-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/PublicSessionCodecCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['SessionPayloadCodecTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={name:path for name,path in TESTS.items() if name!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,ROOT/'session/SessionAttributeCodecTest.java');run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='fa7cdb9d8a5cbfb1743b45ddee7208c1c88a3a893e5453b32a4a27734c34f8b1'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15556-current1870-public-weblog-codec-registry-v1/manifest.json','366596b4fb25238559e0f771eaf9760bc96a1fc85e70b8375d361da57a1182a3')
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
            expected={name}
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}==expected
    assert set(HELPER_PINS)=={'session/SessionPayloadException','session/SessionAttributeCodec'}
    for short,pin in HELPER_PINS.items():
        name=PREFIX+short;path='src/schubert-nk-web/src/main/java/'+name+'.java'
        assert name in current['fullSourceUnits'] and normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
    helper=ROOT/'session/SessionAttributeCodecTest.java';hp=str(helper.relative_to(run.host.ROOT))
    assert normal['begin']['inputHashes'][hp]==run.host.sha(helper)==run.host.sha(COMPILE/'snapshot'/hp)=='54c9a088ec519b70dd19ed4a6f88c2640c0fb5b410f12e16e554e2d0f9170b02'
    assert 'dev.codex.schubert.nk.web.session.SessionAttributeCodecTest' in current['suiteNames']
    assert not any(v in helper.read_text() for v in ['@BeforeAll','@BeforeEach','System.getenv(','ProcessBuilder','DriverManager'])
    run.step=environmental_step;run.main()
