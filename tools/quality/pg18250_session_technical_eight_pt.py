"""Four technical row and fixed exception contracts, no session/auth/commit/graph."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
ROOT=data.ROOT
PREFIX='dev/codex/schubert/nk/api/application/'
MAIN_UNITS={"dev/codex/schubert/nk/web/session/WebSessionRow":{"module":"web","name":"dev/codex/schubert/nk/web/session/WebSessionRow","sha256":"13d4d3f0b7938c5cb790a539817efeaf9453e05b25238fa7fb3baba1b2b8525b"},"dev/codex/schubert/nk/web/security/LoginFormRejectedException":{"module":"web","name":"dev/codex/schubert/nk/web/security/LoginFormRejectedException","sha256":"ee5feba42de3f8a4275f36e412226878e4f9a1edc6bb1c4813d127b614c3f294"},"dev/codex/schubert/nk/web/session/OperationTokenConflictException":{"module":"web","name":"dev/codex/schubert/nk/web/session/OperationTokenConflictException","sha256":"888084c0b0fcd8c4d5c85cfc2578c13f0e04ff5ff959d4205675568a84b2d118"},"dev/codex/schubert/nk/api/messaging/inbound/CommittedFatalInboundException":{"module":"api","name":"dev/codex/schubert/nk/api/messaging/inbound/CommittedFatalInboundException","sha256":"3819e7ff6b7bda704dd560bb99650bb343aa352da7ab9c4987c4806eb21d4334"}}
CLOSURES={n:[n] for n in MAIN_UNITS}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'SessionTechnicalValueContractTest':8}
PINS={'SessionTechnicalValueContractTest':'0693d069c344dd8201c15c03cec259ab4e42f0a7ad42adbf178528dd8b44bb8b'}
TESTS={'SessionTechnicalValueContractTest':ROOT/'tools/quality/architecture/SessionTechnicalValueContractTest.java'}
PUBLIC_READS={"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionPayloadIdentity.java":"f669b82c1ebce568c46198438b01ce65e9133eb1a50e7d94725ef060d3e1e25d","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/EncryptedSessionPayload.java":"b2d8816f5704d9d5d879908bf6ae5f4e95d436c1397b5e6ad71b78d09c45d799"}
EXTRAS={}
FIXTURES={}
SESSION='PG18250-SESSION-TECHNICAL8'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG18249-session-technical-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG18238-current2937-media-display-registry-v1/manifest.json','0a8a2f43c4eed352e40b73003297244475c34bafe48df79f1899b7c818ee0358')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&set(old['fullSourceUnits'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative=='tools/quality/architecture/SessionTechnicalValueContractTest.java'
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        suite=next(v.removeprefix('package ').removesuffix(';') for v in text.splitlines() if v.startswith('package '))+'.'+name
        assert suite not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','getConnection(','System.getenv(','Runtime.getRuntime','addShutdownHook','removeShutdownHook','preserveFatal(','attachSecondary(','Executors.','new Thread','randomUUID','Instant.now','MessageDigest'])
    for path,pin in PUBLIC_READS.items():assert data.sha((ROOT/path).read_bytes())==data.sha((COMPILE/'snapshot'/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,independentNewQualityTests=8,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=0,pureSessionTechnicalValuesOnly=True,syntheticEncryptedPayloadMetadataOnly=True,actualPayloadEncryptionOrDecryption=False,jdkNamedTimeZoneInitializationInvoked=False,businessDateConversionInvoked=False,jdkTimezoneProviderCallsAndResourceReads=None,actualAdminMutationOrAuthorization=False,actualBusinessProviderInvoked=False,actualThrowableGraphTraversal=False,publicFixedUuidFixtureOnly=True,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg18250-session-technical-eight-pt-v1';run.OUT=data.BASE/'PG18250-session-technical-eight-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/SessionTechnicalEightCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['SessionTechnicalValueContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
