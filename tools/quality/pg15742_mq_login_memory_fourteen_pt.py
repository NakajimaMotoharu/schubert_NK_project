"""Whole original memory Login Client6/Probe3/Provider5; no deployed credentials, broker or sessions."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/web/'
MAIN_PINS={"security/MqLoginClient":"9c654ea40f781e8600cfb6254cbb52f0ee0f2072261d145701fc721ca28a5a6c","security/MqLoginContextProbe":"65b26fb1ccb7aad49ce727aaa88d8f6af4f175de7e4c4afbe5fabbcff09ae45d","security/MqAuthenticationProvider":"95ba9e2b71c5b5288e9185d833897adf82949554374de6e5cced94c46b27b7b7","security/LoginClientAddress":"4e6cfb538744d81daf4c5e132b729b6800b1ee3f3aa6682ad06e46c9aabb56c5"}
CLOSURES={"security/MqLoginClient":["security/MqLoginClient","security/MqLoginClient$Reply"],"security/MqLoginContextProbe":["security/MqLoginContextProbe"],"security/MqAuthenticationProvider":["security/MqAuthenticationProvider"],"security/LoginClientAddress":["security/LoginClientAddress"]}
DECLARED={"security/MqLoginClientTest":["6b4e9b5d633652ae0e6aa7e2e141b5ea88bb333906f04d7d06728f0c9f649598",6],"security/MqLoginContextProbeTest":["94bd2c4d5bcc12870074f5907c03a7e21ef7b5a213cad94170a20e480d20434b",3],"security/MqAuthenticationProviderTest":["1102d1cdb41889da6e3476227970c3d01e2523be8603e6a9db83ad1cdc7adcad",5]}
ROOT=run.host.ROOT/'src/schubert-nk-web/src/test/java'/PREFIX
TESTS={p.rpartition('/')[2]:ROOT/(p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
FIXTURES={}
SUPPORT_PINS={"security/MqLoginExchangeException":"4f36806cd08ce5c3eb29d15694392b326da736f7e8f5e371552fe24988cd9684","security/MqLoginLockedException":"badfaf084badf1923f112e49a89aa2b7ce61712ae8d66e4e181231dd856b1c1b","messaging/JmsRequestReplyClient":"cc0689a25334f9b2eb12983e5e952a0a19af703c28ff4898ff8b57f2a6aa7b39","messaging/ReplyCorrelationRegistry":"1a28f9d8ec9438f13621358c02181557fdc3a19f4afd55303ad727ce6fc9ed75","messaging/PendingReply":"346a3d7ddf65889875a3f1907eda05fd061a4788aabf5d7361b461790185c42b"}
SESSION='PG15742-MQ-LOGIN-MEMORY-WHOLE14'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15742-mq-login-memory-fourteen-pt-v1';run.OUT=run.host.BASE/'PG15742-mq-login-memory-fourteen-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/MqLoginMemoryFourteenJunitLauncher.java'
    run.NEW_TEST=TESTS['MqLoginClientTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={name:path for name,path in TESTS.items() if name!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='20b7ca45ec183afdb288674b531a0c841517d01abcb9a1217e541883b964b274'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15732-current2009-recovery-values-registry-v1/manifest.json','66b317c50586b44e39d8a7b7e0f175184d151554c7e7d2c9bfb0d3650e6c7bfa')
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
