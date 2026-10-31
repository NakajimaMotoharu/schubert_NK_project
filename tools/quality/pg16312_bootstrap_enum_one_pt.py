"""One unchanged public enum/schema catalog case, no credential or system-manager connection."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
AES='dev/codex/schubert/nk/api/file/AesCredentialFile'
MANAGER='dev/codex/schubert/nk/bootstrap/SystemManagerObservation'
MAIN_UNITS={AES:dict(module='bootstrap',name=AES,sha256='2e997f3fd7ff7c0075b51333682b3e02b254461326ffe0f92f407aa53716a2f2'),
            MANAGER:dict(module='bootstrap',name=MANAGER,sha256='6affd57005221db2b1d112da3449f8c26085edf21ed132d8abfc9fdb3a5afacb')}
CLOSURES={AES:[AES],MANAGER:[MANAGER,MANAGER+'$Budget',MANAGER+'$Factory',MANAGER+'$Owner',MANAGER+'$Property',MANAGER+'$Service',MANAGER+'$Session']}
METADATA={MANAGER+'$Budget',MANAGER+'$Factory',MANAGER+'$Session'}
UNEXECUTED={MANAGER,MANAGER+'$Owner',MANAGER+'$Property'}
ROOT=data.ROOT/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file'
TESTS={'EnumValueCatalogCompatibilityTest':ROOT/'EnumValueCatalogCompatibilityTest.java'}
COUNTS={'EnumValueCatalogCompatibilityTest':1}
FIXTURES={}
SESSION='PG16312-BOOTSTRAP-ENUM-ONE'
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'

if __name__=='__main__':
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16312-bootstrap-enum-one-pt-v1';run.OUT=data.BASE/'PG16312-bootstrap-enum-one-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/BootstrapEnumOneJunitLauncher.java'
    run.NEW_TEST=TESTS['EnumValueCatalogCompatibilityTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.FIXTURES,run.COUNTS=FIXTURES,COUNTS;run.EXTRA_TEST_SOURCES,run.SESSION_ID=(REPORTER,),SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    previous=data.read_checked(data.BASE/'PG16302-current2172-inspection-registry-v1/manifest.json','000254c960de391f58918a11980b7cc1c62f3fa1cfdabb95188f3ada22d95254')
    assert normal['source']==previous['source']==SOURCE and not set(MAIN_UNITS)&previous['fullSourceUnits'].keys()
    assert 'dev.codex.schubert.nk.api.file.EnumValueCatalogCompatibilityTest' not in previous['suiteNames']
    path=run.NEW_TEST;relative=str(path.relative_to(data.ROOT));text=path.read_text()
    assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)=='da1b6cfec2530e07f7d083906901d80d69279ac926642356d14afa31fb0c57fc'
    assert text.count('@Test')==1 and re.findall(r'@Test\s+void\s+(\w+)\s*\(',text)==['bst001CredentialAndServiceIdentifiersRetainTheirLiteralCatalogs']
    assert not any(v in text for v in ['@Before','ProcessBuilder','DriverManager','HttpClient','Files.','Linux','RootStartupContext','ChildStartupContext','java.sql','ObjectInputStream','ObjectOutputStream','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec'])
    assert re.search(r'SystemManagerObservation\.(?!Service\b)',text) is None and 'new SystemManagerObservation' not in text
    for row in MAIN_UNITS.values():
        relative=source_path(row)
        assert normal['begin']['inputHashes'][relative]==run.host.sha(data.ROOT/relative)==run.host.sha(COMPILE/'snapshot'/relative)==row['sha256']
    with zipfile.ZipFile(normal['jars']['bootstrap']['path']) as jar:
        for name,names in CLOSURES.items():assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(names)
    run.step=environmental_step;run.main()
