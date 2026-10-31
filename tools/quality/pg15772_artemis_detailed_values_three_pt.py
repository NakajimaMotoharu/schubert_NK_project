"""Original whole Artemis detailed values3; injected readers, unused session proxy, no broker."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/batch/'
MAIN_PINS={'mq/ArtemisStartupObservation':'6b92bf3c97bb72a6b0222f35842e251a19bbaf13808a709f2d9c5b2e54207f78','mq/ArtemisManagementReadinessClient':'3eb82d01455cf8d2932baf0bc9ed57c2d843a5bd7e071cdc285958a370413f73','mq/ArtemisQueuePressureClient':'930b0bb1448eaa78c8fa2406a41a06f2b9d1c5cbf6c953b19ec570d1139d386f'}
CLOSURES={'mq/ArtemisStartupObservation':['mq/ArtemisStartupObservation','mq/ArtemisStartupObservation$Evidence'],'mq/ArtemisManagementReadinessClient':['mq/ArtemisManagementReadinessClient','mq/ArtemisManagementReadinessClient$Reader','mq/ArtemisManagementReadinessClient$OperationEncoder','mq/ArtemisManagementReadinessClient$OwnedOperation','mq/ArtemisManagementReadinessClient$MessageWriter','mq/ArtemisManagementReadinessClient$Exchange'],'mq/ArtemisQueuePressureClient':['mq/ArtemisQueuePressureClient','mq/ArtemisQueuePressureClient$Limits','mq/ArtemisQueuePressureClient$Pressure','mq/ArtemisQueuePressureClient$Value','mq/ArtemisQueuePressureClient$Reader']}
ROOT=run.host.ROOT/'src/schubert-nk-batch/src/test/java'/PREFIX
TESTS={'ArtemisDetailedValuesTest':ROOT/'mq/ArtemisDetailedValuesTest.java'}
COUNTS={'ArtemisDetailedValuesTest':3}
PINS={'ArtemisDetailedValuesTest':'bd3c44e8c9f98f2461c386883e1d8f358c1d6e87c99876e7f397abec09293107'}
FIXTURES={}
SUPPORT_PINS={}
SESSION='PG15772-ARTEMIS-DETAILED-VALUES-WHOLE3'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15772-artemis-detailed-values-three-pt-v1';run.OUT=run.host.BASE/'PG15772-artemis-detailed-values-three-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ArtemisDetailedValuesThreeJunitLauncher.java'
    run.NEW_TEST=TESTS['ArtemisDetailedValuesTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={};run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='234a4be0f412a0921f79366589596f31f6088b507549b84400453580090e8af9'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15762-current2023-mock-helper-registry-v1/manifest.json','8c2d3069736a32b9154f030a14f6ca8274e2f4059a3f5507f67f778cbd277bb8')
    path=run.NEW_TEST;text=path.read_text();relative=str(path.relative_to(run.host.ROOT))
    assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==PINS[path.stem]
    assert text.count('@Test')==len(re.findall(r'(?m)^  void [A-Za-z0-9_]+\(',text))==3
    assert not any(v in text for v in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','getConnection(','TemporaryInfrastructureException','WebStartupException','Class.forName(','HttpClient','createConnection(','createContext(','withParentDeadline(','new ArtemisStartupObservation('])
    assert 'borrowed session not needed by fixed reader fixture' in text and 'throw new AssertionError' in text
    assert 'dev.codex.schubert.nk.batch.mq.ArtemisDetailedValuesTest' not in current['suiteNames']
    with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
        for short,pin in MAIN_PINS.items():
            name=PREFIX+short;relative='src/schubert-nk-batch/src/main/java/'+name+'.java'
            assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][relative]==run.host.sha(run.host.ROOT/relative)==run.host.sha(COMPILE/'snapshot'/relative)==pin
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}=={PREFIX+p for p in CLOSURES[short]}
    run.step=environmental_step;run.main()
