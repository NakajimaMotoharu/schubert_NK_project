"""Two independent User display Sources; local role guard, no external authorization/authentication or DB."""
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
MAIN_UNITS={"dev/codex/schubert/nk/web/logging/ClaimedWebLog":{"module":"web","name":"dev/codex/schubert/nk/web/logging/ClaimedWebLog","sha256":"5aad3ffe6cf9fa219708a27b04a58d98fb67c0e16a4f44561296d34cc87acdfb"}}
CLOSURES={"dev/codex/schubert/nk/web/logging/ClaimedWebLog":["dev/codex/schubert/nk/web/logging/ClaimedWebLog"]}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'WebLogClaimValueContractTest':6}
PINS={'WebLogClaimValueContractTest':'a10260c2f4051c4b702b0d8b1595dc0e9009e15c643363d11996f7f308671860'}
TESTS={'WebLogClaimValueContractTest':ROOT/'tools/quality/architecture/WebLogClaimValueContractTest.java'}
PUBLIC_READS={"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebLogPayloadIdentity.java":"b8279f85ba0b8f52466f28c8908f03cb0420556722d9711e4e11168c078c80ca","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/EncryptedWebLogPayload.java":"98cd13d71d07dadf4bb2a65b2d40f9222c0ee1f7d35bc6dfcd46abd1724c9956"}
EXTRAS={}
FIXTURES={}
SESSION='PG18380-WEBLOG-CLAIM6'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG18379-weblog-claim-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG18368-current3002-qn-search-registry-v1/manifest.json','a72db411c88562b44ff0de8b303d792f9b8ff81011169744644baa204389f65b')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&set(old['fullSourceUnits'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative=='tools/quality/architecture/WebLogClaimValueContractTest.java'
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
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,independentNewQualityTests=6,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=0,pureWebLogClaimValueOnly=True,publicSyntheticUuidFixture=True,publicKeyVersionLabelOnly=True,syntheticPayloadBufferOnly=True,localDisplayRoleGuardInvoked=False,requestScopedSyntheticSearchFormBindingInvoked=False,fixedOffsetJstDisplayFormattingInvoked=False,publicSyntheticAuthenticationContextValueOnly=False,syntheticAuthenticationContextValueUsed=False,nfcAndUtf8ValidationInvoked=False,memorySessionPrincipalValueOnly=False,jdkNamedTimeZoneInitializationInvoked=False,maintenanceBusinessDateMethodInvoked=False,jdkTimezoneProviderCallsAndResourceReads=None,actualExternalAuthorizationOrMutation=False,actualBusinessProviderInvoked=False,actualThrowableGraphTraversal=False,publicFixedUuidFixtureOnly=True,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg18380-weblog-claim-six-pt-v1';run.OUT=data.BASE/'PG18380-weblog-claim-six-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/WebLogClaimSixCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['WebLogClaimValueContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
