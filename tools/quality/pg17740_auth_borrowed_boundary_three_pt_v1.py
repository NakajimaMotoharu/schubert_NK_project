"""Original independent Session/Auth Throwable graphs; no held classifier or actual JDBC operation."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/api/security/'
NAME=PREFIX+'AuthenticationService'
ATTEMPTS=PREFIX+'LoginAttemptRepository'
AUDIT=PREFIX+'LoginAuditWriter'
MAIN_UNITS={NAME:dict(module='api',name=NAME,sha256='453a743084bbbe3d8cd859db1246faee5c27af1cc3f46484cb1ea07e98baee51'),ATTEMPTS:dict(module='api',name=ATTEMPTS,sha256='ed47df13b0b33a93bdfea58f0998bf299361c22b463c6e49a679df13a026bc02'),AUDIT:dict(module='api',name=AUDIT,sha256='e78c47b80b4037897a2ec8e3455759ebe183af845c28ce37e7f10833a7faee8b')}
CLOSURES={n:[n] for n in MAIN_UNITS}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'AuthenticationJdbcBoundary329Test':3}
PINS={'AuthenticationJdbcBoundary329Test':'6274073c13052b2b705937cd7c7f5e4744f76a04d18dc2ffdcd3d4b51d4de791'}
ROOT=data.ROOT
TESTS={'AuthenticationJdbcBoundary329Test':ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AuthenticationJdbcBoundary329Test.java'}
PUBLIC_READS={"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthContextCodec.java":"6cbdc8b0bc006e036ac3e127685d06c19bbb3c1e05d854cb52c8620d6a6065d6","src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/ContextHash.java":"9b0714ec9dc88f3f15e11341d71d873250fee8436ebad03b3fb1079060392581","src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthSessionService.java":"1ec3c856c555f77de597745defbbd6ea6f60292013117a44daf81e78a5f5eda8","src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/SessionAuditWriter.java":"173393177007aeb17a945ae37894e4d4a4c8b9b7f386765628bdbede6d7ebb6d","src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthenticationInfrastructureException.java":"4b64f5d458370b67b3f5f156ffb879151eb69c30fbe9819660e70cc81e55a402"}
EXTRAS={}
FIXTURES={}
SESSION='PG17740-AUTH-BORROWED-BOUNDARY-ORIGINAL3'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17740-auth-borrowed-boundary-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17728-current2804-revocation-graph-registry-v1/manifest.json','0a9215529d00fa998c6c81a4e0c6cdfc2dfab988988a12a679f8d4edbcbb58c5')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test(?:\s*@Timeout\([^)]*\))?\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert next(v.removeprefix('package ').removesuffix(';') for v in text.splitlines() if v.startswith('package '))+'.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in PUBLIC_READS.items():assert data.sha((ROOT/path).read_bytes())==data.sha((COMPILE/'snapshot'/path).read_bytes())==current[path]==pin
    for path,pin in EXTRAS.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    for row in MAIN_UNITS.values():
        text=(ROOT/source_path(row)).read_text()
        assert not any(v in text for v in ['TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec','DriverManager','RootStartupContext','ServiceProcessResources'])
    test=TESTS['AuthenticationJdbcBoundary329Test'].read_text()
    assert 'new AuthContextCodec("v1", new byte[32], null, null)' in test and 'new char[3]' in test
    assert 'assertEquals(0, fixture.connectionCloses)' in test and 'assertEquals(0, fixture.commits)' in test and 'assertEquals(0, fixture.rollbacks)' in test
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,inMemoryCredentialBufferAndAclValuesOnly=False,testOwnSecureRandomFixtureBytesGenerated=False,publicFixedUuidFixtureOnly=False,syntheticScenarioPublisherCallbackInvoked=False,stubDescriptorContentHashNotVerified=False,realRuntimeCredentialOrKeyLoaded=False,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=True,publicSourceReadHashes=PUBLIC_READS,testPublicSourceRead=False,syntheticPermitRecordConstructionOnly=False,nativeNamedReadNullGuardOnlyInvoked=False,independentModuleLocalThrowableGraphsOnly=False,syntheticBorrowedAuthenticationJdbcFaultPortsOnly=True,publicZeroAuthCodecFixtureBytes=32,jdkSecureRandomObjectsConstructed=2,jdkSha256ObjectsConstructed=1,jdkProviderInternalEntropyReads=None,sessionIssueNotCalledByFixedFalsePredicateAndSourceProof=True,junitTimeoutSeparateFrameworkWorkerOnly=True,actualPermitNamespaceLookups=0,actualRootOsAdmissionInvoked=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17740-auth-borrowed-boundary-three-pt-v1';run.OUT=data.BASE/'PG17740-auth-borrowed-boundary-three-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/AuthBorrowedBoundaryThreeCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['AuthenticationJdbcBoundary329Test'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
