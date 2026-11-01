"""Whole original Web HTTP12/admission3, owned local MVC containers only, no native Root."""
import re
import inspect
import zipfile
from owned_mvc_loopback_environment_step_v1 import environmental_step,_owned_original_step
import scoped_prometheus_owned_mvc_loopback_host_v1 as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/web/'
NAME=PREFIX+'bootstrap/WebHttpServer'
ADMISSION=PREFIX+'bootstrap/WebHttpAdmission'
MAIN_UNITS={NAME:dict(module='web',name=NAME,sha256='b1e458ef9a9a246f8bb70866dbf671a005bbb569b9c4e27c20b525c20b3180a5'),ADMISSION:dict(module='web',name=ADMISSION,sha256='dd0cda3ed6582fed7cd1d05ce1505d8b4bbfa77eb2984cd275b7c585e57ee130')}
CLOSURES={NAME:[NAME],ADMISSION:[ADMISSION]}
METADATA=set()
METADATA_FLAGS={n:1536 for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'WebHttpServerTest':12,'WebHttpAdmissionTest':3}
PINS={'WebHttpServerTest':'17d753d79b5600d2938e46713767261397f2077b8d018b109e0e8bfad499f6ca','WebHttpAdmissionTest':'31c48ac4bcf81c0602188e2991452c1ecfe0d1a59200598b72832621e5d19d19'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-web/src/test/java/'+PREFIX+'bootstrap/'+n+'.java') for n in COUNTS}
PUBLIC_READS={"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebHttpAdmissionValve.java":"8318b77646af9bbbee9e3a839c6f850548eef82999b640cbc274b61b83a5606f","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/config/WebMvcConfiguration.java":"72ac4fcc161a85182e17d6167640cb18c93faed174fdd142225eaf1d84912d30"}
EXTRAS={}
FIXTURES={}
SESSION='PG17786-WEB-MVC-LOOPBACK-ORIGINAL15'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17785-web-mvc-loopback-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17768-current2810-receipt-owned-graph-registry-v1/manifest.json','34cfd2a3112993b52da7443376e7fd7470ed9709fd00e3612f3b5792c24d8727')
    assert old['source']==SOURCE and NAME not in old['fullSourceUnits'] and ADMISSION in old['fullSourceUnits']
    assert old['fullSourceUnits'][ADMISSION]['four100'] is False
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert next(v.removeprefix('package ').removesuffix(';') for v in text.splitlines() if v.startswith('package '))+'.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in (PUBLIC_READS|EXTRAS).items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    disclosure=data.read_checked(data.BASE/'PG17782-owned-mvc-loopback-runner-metadata-v1/manifest.json','1da064d3efbce8bf4993d28635aafa001fea5c1aa90724993cff8f79b1dccd0f')
    assert disclosure['actualExit']==0 and disclosure['source']==SOURCE and disclosure['productTestsExecuted']==0 and (disclosure['algorithmNegativeVectors'],disclosure['scopeNegativeVectors'],disclosure['effectNegativeVectors'])==(7,8,8)
    assert data.sha((ROOT/'tools/quality/scoped_prometheus_owned_mvc_loopback_host_v1.py').read_bytes())==disclosure['newRunnerSha256']=='18a7ac7b682c388d72c7d3542c563c80b1c131accf41f5eeec7dce2d508e1f5f'
    verify(disclosure['invocation'])
    assert 'Thread.currentThread().interrupt();' in TESTS['WebHttpAdmissionTest'].read_text() and 'assertTrue(Thread.interrupted());' in TESTS['WebHttpAdmissionTest'].read_text()
    env_binding=data.read_checked(data.BASE/'PG17784-owned-mvc-loopback-environment-binding-v1/manifest.json','cc09737223363737e2f09dbb47ee2f76733ca38949c80d1d9b21126f688ad60c')
    assert env_binding['actualExit']==0 and env_binding['source']==SOURCE and (env_binding['sourceNegativeVectors'],env_binding['bindingNegativeVectors'],env_binding['stubDelegations'])==(5,3,1)
    assert data.sha(inspect.getsource(environmental_step).encode())==env_binding['callbackSourceSha256'] and _owned_original_step.__module__==run.__name__==env_binding['ownedStepModule'] and env_binding['oldSlotUnchanged'] is True and env_binding['callerImportedByQualification'] is False
    verify(env_binding['invocation'])
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,inMemoryCredentialBufferAndAclValuesOnly=False,testOwnSecureRandomFixtureBytesGenerated=False,publicFixedUuidFixtureOnly=False,actualNetworkActionCount=None,declaredOwnLoopbackHttpFixtureOnly=True,declaredOnlyLocalAddress='127.0.0.1',declaredOwnJavaMonotonicClockAndBoundedSleep=False,testOwnJavaMonotonicClockRead=True,ownCurrentThreadInterruptFlagModifiedAndFinallyCleared=True,transientOwnWildcardPortRebindWithoutAccept=True,testOwnTemporaryContentWritten=True,publicClasspathTemplatesOpened=True,declaredJdkClientAndServerThreadsOnly=True,syntheticScenarioPublisherCallbackInvoked=False,stubDescriptorContentHashNotVerified=False,realRuntimeCredentialOrKeyLoaded=False,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=False,publicSourceReadHashes=PUBLIC_READS,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=None,declaredOwnExecutorInstances=1,declaredOwnTaskCount=1,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17786-web-mvc-loopback-fifteen-pt-v1';run.OUT=data.BASE/'PG17786-web-mvc-loopback-fifteen-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/WebMvcLoopbackFifteenCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['WebHttpServerTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={};run.OWNED_LOOPBACK_AUTHORITY=True
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
