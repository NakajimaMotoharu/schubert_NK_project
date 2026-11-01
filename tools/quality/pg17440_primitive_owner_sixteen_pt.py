"""Whole original two primitive owner suites; fake integer descriptors, no OS admission."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/batch/'
CG=PREFIX+'platform/FixedUnitCgroupNamespace'
VIEW=PREFIX+'file/StartupAdmissionFile'
MAIN_UNITS={CG:dict(module='batch',name=CG,sha256='96e4b3cfcdb5129e4f7a60e1395ef201a466cea5239d01b488ffd91049382345'),VIEW:dict(module='batch',name=VIEW,sha256='55fdbf46c65a1622f10f19e9ff018b8676c1d3b5a2dcf3ecc80ca5758637c61a')}
CLOSURES={CG:[CG]+[CG+'$'+n for n in ['Context','Io','Identity','Snapshot','Owner']],VIEW:[VIEW]+[VIEW+'$'+n for n in ['Admission','NioIo','AdmittedOperation','Identity','ViewOperation','Io','Snapshot','ViewOwner']]}
METADATA={CG+'$Context',CG+'$Io',VIEW+'$AdmittedOperation',VIEW+'$ViewOperation',VIEW+'$Io'}
METADATA_FLAGS={n:(1537 if n==VIEW+'$AdmittedOperation' else 1536) for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'CgroupPrimitiveOwnerTest':8,'StartupAdmissionViewOwnerTest':8}
PINS={'CgroupPrimitiveOwnerTest':'849da5012a073260ae4b7df40bbab647af37d075653841e60683a6105dc3e234','StartupAdmissionViewOwnerTest':'719595a634dfe355e89e88e8cbadbeeb32cf417ed5e4c859b9f7bf940b46c3f2'}
ROOT=data.ROOT
TESTS={'CgroupPrimitiveOwnerTest':ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/CgroupPrimitiveOwnerTest.java','StartupAdmissionViewOwnerTest':ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/StartupAdmissionViewOwnerTest.java'}
EXTRAS={}
FIXTURES={}
SESSION='PG17440-PRIMITIVE-OWNERS-ORIGINAL16'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17439-primitive-owners-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17428-current2714-web-management-registry-v1/manifest.json','5f99a1fa60f08e34de59942316e397fb987701b9f613804329028ef5131ae02f')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert next(v.removeprefix('package ').removesuffix(';') for v in text.splitlines() if v.startswith('package '))+'.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in EXTRAS.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=True,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,inMemoryCredentialBufferAndAclValuesOnly=False,testOwnSecureRandomFixtureBytesGenerated=False,publicFixedUuidFixtureOnly=False,syntheticScenarioPublisherCallbackInvoked=False,stubDescriptorContentHashNotVerified=False,realRuntimeCredentialOrKeyLoaded=False,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=4,declaredOwnExecutorInstances=2,declaredOwnTaskCount=4,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17440-primitive-owner-sixteen-pt-v1';run.OUT=data.BASE/'PG17440-primitive-owner-sixteen-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/PrimitiveOwnerSixteenCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['CgroupPrimitiveOwnerTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={'StartupAdmissionViewOwnerTest':TESTS['StartupAdmissionViewOwnerTest']}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
