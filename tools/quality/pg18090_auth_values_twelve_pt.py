"""Nine pure auth DTO/catalog Sources with public synthetic values; no authentication/session issuance."""
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
MAIN_UNITS={"dev/codex/schubert/nk/api/security/LoginAccount":{"module":"api","name":"dev/codex/schubert/nk/api/security/LoginAccount","sha256":"f78519bcbdcb4d906fa63010239a8f31398f1564d5fdb1ffcd9602e3dac4b2a0"},"dev/codex/schubert/nk/api/security/IssuedContext":{"module":"api","name":"dev/codex/schubert/nk/api/security/IssuedContext","sha256":"e63b4f5bc96fef9df4b42ca1bff2de29098ab1139d96d49d4aedb1dbbc991ec1"},"dev/codex/schubert/nk/api/security/RevokedContext":{"module":"api","name":"dev/codex/schubert/nk/api/security/RevokedContext","sha256":"103bff044f7e8e66b214fbb4d680fd9644afdf81ee88d4eef9411e6e4c65d8f0"},"dev/codex/schubert/nk/api/security/LockedLoginAttempt":{"module":"api","name":"dev/codex/schubert/nk/api/security/LockedLoginAttempt","sha256":"71655d2fa7fa5fe730d9d1ca20e7f713e669760f32af4437fed064873066e7a4"},"dev/codex/schubert/nk/api/security/LoginResult":{"module":"api","name":"dev/codex/schubert/nk/api/security/LoginResult","sha256":"d5efa4df9df7e10fd959c1f515e624fee369b0ce290583ffdb84f459c904f832"},"dev/codex/schubert/nk/api/domain/Role":{"module":"api","name":"dev/codex/schubert/nk/api/domain/Role","sha256":"e60e607a3f09e860ad7c28c62555672ebdca3e8590d98fcffa45f82b5c2f5fe8"},"dev/codex/schubert/nk/api/security/LoginAuditReason":{"module":"api","name":"dev/codex/schubert/nk/api/security/LoginAuditReason","sha256":"4710a12a0c95eb7dfa45dd67d53a69b8a08dd25b70d94d7ddf172da9a9e308f6"},"dev/codex/schubert/nk/api/security/SessionRevocationReason":{"module":"api","name":"dev/codex/schubert/nk/api/security/SessionRevocationReason","sha256":"213a5fb2c04bf79b447f0a981f4f8b0eb3834b948476f8b2ddadb56b472cdd74"},"dev/codex/schubert/nk/api/security/AuthenticationContextException":{"module":"api","name":"dev/codex/schubert/nk/api/security/AuthenticationContextException","sha256":"5a0e03c3b5aa5c14f41b8273bca454409288b88b50190f23d1d59982be8552ce"}}
CLOSURES={"dev/codex/schubert/nk/api/security/LoginAccount":["dev/codex/schubert/nk/api/security/LoginAccount"],"dev/codex/schubert/nk/api/security/IssuedContext":["dev/codex/schubert/nk/api/security/IssuedContext"],"dev/codex/schubert/nk/api/security/RevokedContext":["dev/codex/schubert/nk/api/security/RevokedContext"],"dev/codex/schubert/nk/api/security/LockedLoginAttempt":["dev/codex/schubert/nk/api/security/LockedLoginAttempt"],"dev/codex/schubert/nk/api/security/LoginResult":["dev/codex/schubert/nk/api/security/LoginResult","dev/codex/schubert/nk/api/security/LoginResult$Failure","dev/codex/schubert/nk/api/security/LoginResult$Success"],"dev/codex/schubert/nk/api/domain/Role":["dev/codex/schubert/nk/api/domain/Role"],"dev/codex/schubert/nk/api/security/LoginAuditReason":["dev/codex/schubert/nk/api/security/LoginAuditReason"],"dev/codex/schubert/nk/api/security/SessionRevocationReason":["dev/codex/schubert/nk/api/security/SessionRevocationReason"],"dev/codex/schubert/nk/api/security/AuthenticationContextException":["dev/codex/schubert/nk/api/security/AuthenticationContextException"]}
METADATA={"dev/codex/schubert/nk/api/security/LoginResult"}
METADATA_FLAGS={"dev/codex/schubert/nk/api/security/LoginResult":1537}
GENERATED_METADATA=set()
COUNTS={'AuthImmutableValueContractTest':12}
PINS={'AuthImmutableValueContractTest':'108a9d3b2834c11fdb82b61024628b8d80a78b9d163cb41d868cc66caaa8428f'}
TESTS={'AuthImmutableValueContractTest':ROOT/'tools/quality/architecture/AuthImmutableValueContractTest.java'}
PUBLIC_READS={"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginAttemptState.java":"393f52726e83c3ea52fe34c7385c0da413d49306a476894255602fe82880c352","src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginAttemptKind.java":"493c8b03e7791a044be87f4fadeb1c7c7c95588aba1174cb38baa0b5a3b56f7b","src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthContextIdentity.java":"b9dbed4233756c481cdb747d96f6de8843e9d910a4c18f51c30454d16130d7dd","src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthenticatedActor.java":"830a87635d2782354fe9c03e5d7612a2ab88364cdc31157b501fbf7baf361469","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/header/AuthenticationContext.java":"aaa18a4c954a425c943e8c30ea1752b665b249e86d8f1767e9e37f4aa61a6b66","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/header/ResultCode.java":"ade5ac5514ed62f2be57419eeab2d3a5e27da98a1c6607621be60e3a11c162f4"}
EXTRAS={}
FIXTURES={}
SESSION='PG18090-AUTH-IMMUTABLE12'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG18089-auth-values-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG18078-current2871-inspection-values-registry-v1/manifest.json','8ad7ee8443c1b439de4afaec3832ed534511b37a4c6e8016b85f026ed8c6fdb7')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&set(old['fullSourceUnits'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative=='tools/quality/architecture/AuthImmutableValueContractTest.java'
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
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,independentNewQualityTests=12,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=0,pureAuthImmutableValuesAndCatalogOnly=True,actualAdminMutationOrAuthorization=False,actualProviderInvoked=False,actualThrowableGraphTraversal=False,publicFixedUuidFixtureOnly=True,publicSyntheticAuthenticationContextValueOnly=True,syntheticAuthenticationContextValueUsed=True,directNumericIpLiteralParsingInvoked=True,explicitDnsLookupInvoked=False,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg18090-auth-values-twelve-pt-v1';run.OUT=data.BASE/'PG18090-auth-values-twelve-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/AuthValuesTwelveCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['AuthImmutableValueContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
