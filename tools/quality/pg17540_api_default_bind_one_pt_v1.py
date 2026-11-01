"""Whole original default-bind1 owned loopback; supplementary scope only, no business API/native start."""
import re
import inspect
import zipfile
from owned_api_default_loopback_environment_step_v1 import environmental_step,_owned_original_step
import scoped_prometheus_owned_api_default_loopback_host_v1 as run
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
COUNTS={'ApiManagementDefaultBindTest':1}
PINS={'ApiManagementDefaultBindTest':'d12fa4fa382555316c3f280ec1040bb8850839dc4db146c816262c3157b75e82'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-api/src/test/java/'+PREFIX+'bootstrap/'+n+'.java') for n in COUNTS}
EXTRAS={}
FIXTURES={}
SESSION='PG17540-API-DEFAULT-BIND-ORIGINAL1'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17539-api-default-bind-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17508-current2746-inspector-deployment-registry-v1/manifest.json','eb7902fee60aaf3966019a81ce70ffde89e1d070181fa83264508fc381f6de6a')
    assert old['source']==SOURCE and set(MAIN_UNITS)<=old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert next(v.removeprefix('package ').removesuffix(';') for v in text.splitlines() if v.startswith('package '))+'.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in EXTRAS.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    disclosure=data.read_checked(data.BASE/'PG17533-owned-api-default-loopback-metadata-v2/manifest.json','6a74805ca8c4ec6a415ec608833ee749d9bec431a875eb1a6f8812e26bd2c31e')
    assert disclosure['actualExit']==0 and disclosure['source']==SOURCE and disclosure['productTestsExecuted']==0 and (disclosure['algorithmNegativeVectors'],disclosure['scopeNegativeVectors'],disclosure['effectNegativeVectors'])==(7,8,8)
    assert data.sha((ROOT/'tools/quality/scoped_prometheus_owned_api_default_loopback_host_v1.py').read_bytes())==disclosure['newRunnerSha256']=='58ed7e9ced26b1fb5b17ad509981c582c5e7a273974b1e5b7c56511da5c166bd'
    verify(disclosure['invocation'])
    env_binding=data.read_checked(data.BASE/'PG17534-owned-api-default-environment-binding-v1/manifest.json','9f0055d8350621694a443f3a805b1753ccd880d108f8060233cc14db37d61781')
    assert env_binding['actualExit']==0 and env_binding['source']==SOURCE and (env_binding['sourceNegativeVectors'],env_binding['bindingNegativeVectors'],env_binding['stubDelegations'])==(5,3,1)
    assert data.sha(inspect.getsource(environmental_step).encode())==env_binding['callbackSourceSha256'] and _owned_original_step.__module__==run.__name__==env_binding['ownedStepModule'] and env_binding['oldSlotUnchanged'] is True and env_binding['callerImportedByQualification'] is False
    verify(env_binding['invocation'])
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    prior_review=data.read_checked(data.BASE/'PG17389-api-management-review-v3/manifest.json','29aa440f0b6c31ab61c489901db7ca8827a694481f5d172e19361975f30af41a')
    assert prior_review['source']==SOURCE and prior_review['reviewedMainInputs']==reviewed
    verify(prior_review['invocation'])
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='SAME_BYTE_PRIOR_WHOLE_MAIN_REVIEW_AND_FRESH_WHOLE_ORIGINAL_TEST1',priorWholeMainReviewReference=['PG17389-api-management-review-v3','29aa440f0b6c31ab61c489901db7ca8827a694481f5d172e19361975f30af41a'],supplementaryScopeOnly=True,oldFullSourceCountersPreserved=True,reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,inMemoryCredentialBufferAndAclValuesOnly=False,testOwnSecureRandomFixtureBytesGenerated=False,publicFixedUuidFixtureOnly=False,actualNetworkActionCount=None,declaredOwnLoopbackHttpFixtureOnly=True,declaredOnlyLocalAddress='127.0.0.1',declaredOwnJavaMonotonicClockAndBoundedSleep=True,declaredJdkClientAndServerThreadsOnly=True,syntheticScenarioPublisherCallbackInvoked=False,stubDescriptorContentHashNotVerified=False,realRuntimeCredentialOrKeyLoaded=False,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=None,declaredOwnExecutorInstances=None,declaredOwnTaskCount=None,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17540-api-default-bind-one-pt-v1';run.OUT=data.BASE/'PG17540-api-default-bind-one-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/ApiManagementDefaultBindCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['ApiManagementDefaultBindTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={};run.OWNED_LOOPBACK_AUTHORITY=True
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
