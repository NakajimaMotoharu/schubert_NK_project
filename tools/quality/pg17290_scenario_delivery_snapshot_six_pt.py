"""Whole original delivery3/snapshot-boundary3; only memory data, handwritten goldens and fake publisher."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/api/'
NAME=PREFIX+'application/scenario/ScenarioDetailDelivery'
MAIN_UNITS={PREFIX+n:dict(module='api',name=PREFIX+n,sha256=h) for n,h in [('application/scenario/ScenarioDetailDelivery','6400a4da0720ec7987f3aa4defe005014a232ed0475513fd90501b08366a2523'),('persistence/ScenarioDetailSnapshot','a9adb21b9bddf514ad3b44218465762c767d8f4f8ba34d38c4526df74eb0dcc6')]}
CLOSURES={n:[n] for n in MAIN_UNITS}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'ScenarioDetailDeliveryTest':3,'ScenarioDetailSnapshotBoundaryTest':3}
PINS={'ScenarioDetailDeliveryTest':'59127e08ee2dc63a31dbd13070add804f721caf9bebf2d5b3934868448767fd5','ScenarioDetailSnapshotBoundaryTest':'4d235d14a7c7c31089525741ac93cb425520bae75e703d9b51b2e6d46c03ede2'}
ROOT=data.ROOT
TESTS={'ScenarioDetailDeliveryTest':ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/scenario/ScenarioDetailDeliveryTest.java','ScenarioDetailSnapshotBoundaryTest':ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/persistence/ScenarioDetailSnapshotBoundaryTest.java'}
EXTRAS={}
FIXTURES={}
SESSION='PG17290-SCENARIO-DELIVERY-SNAPSHOT-ORIGINAL6'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17289-scenario-delivery-snapshot-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17278-current2655-scenario-audit-registry-v1/manifest.json','43247467c29ef1486523990bbe637fdc43eb215bb525302dbcd73edf3de7c101')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        declared_package=next(line.removeprefix('package ').removesuffix(';') for line in text.splitlines() if line.startswith('package '))
        assert declared_package+'.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in EXTRAS.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,inMemoryCredentialBufferAndAclValuesOnly=False,testOwnSecureRandomFixtureBytesGenerated=False,publicFixedUuidFixtureOnly=True,syntheticScenarioPublisherCallbackInvoked=True,stubDescriptorContentHashNotVerified=True,realRuntimeCredentialOrKeyLoaded=False,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17290-scenario-delivery-snapshot-six-pt-v1';run.OUT=data.BASE/'PG17290-scenario-delivery-snapshot-six-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/ScenarioDeliverySnapshotSixCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['ScenarioDetailDeliveryTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={'ScenarioDetailSnapshotBoundaryTest':TESTS['ScenarioDetailSnapshotBoundaryTest']}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
