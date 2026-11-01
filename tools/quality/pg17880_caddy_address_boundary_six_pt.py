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
NAME='dev/codex/schubert/nk/web/security/CaddyClientAddressResolver'
MAIN_UNITS={NAME:dict(module='web',name=NAME,sha256='f5b117c9d9a9473a45b602c3ce97a6e92198b27490ac284e7281956cd7b42f37')}
CLOSURES={NAME:[NAME]}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'CaddyAddressBoundaryContractTest':6}
PINS={'CaddyAddressBoundaryContractTest':'f0612ddb3090a317163f1793408c724796c1ab818fde23b0942192283178c6c0'}
ROOT=data.ROOT
TESTS={'CaddyAddressBoundaryContractTest':ROOT/'tools/quality/architecture/CaddyAddressBoundaryContractTest.java'}
PUBLIC_READS={'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/LoginClientAddress.java':'4e6cfb538744d81daf4c5e132b729b6800b1ee3f3aa6682ad06e46c9aabb56c5','src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/CaddyRequestRejectedException.java':'d6c50441cde4887be9a0d9585bb41512ee5228042419b78d48437a1f88620967'}
EXTRAS={}
FIXTURES={}
SESSION='PG17880-CADDY-ADDRESS-BOUNDARY6'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17879-caddy-address-boundary-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17858-current2827-codefree17-registry-v1/manifest.json','1979776c9e85f43e9e69ed30ceb1dc7444c5bc5ad09b044f479eefff4c46d40f')
    assert old['source']==SOURCE and old['fullSourceUnits'][NAME]['four100'] is False
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative=='tools/quality/architecture/CaddyAddressBoundaryContractTest.java'
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
    assert 'InetAddress.ofLiteral(peer.value()).isLoopbackAddress()' in text
    assert not any(v in text for v in ['getByName','getSession','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec','RootStartupContext','ServiceProcessResources'])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,inMemoryCredentialBufferAndAclValuesOnly=False,testOwnSecureRandomFixtureBytesGenerated=False,publicFixedUuidFixtureOnly=False,syntheticScenarioPublisherCallbackInvoked=False,stubDescriptorContentHashNotVerified=False,realRuntimeCredentialOrKeyLoaded=False,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=False,publicSourceReadHashes=PUBLIC_READS,testPublicSourceRead=False,syntheticPermitRecordConstructionOnly=False,nativeNamedReadNullGuardOnlyInvoked=False,independentModuleLocalThrowableGraphsOnly=False,syntheticOwnedReceiptJdbcFaultPortsOnly=False,memoryServletHeaderFixtureOnly=True,directNumericIpLiteralParsingInvoked=True,explicitDnsLookupInvoked=False,networkCountScope='PROJECT_EXPLICIT_TRANSPORT_CALLS_NOT_JDK_INTERNAL_INITIALIZATION',platformJdkInitializationEffects=None,junitTimeoutSeparateFrameworkWorkerOnly=False,actualPermitNamespaceLookups=0,actualRootOsAdmissionInvoked=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17880-caddy-address-boundary-six-pt-v1';run.OUT=data.BASE/'PG17880-caddy-address-boundary-six-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/CaddyAddressBoundarySixCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['CaddyAddressBoundaryContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
