"""Whole original injected receipt recovery4 and fixed exception values1, without crypto or DB."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/api/'
MAIN_PINS={"idempotency/ResponseSnapshotException":"89e48100d374c9eb0e0b30381d8ea832e48114c86ce65a4dba734cbaefe8b703"}
CLOSURES={"idempotency/ResponseSnapshotException":["idempotency/ResponseSnapshotException","idempotency/ResponseSnapshotException$Reason"]}
DECLARED={"application/question/QuestionReceiptRecoveryTest":["f6fd94a5aa4d26042cd1f8a83e0bec1db3ff986b2c6da6751c1ff12a5565b830",4],"idempotency/ExceptionValueContractTest":["68a6c832c062ab23915a056fa0e71c7c10eff0b02857e21a88cfdb2a15d3ac85",1]}
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java'/PREFIX
TESTS={p.rpartition('/')[2]:ROOT/(p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
FIXTURES={}
SUPPORT_PINS={"application/question/QuestionReceiptIdGenerator":"a4cb4c03f5dbdb225632d6abf4c2465fbb414ce09b0894f0b6649c83c7bc145d","application/question/QuestionReceiptId":"32e2d84c19a05c4655c6911e0b27374c13fb6b4d3ef09ead40e60877305d5d2f","idempotency/InboxException":"3d5cf68d628c17ccdb489e1c5199d43b144562d4b96df544580f7013eb1a680b"}
SESSION='PG15726-RECEIPT-RECOVERY-EXCEPTION-WHOLE5'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15726-receipt-recovery-exception-five-pt-v1';run.OUT=run.host.BASE/'PG15726-receipt-recovery-exception-five-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ReceiptRecoveryExceptionJunitLauncher.java'
    run.NEW_TEST=TESTS['QuestionReceiptRecoveryTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={name:path for name,path in TESTS.items() if name!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='8760c7e00b0e29d08ab9134c94e8d0d921ab644ab1f94918106f5e1ad9abf7cb'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15716-current2004-caddy-values-registry-v1/manifest.json','303896c2bf9a0738a00a8c3af8a23d23387dd7d31c1852593009fd609a45ba5d')
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
        assert ('dev.codex.schubert.nk.api.'+next(p for p in DECLARED if p.endswith('/'+name)).replace('/','.')) not in current['suiteNames']
    for short,pin in SUPPORT_PINS.items():
        name=PREFIX+short;path='src/schubert-nk-api/src/main/java/'+name+'.java'
        assert name in current['fullSourceUnits'] and current['fullSourceUnits'][name]['four100'] is True
        assert normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for short,pin in MAIN_PINS.items():
            name=PREFIX+short;path='src/schubert-nk-api/src/main/java/'+name+'.java'
            assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
            expected={PREFIX+p for p in CLOSURES[short]}
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}==expected
    run.step=environmental_step;run.main()
