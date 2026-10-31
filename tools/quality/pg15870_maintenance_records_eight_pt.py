"""Original whole literal maintenance codec8; public own TempDir/hash oracle only, no live file store."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/batch/'
MAIN_PINS={'file/MaintenanceRecords':'3c83d4b28a61325e4d997bfe7a92d92ea0f2ff79bbf03d4b8e37185c2335b80e','repository/MaintenanceCompletion':'3713fb2ce03a4ec926c4d193051373348da922c15d5f22e8f43cabd215b36dcd'}
CLOSURES={'file/MaintenanceRecords':['file/MaintenanceRecords'],'repository/MaintenanceCompletion':['repository/MaintenanceCompletion','repository/MaintenanceCompletion$Outcome']}
DECLARED={'file/MaintenanceRecordsTest':['6a771cff5dad26f8b9f469667169f113b3e91be172fe52f400e53d543615dc32',8]}
ROOT=run.host.ROOT/'src/schubert-nk-batch/src/test/java'/PREFIX
TESTS={p.rpartition('/')[2]:ROOT/(p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
FIXTURES={}
SESSION='PG15870-MAINTENANCE-RECORDS-WHOLE8'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15870-maintenance-records-eight-pt-v1';run.OUT=run.host.BASE/'PG15870-maintenance-records-eight-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/MaintenanceRecordsEightJunitLauncher.java'
    run.NEW_TEST=TESTS['MaintenanceRecordsTest'];run.TEST_ROOT=ROOT/'file'
    run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='01b268ed6644cd780e4248ddccdc77930dfbd74df5562eedb099183cc9dae7e1'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15860-current2047-scenario-reader-registry-v1/manifest.json','4dc04911cc2e6a097dbb5908e1fe37d31612c04d33ff3ef07500bac33ad6e1ba')
    assert current['postDisclosureCorrections']['22f14eebdb3284e51c67d9b05b4ee8eaf4b01784006a76cae6d73b071c98bcb3']['effectiveDisclosure']['effectiveCryptoOrKeyOperationsInvoked'] is True
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(run.host.ROOT))
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'(?m)^  void [A-Za-z0-9_]+\(',text))==COUNTS[name]
        assert 'Path.of("target/maintenance-record-traces")' in text and 'Executors.newFixedThreadPool(8)' in text and 'index <= 64' in text
        assert ('dev.codex.schubert.nk.batch.file.'+name) not in current['suiteNames']
        assert not any(v in text for v in ['ProcessBuilder','DriverManager','System.getenv(','getConnection(','TemporaryInfrastructureException','WebStartupException','Class.forName(','HttpClient','Tomcat','createConnection(','createContext(','configureOwned(','.production('])
    with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
        for short,pin in MAIN_PINS.items():
            name=PREFIX+short;path='src/schubert-nk-batch/src/main/java/'+name+'.java'
            assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}=={PREFIX+v for v in CLOSURES[short]}
    for name in ['dev/codex/schubert/nk/batch/repository/BatchRun','dev/codex/schubert/nk/batch/repository/MaintenanceActivation']:
        assert name in current['fullSourceUnits']
    run.step=environmental_step;run.main()
