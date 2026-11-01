"""Independent closed Authentication DTO validation only, without any real authentication flow."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME='dev/codex/schubert/nk/web/security/ClosedWebAuthentication'
MAIN_UNITS={NAME:dict(module='web',name=NAME,sha256='ad4406d529ecd8fcbca8c523d74bb6d8f6602632ef7cdd768f589bf52ce58214')}
CLOSURES={NAME:[NAME]}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'ClosedProjectionValueContractTest':6}
PINS={'ClosedProjectionValueContractTest':'96dc488720504882f06ef476b0482b34975b400a7d6feec55a9b839385c9c29d'}
ROOT=data.ROOT
TESTS={'ClosedProjectionValueContractTest':ROOT/'tools/quality/architecture/ClosedProjectionValueContractTest.java'}
PUBLIC_READS={'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/header/AuthenticationContext.java':'aaa18a4c954a425c943e8c30ea1752b665b249e86d8f1767e9e37f4aa61a6b66','src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/UserRole.java':'b68402e5705ca2ac5093a1b98a44de5a9f45ed69cb9b231658b4903c51e0bf69','src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionPrincipal.java':'29af626632ac4c2727f9d0963c3967cb0be7eda57daf762a482268c467dc9232','src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionStoreException.java':'93717ee948f88bd799a14cdad397c0d92e584711c32f571df8592be379033ed1'}
EXTRAS={}
FIXTURES={}
SESSION='PG17950-CLOSED-PROJECTION-VALUES6'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17949-closed-projection-value-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17938-current2840-web-ready-joint-registry-v1/manifest.json','a1289d9a32aa20e1c70eb06cf309b655f77f0af8150e13bd4b93ab3be84e2c06')
    assert old['source']==SOURCE and old['fullSourceUnits'][NAME]['four100'] is False
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative=='tools/quality/architecture/ClosedProjectionValueContractTest.java'
        assert text.count('@Test')==len(re.findall(r'@Test(?:\s*@Timeout\([^)]*\))?\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert next(v.removeprefix('package ').removesuffix(';') for v in text.splitlines() if v.startswith('package '))+'.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in PUBLIC_READS.items():assert data.sha((ROOT/path).read_bytes())==data.sha((COMPILE/'snapshot'/path).read_bytes())==current[path]==pin
    for path,pin in EXTRAS.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    text=(ROOT/source_path(MAIN_UNITS[NAME])).read_text()
    assert 'authentication.getClass() != UsernamePasswordAuthenticationToken.class' in text and 'authentication.getCredentials() != null' in text and 'authentication.getDetails() != null' in text
    assert not any(v in text for v in ['getByName','getSession','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec','RootStartupContext','ServiceProcessResources'])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,inMemoryCredentialBufferAndAclValuesOnly=False,testOwnSecureRandomFixtureBytesGenerated=False,publicFixedUuidFixtureOnly=False,syntheticScenarioPublisherCallbackInvoked=False,stubDescriptorContentHashNotVerified=False,realRuntimeCredentialOrKeyLoaded=False,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=False,publicSourceReadHashes=PUBLIC_READS,testPublicSourceRead=False,syntheticPermitRecordConstructionOnly=False,nativeNamedReadNullGuardOnlyInvoked=False,independentModuleLocalThrowableGraphsOnly=False,syntheticOwnedReceiptJdbcFaultPortsOnly=False,memoryServletHeaderFixtureOnly=False,memorySessionPrincipalValueOnly=False,nfcAndUtf8ValidationInvoked=False,publicSyntheticAuthenticationContextValueOnly=True,syntheticAuthenticationDtoProjectionOnly=True,syntheticPublicCredentialFixtureOnly=True,directNumericIpLiteralParsingInvoked=False,explicitDnsLookupInvoked=False,networkCountScope='PROJECT_EXPLICIT_TRANSPORT_CALLS_NOT_JDK_INTERNAL_INITIALIZATION',platformJdkInitializationEffects=None,junitTimeoutSeparateFrameworkWorkerOnly=False,actualPermitNamespaceLookups=0,actualRootOsAdmissionInvoked=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17950-closed-projection-six-pt-v1';run.OUT=data.BASE/'PG17950-closed-projection-six-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/ClosedProjectionSixCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['ClosedProjectionValueContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
