"""Whole LGS8/reply decoder6; fake sender/Proxy JMS and destination values, no services."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/web/'
MAIN_PINS={"messaging/LogSearchWireClient":"4606ebc5e433903fa46f1a356d38368bb7ae4871efb4c30892932a560908154b","messaging/JmsReplyDecoder":"f6d03f1809ddd5d58df0c9a0b670be35e5884b8d10d30b42ada40a5f0285c78f","messaging/ValidatedReply":"5003b09aff1093dab0f672518d1962d5b2a9f0b95698d11d0295639ebe3b3a54"}
CLOSURES={"messaging/LogSearchWireClient":["messaging/LogSearchWireClient"],"messaging/JmsReplyDecoder":["messaging/JmsReplyDecoder"],"messaging/ValidatedReply":["messaging/ValidatedReply"]}
DECLARED={"messaging/LogSearchWireClientTest":["d4c586832cec19d3a7d896aa0ee6f316c3cab96af6a808d0b54f5cff8734729f",8],"messaging/JmsReplyDecoderTest":["4e57ec319666832fa7aaa8639bb44920c84969f13e59c8450706d63b9dcea05e",6]}
ROOT=run.host.ROOT/'src/schubert-nk-web/src/test/java'/PREFIX
TESTS={p.rpartition('/')[2]:ROOT/(p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
FIXTURES={}
SESSION='PG15646-LGS-REPLY-CURRENT-WHOLE14'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15646-lgs-reply-fourteen-pt-v1';run.OUT=run.host.BASE/'PG15646-lgs-reply-fourteen-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/LgsReplyCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['LogSearchWireClientTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={name:path for name,path in TESTS.items() if name!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='fad0f82a387c8729c582609173df0242cff0908fa30116f058ba6f334319c2aa'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15637-current1936-protected-facades-registry-v2/manifest.json','9fa92ea73d1b63854242560dcc2902a71f09fb4041bf8263fa9470ddd0c6c972')
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
