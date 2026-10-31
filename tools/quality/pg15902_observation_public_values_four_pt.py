"""Original public observation values4; five enclosing sources measured fully, outer operations never called."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
ROWS=[{"module":"batch","name":"dev/codex/schubert/nk/batch/file/RootServiceFacts","sha256":"35f12e3f827bafcc0283c6f3064a6ac8f6288475a003cf6ec4fcbc866a555f76","suffixes":["","$Facts"]},{"module":"batch","name":"dev/codex/schubert/nk/batch/file/MorningBrokerExecution","sha256":"b5d27b117ee2c6fb9de12cf90018f8594821ef6618f552a4c17908c88eaa1e1e","suffixes":["","$ExpectedCurrent","$Observations","$Completion"]},{"module":"batch","name":"dev/codex/schubert/nk/batch/platform/RootReleaseAdmission","sha256":"dcbcc5d7b7ee97d9fd5aa50118d0fe24353bf9af429ef33271962fafe5f17753","suffixes":["","$EffectiveConfigurations","$NativeOsIo","$DatabaseInspection","$OsIo","$Loader","$Platform"]},{"module":"batch","name":"dev/codex/schubert/nk/batch/platform/BrokerJournalEvidence","sha256":"18f067e88b43658b276d06a0ef889adde32d039a50e2b1ba8dd654488d2d70bb","suffixes":["","$Summary","$Anchor"]},{"module":"storage","name":"dev/codex/schubert/nk/storage/ServiceConfigFiles","sha256":"11b33bed1889750459c6e27c65a7cacd69c51c79f78cd85da252093c504912d6","suffixes":["","$NioIo","$Service","$Snapshot","$Io","$Contents"]}]
MAIN_UNITS={r['name']:r for r in ROWS}
CLOSURES={r['name']:[r['name']+suffix for suffix in r['suffixes']] for r in ROWS}
METADATA={'dev/codex/schubert/nk/batch/file/MorningBrokerExecution$ExpectedCurrent','dev/codex/schubert/nk/batch/platform/RootReleaseAdmission$Loader','dev/codex/schubert/nk/batch/platform/RootReleaseAdmission$Platform','dev/codex/schubert/nk/batch/platform/RootReleaseAdmission$OsIo','dev/codex/schubert/nk/storage/ServiceConfigFiles$Io'}
EXECUTED={'dev/codex/schubert/nk/batch/file/RootServiceFacts$Facts','dev/codex/schubert/nk/batch/file/MorningBrokerExecution$Observations','dev/codex/schubert/nk/batch/platform/RootReleaseAdmission$EffectiveConfigurations','dev/codex/schubert/nk/batch/platform/BrokerJournalEvidence$Summary','dev/codex/schubert/nk/storage/ServiceConfigFiles$Contents'}
UNEXECUTED={n for group in CLOSURES.values() for n in group}-METADATA-EXECUTED
TEST=run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/ObservationValueRedactionTest.java'
TEST_SHA='b0659ff613078fd893ca30bf263b3d372d99dde987f5475a14f84c409a76ee77'
TESTS={'ObservationValueRedactionTest':TEST}
COUNTS={'ObservationValueRedactionTest':4}
FIXTURES={}
SESSION='PG15902-OBSERVATION-PUBLIC-VALUES-WHOLE4'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15902-observation-public-values-four-pt-v1';run.OUT=run.host.BASE/'PG15902-observation-public-values-four-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ObservationValueRedactionFourJunitLauncher.java'
    run.NEW_TEST=TEST;run.TEST_ROOT=TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    reporter=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert reporter['actualExit']==reporter['productTestsExecuted']==0 and reporter['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==reporter['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='2fd3bf9562be4000094e1ee6d2f11d70dcfd15537997df3f3d6ef420ce2bbe5e'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15892-current2060-scenario-stream-registry-v1/manifest.json','c9edd9a200ac7e24583872ed715368439346d9cb5c0243722f164eba6bf60f49')
    relative=str(TEST.relative_to(data.ROOT));text=TEST.read_text()
    assert run.host.sha(TEST)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==TEST_SHA
    assert text.count('@Test')==len(re.findall(r'(?m)^  void [A-Za-z0-9_]+\(',text))==4
    assert 'dev.codex.schubert.nk.batch.file.ObservationValueRedactionTest' not in current['suiteNames']
    assert not re.search(r'(?<![A-Za-z0-9_$])Files\s*\.',text)
    assert not any(v in text for v in ['@BeforeAll','@BeforeEach','@TempDir','ProcessBuilder','DriverManager','System.getenv(','getConnection(','TemporaryInfrastructureException','WebStartupException','Class.forName(','HttpClient','.production(','.inspect(','.inspectServiceConfigurations(','.capture(','.create(','LinuxDirectoryCalls'])
    assert all(v in text for v in ['new ServiceConfigFiles.Contents(','new RootReleaseAdmission.EffectiveConfigurations(','new RootServiceFacts.Facts(','new MorningBrokerExecution.Observations(','new BrokerJournalEvidence.Summary(','Path.of("/public-data/','"/public-diagnostic/"'])
    assert len(METADATA)==5 and len(EXECUTED)==5 and len(UNEXECUTED)==12 and all(n in UNEXECUTED for n in MAIN_UNITS)
    for row in ROWS:
        path=source_path(row);name=row['name']
        assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][path]==run.host.sha(data.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}==set(CLOSURES[name])
    for name in ['dev/codex/schubert/nk/storage/StorageRootLayout','dev/codex/schubert/nk/batch/mq/ArtemisStartupObservation']:
        assert name in current['fullSourceUnits']
    run.step=environmental_step;run.main()
