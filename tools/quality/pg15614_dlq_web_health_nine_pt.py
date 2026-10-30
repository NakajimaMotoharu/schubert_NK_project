"""Whole DLQ3/health4/admission-valve2; Proxy JMS and unstarted Tomcat values, no services."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/'
MAIN_PINS={"api/messaging/outbound/FatalDlqMessageWriter":"a1ae6af67703defb14f811b91e1b872c1d6ad2442d2fac8d758d18b39d661095","api/messaging/outbound/FatalDlqMetadata":"ecb1f660cd83fbc28c7133e38f1ea1a67ef47f7bf46085e220b810047d963efc","web/bootstrap/WebRuntimeHealth":"5afec3b52675a18c3d34b676b0d3313dc42b58e7b7377b0658524530b675f5a9","web/bootstrap/WebHttpAdmissionValve":"8318b77646af9bbbee9e3a839c6f850548eef82999b640cbc274b61b83a5606f","web/bootstrap/WebHttpAdmission":"dd0cda3ed6582fed7cd1d05ce1505d8b4bbfa77eb2984cd275b7c585e57ee130"}
CLOSURES={"api/messaging/outbound/FatalDlqMessageWriter":["api/messaging/outbound/FatalDlqMessageWriter"],"api/messaging/outbound/FatalDlqMetadata":["api/messaging/outbound/FatalDlqMetadata","api/messaging/outbound/FatalDlqMetadata$DetectedBy"],"web/bootstrap/WebRuntimeHealth":["web/bootstrap/WebRuntimeHealth"],"web/bootstrap/WebHttpAdmissionValve":["web/bootstrap/WebHttpAdmissionValve","web/bootstrap/WebHttpAdmissionValve$Lease"],"web/bootstrap/WebHttpAdmission":["web/bootstrap/WebHttpAdmission"]}
DECLARED={"api/messaging/outbound/FatalDlqMessageWriterTest":["2180953b5187548b68c906ee04057d4f479a140682a84d2e19f426767f4df88d",3],"web/bootstrap/WebRuntimeHealthTest":["385348477db8c3f4a5966f049aee3fba659923b6cf872f4df00d5f52d6c86683",4],"web/bootstrap/WebHttpAdmissionValveTest":["335a66156b4982a84333d3f0c6d97b72a065f7aca36dc53c16af8597f248a3f4",2]}
ROOT=run.host.ROOT
TESTS={p.rpartition('/')[2]:ROOT/('src/schubert-nk-'+p.partition('/')[0]+'/src/test/java/'+PREFIX+p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
FIXTURES={}
SESSION='PG15614-DLQ-WEB-HEALTH-CURRENT-WHOLE9'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15614-dlq-web-health-nine-pt-v1';run.OUT=run.host.BASE/'PG15614-dlq-web-health-nine-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/DlqWebHealthCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['FatalDlqMessageWriterTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={name:path for name,path in TESTS.items() if name!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='172d74509865871e558e6a08476fb8920f25bb7f1590803f00e925c782187380'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15604-current1903-checksum-capacity-registry-v1/manifest.json','eb3aa009a2892cffbac916a23e6dbd5c4d59b1a98476007dcbe2046e98088d72')
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
        assert ('dev.codex.schubert.nk.'+next(p for p in DECLARED if p.endswith('/'+name)).replace('/','.')) not in current['suiteNames']
    for short,pin in MAIN_PINS.items():
        mod=short.partition('/')[0];name=PREFIX+short;path='src/schubert-nk-'+mod+'/src/main/java/'+name+'.java'
        assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
        with zipfile.ZipFile(normal['jars'][mod]['path']) as jar:
            expected={PREFIX+p for p in CLOSURES[short]}
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}==expected
    run.step=environmental_step;run.main()
