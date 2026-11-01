"""Whole original public ELF and typed metadata six; no OS or real Root admission."""
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
NAME=PREFIX+'file/RootServiceExecutableAdmission'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='04efbba4deb8101b038a9faa978c090fc3227e86dc4658abc4b5dfde959d28c7')}
CLOSURES={NAME:[NAME,NAME+'$RootDescriptor',NAME+'$Capability',NAME+'$Work',NAME+'$DigestFactory']}
METADATA={NAME+'$'+n for n in ['Capability','Work','DigestFactory']}
METADATA_FLAGS={n:1536 for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'RootServiceExecutableAdmissionTest':6}
PINS={'RootServiceExecutableAdmissionTest':'0eb588b1c26c5f43be596c2f7c33548eaca39981c6a95bea4c602cfd0084681f'}
ROOT=data.ROOT
TESTS={'RootServiceExecutableAdmissionTest':ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootServiceExecutableAdmissionTest.java'}
EXTRAS={}
FIXTURES={}
SESSION='PG17460-ROOT-ELF-METADATA-ORIGINAL6'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17459-root-elf-metadata-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17448-current2730-primitive-owner-registry-v1/manifest.json','7e21829d2e0dedba307f17829397864d4c5cfb350a13006ccd943aef2b9139ff')
    assert old['source']==SOURCE and set(MAIN_UNITS)<=old['fullSourceUnits'].keys()
    prior_review=data.read_checked(data.BASE/'PG17309-root-elf-digest-review-v1/manifest.json','b6b45247e72774f119e73bc5d3d0f6b1afbdaef94f3ae7c21f8ce9794ed7b81a')
    assert prior_review['actualExit']==0 and prior_review['source']==SOURCE and prior_review['reviewedMainInputs']=={source_path(row):row['sha256'] for row in MAIN_UNITS.values()}
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
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='SAME_BYTE_PRIOR_WHOLE_MAIN_AND_FRESH_ORIGINAL_TEST_REVIEW',priorWholeMainReviewReference=['PG17309-root-elf-digest-review-v1','b6b45247e72774f119e73bc5d3d0f6b1afbdaef94f3ae7c21f8ce9794ed7b81a'],reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,inMemoryCredentialBufferAndAclValuesOnly=False,testOwnSecureRandomFixtureBytesGenerated=False,publicFixedUuidFixtureOnly=False,syntheticScenarioPublisherCallbackInvoked=False,stubDescriptorContentHashNotVerified=False,realRuntimeCredentialOrKeyLoaded=False,publicDigestOnly=True,cryptoOrKeyOperationsInvoked=True,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17460-root-elf-metadata-six-pt-v1';run.OUT=data.BASE/'PG17460-root-elf-metadata-six-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/RootElfMetadataSixCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['RootServiceExecutableAdmissionTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
