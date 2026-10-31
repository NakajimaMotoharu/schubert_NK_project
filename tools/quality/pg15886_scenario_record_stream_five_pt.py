"""Original whole Scenario stream5; public own TempDir and independent full-byte/hash oracle."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/api/'
MAIN_PINS={'storage/ScenarioRecordStream':'c86d8e01903b09c050187c4da462e82279b86eb638d8a2e1f12ecbc09b80f2ae'}
CLOSURES={'storage/ScenarioRecordStream':['storage/ScenarioRecordStream']}
DECLARED={'storage/ScenarioRecordStreamTest':['dab5445d8223665deb56954dc6b27e75898b06d34cea9e63da478c2e7ee2cd7a',5]}
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java'/PREFIX
TESTS={p.rpartition('/')[2]:ROOT/(p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
FIXTURES={}
SESSION='PG15886-SCENARIO-RECORD-STREAM-WHOLE5'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15886-scenario-record-stream-five-pt-v1';run.OUT=run.host.BASE/'PG15886-scenario-record-stream-five-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ScenarioRecordStreamFiveJunitLauncher.java'
    run.NEW_TEST=TESTS['ScenarioRecordStreamTest'];run.TEST_ROOT=ROOT/'storage'
    run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='da50959cfc5618f5dc228eb280ba618be3a29138dd84d330bb2c9d2dfadc421d'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15876-current2055-maintenance-records-registry-v1/manifest.json','e297179a1c121c3842432940be4f8a85d35de820c379fef7cf3661af79aa4389')
    assert current['postDisclosureCorrections']['22f14eebdb3284e51c67d9b05b4ee8eaf4b01784006a76cae6d73b071c98bcb3']['effectiveDisclosure']['effectiveCryptoOrKeyOperationsInvoked'] is True
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(run.host.ROOT))
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'(?m)^  void [A-Za-z0-9_]+\(',text))==COUNTS[name]
        assert '@TempDir Path root;' in text and 'new int[] {1, 201, 10000}' in text and 'Executors.newFixedThreadPool(8)' in text and 'i < 16' in text
        assert ('dev.codex.schubert.nk.api.storage.'+name) not in current['suiteNames']
        assert not any(v in text for v in ['ProcessBuilder','DriverManager','System.getenv(','getConnection(','TemporaryInfrastructureException','WebStartupException','Class.forName(','HttpClient','Tomcat','createConnection(','createContext(','configureOwned(','.production('])
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for short,pin in MAIN_PINS.items():
            name=PREFIX+short;path='src/schubert-nk-api/src/main/java/'+name+'.java'
            assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}=={PREFIX+v for v in CLOSURES[short]}
    for name in ['dev/codex/schubert/nk/protocol/codec/PayloadCodec','dev/codex/schubert/nk/protocol/layout/PayloadSemanticValidator','dev/codex/schubert/nk/protocol/layout/scenario/ScenarioEntryRecord','dev/codex/schubert/nk/protocol/file/LargeResultContent','dev/codex/schubert/nk/storage/StorageIoException']:
        assert name in current['fullSourceUnits']
    run.step=environmental_step;run.main()
