"""Four distinct stored metadata value contracts; public bytes only, no HMAC/AES/keyring/DB."""
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
MAIN_UNITS={"dev/codex/schubert/nk/api/idempotency/Fingerprint":{"module":"api","name":"dev/codex/schubert/nk/api/idempotency/Fingerprint","sha256":"0b10a762ba66659b57aa3ae924030faa75f5a4cab1cbf7a06cc1b65002e05661"},"dev/codex/schubert/nk/api/idempotency/FingerprintVerification":{"module":"api","name":"dev/codex/schubert/nk/api/idempotency/FingerprintVerification","sha256":"cfa87222c236a4629d1556f081b073b0b2a99578dbc5db476372243d955f1110"},"dev/codex/schubert/nk/api/idempotency/EncryptedResponseSnapshot":{"module":"api","name":"dev/codex/schubert/nk/api/idempotency/EncryptedResponseSnapshot","sha256":"c7d2738376c3d732dfd9556d015c2a8ff91da469320db029a3368ed3d95eae22"},"dev/codex/schubert/nk/api/idempotency/BoundInboxExecution":{"module":"api","name":"dev/codex/schubert/nk/api/idempotency/BoundInboxExecution","sha256":"03914a804c99f24c16010075bf9854199049d4026a5e180c8fcc5d686fae8caa"}}
CLOSURES={n:[n] for n in MAIN_UNITS}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'StoredMetadataContractTest':6}
PINS={'StoredMetadataContractTest':'13a922da6094a6d7c436706bf40fcfec7cb29862adc79fa86aadb428f6c86ae7'}
TESTS={'StoredMetadataContractTest':ROOT/'tools/quality/architecture/StoredMetadataContractTest.java'}
PUBLIC_READS={"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/InboxExecution.java":"1b791d1eab0c318582bb27ce37f9f99cbb590901c7d8c4f03a0daaf42f2c31c1","src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/InboxExecutionStatus.java":"349b9813318d93b15eb334a5ea5de8bd24f5cbfde96cec8114eafa8150aec7bb"}
EXTRAS={}
FIXTURES={}
SESSION='PG18170-STORED-METADATA6'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG18169-inbox-stored-metadata-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG18158-current2901-error-values-registry-v1/manifest.json','6977565eaecd085346ce980d7326849d3c0863f6660e423cea66ff9a45d766a8')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&set(old['fullSourceUnits'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative=='tools/quality/architecture/StoredMetadataContractTest.java'
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
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,independentNewQualityTests=6,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=0,pureStoredMetadataValuesOnly=True,jdkNamedTimeZoneInitializationInvoked=False,businessDateConversionInvoked=False,jdkTimezoneProviderCallsAndResourceReads=None,actualAdminMutationOrAuthorization=False,actualBusinessProviderInvoked=False,actualThrowableGraphTraversal=False,publicFixedUuidFixtureOnly=True,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg18170-inbox-stored-metadata-six-pt-v1';run.OUT=data.BASE/'PG18170-inbox-stored-metadata-six-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/StoredMetadataSixCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['StoredMetadataContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
