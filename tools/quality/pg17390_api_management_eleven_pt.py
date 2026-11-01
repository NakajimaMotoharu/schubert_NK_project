"""Whole original own loopback Server7/Stop4; explicit fixture network, no business API/native start."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_owned_loopback_host_v1 as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/api/'
NAME=PREFIX+'bootstrap/ApiManagementServer'
MAIN_UNITS={NAME:dict(module='api',name=NAME,sha256='81c29219808b8c38764d7bcd9ec1d1e7fc32a709a158a0399237e7fe5d46cb5c')}
CLOSURES={NAME:[NAME,NAME+'$Factory']}
METADATA={NAME+'$Factory'}
METADATA_FLAGS={n:1536 for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'ApiManagementServerTest':7,'ApiManagementStopTest':4}
PINS={'ApiManagementServerTest':'24361ef91c061e534a9d7468ba26c0d5cc899b79f43d26f268b03b46176c04b2','ApiManagementStopTest':'3dd22208776aed87e326a413ceb19c3179f4cab253b407e57c9264755b3a0bce'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-api/src/test/java/'+PREFIX+'bootstrap/'+n+'.java') for n in COUNTS}
EXTRAS={}
FIXTURES={}
SESSION='PG17390-API-MANAGEMENT-ORIGINAL11'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17389-api-management-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17378-current2690-web-codec-owner-registry-v1/manifest.json','6ebc5bde4fe2f26d0ddebd442788fb9cd347777080d50187c5e87ff4f0e64790')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert next(v.removeprefix('package ').removesuffix(';') for v in text.splitlines() if v.startswith('package '))+'.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in EXTRAS.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    disclosure=data.read_checked(data.BASE/'PG17388-owned-loopback-runner-metadata-v1/manifest.json','2eb8a6f1c1832f9612522d93e9a8cbe05e4549db713dc9378a358b563450d2b6')
    assert disclosure['actualExit']==0 and disclosure['source']==SOURCE and disclosure['productTestsExecuted']==0 and (disclosure['algorithmNegativeVectors'],disclosure['scopeNegativeVectors'],disclosure['effectNegativeVectors'])==(7,8,8)
    assert data.sha((ROOT/'tools/quality/scoped_prometheus_owned_loopback_host_v1.py').read_bytes())==disclosure['newRunnerSha256']=='faf3eae6357d50d2b3b89311fb4fb48613309c236e1d32686f9227a9cfd4c6ea'
    verify(disclosure['invocation'])
    assert 'while (!condition.getAsBoolean() && System.nanoTime() - deadline < 0) Thread.sleep(1);' in TESTS['ApiManagementStopTest'].read_text()
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,inMemoryCredentialBufferAndAclValuesOnly=False,testOwnSecureRandomFixtureBytesGenerated=False,publicFixedUuidFixtureOnly=False,actualNetworkActionCount=None,declaredOwnLoopbackHttpFixtureOnly=True,declaredOnlyLocalAddress='127.0.0.1',declaredOwnJavaMonotonicClockAndBoundedSleep=True,declaredJdkClientAndServerThreadsOnly=True,syntheticScenarioPublisherCallbackInvoked=False,stubDescriptorContentHashNotVerified=False,realRuntimeCredentialOrKeyLoaded=False,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=None,declaredOwnExecutorInstances=None,declaredOwnTaskCount=None,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17390-api-management-eleven-pt-v1';run.OUT=data.BASE/'PG17390-api-management-eleven-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/ApiManagementElevenCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['ApiManagementServerTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={};run.OWNED_LOOPBACK_AUTHORITY=True
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
