"""Original whole Scenario reader4; public own TempDir/hash oracle only, no live file store."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/web/'
MAIN_PINS={'storage/ScenarioRecordReader':'39d4882340526f647f73b93669b45fc2e6570be220c23bd5aaf45a3012c1b359','storage/FileIntegrityException':'0ae4adadc3ba54aa98aa352a39a174a9b776e8240f442d7f1f43704e394a4854'}
CLOSURES={k:[k] for k in MAIN_PINS}
DECLARED={'storage/ScenarioRecordReaderTest':['34211a24be4ae7bc625c3ee4270a0cc359daf2ae6aea0627deaf39c1d9fe0626',4]}
ROOT=run.host.ROOT/'src/schubert-nk-web/src/test/java'/PREFIX
TESTS={p.rpartition('/')[2]:ROOT/(p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
FIXTURES={}
FIXTURE_SOURCE=ROOT/'storage/ScenarioFileFixture.java'
FIXTURE_SOURCE_SHA='bab03337af5d15eb5b1ec8855dac3816043a3b22788ed152a5a34fc85ea59b80'
SESSION='PG15854-SCENARIO-RECORD-READER-WHOLE4'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15854-scenario-record-reader-four-pt-v1';run.OUT=run.host.BASE/'PG15854-scenario-record-reader-four-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ScenarioRecordReaderFourJunitLauncher.java'
    run.NEW_TEST=TESTS['ScenarioRecordReaderTest'];run.TEST_ROOT=ROOT/'storage'
    run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,FIXTURE_SOURCE);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='3d39aa47b83177ed8e7bcd21812a08be6b2c60b8ae9ae926f6da86bdaba8cfc8'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15826-current2043-generated-values-registry-v1/manifest.json','dc8e5ea4115e406ef4951c060586261fce5e189fb92a65c694b2daca56199f85')
    assert current['postDisclosureCorrections']['22f14eebdb3284e51c67d9b05b4ee8eaf4b01784006a76cae6d73b071c98bcb3']['effectiveDisclosure']['effectiveCryptoOrKeyOperationsInvoked'] is True
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(run.host.ROOT))
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'(?m)^  void [A-Za-z0-9_]+\(',text))==COUNTS[name]
        assert '@TempDir Path root;' in text and 'root.resolve(' in text and 'new int[] {1, 201, 10000}' in text
        assert ('dev.codex.schubert.nk.web.storage.'+name) not in current['suiteNames']
        assert not any(v in text for v in ['ProcessBuilder','DriverManager','System.getenv(','getConnection(','TemporaryInfrastructureException','WebStartupException','Class.forName(','HttpClient','Tomcat','createConnection(','createContext(','configureOwned(','.production('])
    relative=str(FIXTURE_SOURCE.relative_to(run.host.ROOT))
    assert run.host.sha(FIXTURE_SOURCE)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==FIXTURE_SOURCE_SHA
    assert 'PayloadCodec' not in FIXTURE_SOURCE.read_text() and 'MessageDigest.getInstance("SHA-256")' in FIXTURE_SOURCE.read_text()
    with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
        for short,pin in MAIN_PINS.items():
            name=PREFIX+short;path='src/schubert-nk-web/src/main/java/'+name+'.java'
            assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}=={name}
    for name in ['dev/codex/schubert/nk/protocol/codec/PayloadCodec','dev/codex/schubert/nk/protocol/layout/PayloadSemanticValidator','dev/codex/schubert/nk/protocol/layout/scenario/ScenarioEntryRecord','dev/codex/schubert/nk/protocol/file/LargeResultDescriptor']:
        assert name in current['fullSourceUnits']
    run.step=environmental_step;run.main()
