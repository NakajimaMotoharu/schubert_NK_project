"""Whole original pre-SQL13, JDBC Proxy must remain untouched; existing Source proofs retained."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/batch/'
MAIN_PINS={"file/CaddyPublicConfiguration":"f0d5b21a34e7e9d5879663ee49e4645d34115aef60b2d3119594cf9c424a731f","file/EnvironmentInodePolicy":"88285d20e13e42bc6ecf729f4011c0129ccf4b5e7fe153e44a3d8c126b8dde9b"}
CLOSURES={"file/CaddyPublicConfiguration":["file/CaddyPublicConfiguration"],"file/EnvironmentInodePolicy":["file/EnvironmentInodePolicy","file/EnvironmentInodePolicy$Metadata","file/EnvironmentInodePolicy$Snapshot","file/EnvironmentInodePolicy$Source"]}
DECLARED={"file/CaddyAddressBoundaryTest":["7f4eb7a2c81d22f157a7306a554a195924f8b9d87b5f1e750c6b2887cecb73f0",2],"file/CaddyPublicCaMetadataTest":["730d70e2456ac1fe29cca90f217e07ad5df3b2014638adab59f0aa79c2596b42",3],"file/CaddyPublicMetadataTest":["8590d10b5f5c074de40ff89e08882daafe2500831c5376b9da350027e53b0b77",4]}
ROOT=run.host.ROOT/'src/schubert-nk-batch/src/test/java'/PREFIX
TESTS={p.rpartition('/')[2]:ROOT/(p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
FIXTURES={}
SESSION='PG15710-CADDY-PUBLIC-VALUE-WHOLE9'
GOLDEN_SOURCE=ROOT/'file/CaddyPublicConfigurationTest.java'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15710-caddy-public-value-nine-pt-v1';run.OUT=run.host.BASE/'PG15710-caddy-public-value-nine-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/CaddyPublicValueJunitLauncher.java'
    run.NEW_TEST=TESTS['CaddyAddressBoundaryTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={name:path for name,path in TESTS.items() if name!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,GOLDEN_SOURCE);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='e3e81789502723cdc40b0548b7c0c0a0deb5dd2cf27e5d8de3c867c18b166091'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15701-current1995-media-scenario-registry-v2/manifest.json','27a79dcda15f57f41c45673c203a6e3127547a4b1be72d3d1058843ce71bf5d0')
    assert current['postDisclosureCorrections']['22f14eebdb3284e51c67d9b05b4ee8eaf4b01784006a76cae6d73b071c98bcb3']['effectiveDisclosure']['effectiveCryptoOrKeyOperationsInvoked'] is True
    golden='a7cde1d1a189e6e835084e612d83e87b0d51925a8a17374f97005301019daa9c'
    relative=str(GOLDEN_SOURCE.relative_to(run.host.ROOT))
    assert run.host.sha(GOLDEN_SOURCE)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==golden
    assert GOLDEN_SOURCE.read_text().count('@Test')==3 and '@Before' not in GOLDEN_SOURCE.read_text()
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
        assert ('dev.codex.schubert.nk.batch.'+next(p for p in DECLARED if p.endswith('/'+name)).replace('/','.')) not in current['suiteNames']
    with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
        for short,pin in MAIN_PINS.items():
            name=PREFIX+short;path='src/schubert-nk-batch/src/main/java/'+name+'.java'
            assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
            expected={PREFIX+p for p in CLOSURES[short]}
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}==expected
    run.step=environmental_step;run.main()
