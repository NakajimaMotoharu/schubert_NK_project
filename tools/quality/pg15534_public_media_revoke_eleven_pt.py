"""Whole original media4/revocation7; public synthetic crypto and pure wire bytes only."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/web/'
MAIN_PINS={"media/MediaResponseDecoder":"2eea32c993a8aa57d4b21c31382e73078459b7a4097249e7a540a4fafc5e7c5f","media/MediaDeliveryException":"1b67c19a97f0cd35f193bc38ad1e155a4691f54ce6ad0c58d9bb37728cc77585","revocation/RevocationPayloadCodec":"c4e3c4ef95af5a79241392a21bd360f82b86d591335dce8ceda9c762bb6e1786","revocation/RevocationPayloadIdentity":"ee2a5de2420d9fd0f73919a78de9a6b5cbfd8fa13836100f234bb33cc85b1252","revocation/EncryptedRevocationPayload":"cef3f699c0f4b9eb8d562ed2c131c8c23e389808d0e8fd08bc33144b0aa55d94","revocation/RevocationPayloadException":"b348ae32f6c4294a3e708b590fe46499386a0f1b516f7171d45574edc050ecf0"}
DECLARED={"media/MediaResponseDecoderTest":["8926c5cf8508861e8e41a44ef9ab90b3c03fdbebd8362c7a937caf26a9e0ac21",4],"revocation/RevocationPayloadCodecTest":["6baaa1a06d02a069dd6117d8d6722e414ef738665742cb12a2f192bdd6212ba2",7]}
ROOT=run.host.ROOT/'src/schubert-nk-web/src/test/java'/PREFIX
TESTS={p.rpartition('/')[2]:ROOT/(p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
FIXTURES={}
SESSION='PG15534-PUBLIC-MEDIA-REVOKE-CURRENT-WHOLE11'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15534-public-media-revoke-eleven-pt-v1';run.OUT=run.host.BASE/'PG15534-public-media-revoke-eleven-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/PublicMediaRevokeCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['RevocationPayloadCodecTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={name:path for name,path in TESTS.items() if name!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='8f3202e58f28f64d99047476721b0f9600b7399ad515a59357c3da15eda63de5'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15524-current1850-synthetic-jms-guard-registry-v1/manifest.json','56979288ade5f3ab2f215677d826e0fcc706bbd72dcb24b760c03907a3ae2913')
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
            expected={name,*[name+'$'+n for n in ({'media/MediaResponseDecoder':['Binding','Result'],'media/MediaDeliveryException':['Reason'],'revocation/RevocationPayloadException':['Reason']}.get(short,[]))]}
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}==expected
    run.step=environmental_step;run.main()
