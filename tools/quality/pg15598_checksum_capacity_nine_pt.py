"""Original checksum4/capacity5; borrowed in-memory channels/counters, no filesystem or inspector."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/api/'
MAIN_PINS={"file/AssetChecksumManifest":"503f89c284da8e356acc0ff45cf865b40cd094a783b04abce2389a89bb59a8b9","file/MediaIntegrityException":"c95df6a16e02c263a6409b04695df44ab06b4500f92c825bdbf31e94a89168ac","storage/TransferCapacity":"93d56d7ef295998c5f637c90f0aafaa2f15fbdc4d366ab6e238c833c96788db7","error/CapacityExceededException":"97da7ca6adc387e39046443ca298a4dd39dbbf574fa2b9e16951c8b9d227793c"}
CLOSURES={"file/AssetChecksumManifest":["file/AssetChecksumManifest"],"file/MediaIntegrityException":["file/MediaIntegrityException"],"storage/TransferCapacity":["storage/TransferCapacity","storage/TransferCapacity$Level","storage/TransferCapacity$Reservation","storage/TransferCapacity$Snapshot"],"error/CapacityExceededException":["error/CapacityExceededException"]}
DECLARED={"file/AssetChecksumManifestTest":["9df639438471f40c95c88f75b73dc0e627f45d576e5ec62671a9893b728c928a",4],"storage/TransferCapacityTest":["3eecc613cba54d6a14141b751c131e1360f82318c536f733e084d2abc3d08ea1",5]}
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java'/PREFIX
TESTS={p.rpartition('/')[2]:ROOT/(p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
FIXTURES={}
SESSION='PG15598-CHECKSUM-CAPACITY-CURRENT-WHOLE9'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15598-checksum-capacity-nine-pt-v1';run.OUT=run.host.BASE/'PG15598-checksum-capacity-nine-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ChecksumCapacityCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['AssetChecksumManifestTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={name:path for name,path in TESTS.items() if name!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='0311cee598fda699f1bab96eeb6d3e8625dd9102d2b82bb9c8cc72f7dd90bbc8'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15588-current1894-public-inbox-values-registry-v1/manifest.json','326d30d61ad5da5149c91af3b8687ef954180f0487925857e3158ed85699b9b1')
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
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for short,pin in MAIN_PINS.items():
            name=PREFIX+short;path='src/schubert-nk-api/src/main/java/'+name+'.java'
            assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
            expected={PREFIX+p for p in CLOSURES[short]}
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}==expected
    run.step=environmental_step;run.main()
