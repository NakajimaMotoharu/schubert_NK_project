"""Entire original fixed credential-name catalog5; no credential bytes, config IO or native initialization."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'ServiceCredentialIdTest':4,'EnumValueCatalogCompatibilityTest':1}
SESSION='PG14647-ORIGINAL-STORAGE-CATALOG5'
ROOT=run.host.ROOT/'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={'ServiceCredentialIdTest':'3e57341d9cc9427e366ea1e91ac5f2d808f87d0f0cc3dc0679e6470776438461','EnumValueCatalogCompatibilityTest':'d5ca7770d0664831aae96eabf785d13195cc0695e6903c7ce01a31b0c1e7b61f'}
FIXTURES={}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PREFIX='dev/codex/schubert/nk/storage/'
REQUIRED={PREFIX+'ServiceCredentialId',PREFIX+'ServiceCredentialId$Kind',PREFIX+'ServiceConfigFiles$Service'}

def initialized_classes(text):
    return {m.group(1).replace('.','/') for m in re.finditer(r"Initializing ['\"]([^'\"]+)['\"]",text)}

def isolated(values):
    return REQUIRED<=values and PREFIX+'ServiceConfigFiles' not in values and not any(n.startswith(PREFIX+'Linux') for n in values)

def init_prevention(values):
    assert isolated(values)
    vectors=[values|{PREFIX+'ServiceConfigFiles'},values|{PREFIX+'LinuxDirectoryCalls'},values-{PREFIX+'ServiceConfigFiles$Service'},values-{PREFIX+'ServiceCredentialId'}]
    assert all(not isolated(v) for v in vectors)
    return len(vectors)

def catalog_step(name,command):
    if name=='selected-junit':
        log=run.SLOT/'own-class-init.log'
        assert not log.exists()
        command=[command[0],'-Xlog:class+init=info:file='+str(log),*command[1:]]
    result=environmental_step(name,command)
    if name=='selected-junit' and result['actualExit']==0:
        names=initialized_classes(log.read_text())
        assert init_prevention(names)==4
        result['ownClassInitialization']=dict(path=str(log),sha256=run.host.sha(log),required=sorted(REQUIRED),observedRequired=sorted(REQUIRED&names),outerConfigInitialized=False,linuxClassesInitialized=[],metadataNegativeVectors=4,sourceScopeChecks=6,sourceScopeNegativeVectors=5,observationScope='THIS_OWN_JVM_ONLY_NOT_EXTERNAL_PROCESS_OR_VM')
    return result


def source_operation_allowed(text):
    forbidden=['@BeforeAll','@BeforeEach','@TempDir','ProcessBuilder','DriverManager','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(']
    return not any(term in text for term in forbidden) and re.search(r'(?<![A-Za-z0-9_$])Files\s*\.',text) is None and re.search(r'ServiceConfigFiles\s*\.\s*(production|read)\s*\(',text) is None

def source_prevention():
    expected=[
        ('ServiceConfigFiles.Service.API',True),
        ('Files.readString(p)',False),
        ('java.nio.file.Files.readString(p)',False),
        ('Files . readString(p)',False),
        ('ServiceConfigFiles.production()',False),
        ('ServiceConfigFiles . read(p)',False)]
    assert all(source_operation_allowed(text) is allowed for text,allowed in expected)
    return len(expected)

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14647-storage-catalog-whole-five-pt-v2'
    run.OUT=run.host.BASE/'PG14647-storage-catalog-whole-five-pt-v2'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalStorageCatalogJunitLauncher.java'
    run.NEW_TEST=TESTS['ServiceCredentialIdTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='ServiceCredentialIdTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    for n,p in TESTS.items():
        relative=str(p.relative_to(run.host.ROOT))
        assert p==ROOT/(n+'.java') and p.parent==ROOT and relative.startswith('src/schubert-nk-storage/src/test/java/')
        assert normal['begin']['inputHashes'][relative]==run.host.sha(p)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[n]
        text=p.read_text()
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[n]
        assert source_operation_allowed(text)
        assert '"dev.codex.schubert.nk.storage.'+n+'", '+str(COUNTS[n]) in run.HELPER.read_text()
    assert init_prevention(set(REQUIRED))==4 and source_prevention()==6
    run.step=catalog_step;run.main()
