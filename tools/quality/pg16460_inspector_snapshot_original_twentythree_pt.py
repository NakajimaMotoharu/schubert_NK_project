"""Original whole observation data23; memory reader and own scalar trace, no Root recovery."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME='dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='a69a3ab5d53aedde2982176c43bbec15e27358921cd4d5140e395fee228e8cd4')}
CLOSURES={NAME:[NAME,NAME+'$Target']}
METADATA=set()
UNEXECUTED=set()
COUNTS={'InspectorUnitSnapshotTest':10,'InspectorHeldStateContractTest':9,'ArtemisUnitSnapshotTest':4}
SESSION='PG16460-INSPECTOR-SNAPSHOT-ORIGINAL-TWENTYTHREE'
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
TEST_PINS={'InspectorUnitSnapshotTest':'edf0ce67d649d340e2e61907cc8228cd9c44fe08a21a9f011d81cdcbef4d1a63','InspectorHeldStateContractTest':'15f183d2a47186954381876bc2a8e9cbf9505c3bdda08f6e5dca242e608f6b66','ArtemisUnitSnapshotTest':'968b2e8371cd008c36729e251cc406eea6b48c305222b0dbeb8de8038a5bbcd0'}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
GOLDEN='src/schubert-nk-batch/src/test/resources/inspector/unit-golden.txt'
FIXTURES={GOLDEN:'2170fc2e71a4ba50519bc2f123d0bf75fcc46adab033645b7b68b5c513c345f6'}
PUBLIC_UNIT='src/deployment/systemd/artemis.service'
PUBLIC_UNIT_SHA='1b8fe8eaab683ac658bfe8c23816e709725431a0a2b80816bba5449d129c5266'
TRACE='target/inspector-unit-traces/PT-OPS-UNIT-001-state.txt'
EXPECTED_TRACE='quiescent=true\nreceipt=10\nsameInvocationReceipt=none\n'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
def owned_step(name,command):
    if name=='selected-junit':
        command=list(command);command.insert(1,'-Dnk.pt.repository='+str(COMPILE/'snapshot'))
        assert run.host.sha(COMPILE/'snapshot'/PUBLIC_UNIT)==PUBLIC_UNIT_SHA
    result=environmental_step(name,command)
    if name=='selected-junit' and result['actualExit']==0:
        path=run.SLOT/TRACE;assert path.is_file() and not path.is_symlink() and path.read_text()==EXPECTED_TRACE
        assert run.host.sha(COMPILE/'snapshot'/PUBLIC_UNIT)==PUBLIC_UNIT_SHA
        result['scalarTraceAtOwnedStageEnd']={TRACE:run.host.sha(path)}
        result['publicUnitTemplateRead']=dict(path=PUBLIC_UNIT,sha256=PUBLIC_UNIT_SHA,snapshot=str(COMPILE/'snapshot'))
    return result

if __name__=='__main__':
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16460-inspector-snapshot-original-twentythree-pt-v1';run.OUT=data.BASE/'PG16460-inspector-snapshot-original-twentythree-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/InspectorSnapshotTwentyThreeCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['InspectorUnitSnapshotTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.FIXTURES,run.COUNTS=FIXTURES,COUNTS;run.EXTRA_TEST_SOURCES=(REPORTER,);run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    previous=data.read_checked(data.BASE/'PG16450-current2201-config-resource-registry-v1/manifest.json','1a5c0cce5b094ca859c66e83d74987ed4c65ef8c5c6a1ff89c88bf379b05e9b5')
    assert normal['source']==previous['source']==SOURCE
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));text=path.read_text()
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==TEST_PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.platform.'+name not in previous['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','ProcessBuilder','DriverManager','HttpClient','KeyStore','java.sql','java.net.','RootStartupContext','RootFailedStartRecovery','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec','NativeReader.forTarget','new InspectorUnitProbe.NativeReader'])
    assert normal['begin']['inputHashes'][GOLDEN]==FIXTURES[GOLDEN] and normal['begin']['inputHashes'][PUBLIC_UNIT]==PUBLIC_UNIT_SHA
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert normal['begin']['inputHashes'][path]==run.host.sha(data.ROOT/path)==row['sha256']
        assert name not in previous['fullSourceUnits']
        with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    run.step=owned_step;run.main()
