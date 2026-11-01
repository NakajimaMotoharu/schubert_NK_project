"""Six revocation projection/fixed exception contracts, no actual claim/send/file or credentials."""
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
MAIN_UNITS={"dev/codex/schubert/nk/web/revocation/ClaimedRevocation":{"module":"web","name":"dev/codex/schubert/nk/web/revocation/ClaimedRevocation","sha256":"0d62d5d5c749ed7db388e0d96aacfda7bd8cc74edb07326abd945c61b33e2d4f"},"dev/codex/schubert/nk/web/revocation/RevocationFailureCode":{"module":"web","name":"dev/codex/schubert/nk/web/revocation/RevocationFailureCode","sha256":"7619c5d7d7f1e7904d5379123512e6a829691ab1eb2a06dd1305d44bdc7d6fe7"},"dev/codex/schubert/nk/web/logging/WebLogSendException":{"module":"web","name":"dev/codex/schubert/nk/web/logging/WebLogSendException","sha256":"86e86c4d60e6e522532e08bab5ead7c42a30d52cbc03f6b5ae0226fa510992e8"},"dev/codex/schubert/nk/web/messaging/CommittedFatalReplyException":{"module":"web","name":"dev/codex/schubert/nk/web/messaging/CommittedFatalReplyException","sha256":"0d2a1a7c5eceda3627e62e6d3f87a1868653fc7328a2d69e15c1ecc7ec605c12"},"dev/codex/schubert/nk/api/file/ServiceCredentialException":{"module":"bootstrap","name":"dev/codex/schubert/nk/api/file/ServiceCredentialException","sha256":"3fcb0a3417ddf3e02ed0076ff99b6911c373b80574c6630b1a86294e3b7d48c0"},"dev/codex/schubert/nk/api/file/InspectorCredentialException":{"module":"bootstrap","name":"dev/codex/schubert/nk/api/file/InspectorCredentialException","sha256":"316e8b5aa67665f816fb51f54b217f873b9c1b1df284393dcbb2aad1f397ad10"}}
CLOSURES={n:[n] for n in MAIN_UNITS}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'RevokeProjectionValueContractTest':10}
PINS={'RevokeProjectionValueContractTest':'e21fcb7838dbc3413bc0a835f39030aa91aed034e5520bd1c96c70fe4f6e924a'}
TESTS={'RevokeProjectionValueContractTest':ROOT/'tools/quality/architecture/RevokeProjectionValueContractTest.java'}
PUBLIC_READS={"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/revocation/RevocationPayloadIdentity.java":"ee2a5de2420d9fd0f73919a78de9a6b5cbfd8fa13836100f234bb33cc85b1252","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/revocation/EncryptedRevocationPayload.java":"cef3f699c0f4b9eb8d562ed2c131c8c23e389808d0e8fd08bc33144b0aa55d94","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/revocation/PendingRevocationRepository.java":"5c3cfd9965aa0e90666dc3344fe51513a9a3bb6fa51e2071d3f4290e3c028e4a"}
EXTRAS={}
FIXTURES={}
SESSION='PG18270-REVOKE-VALUES10'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG18269-revoke-values-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG18258-current2945-session-technical-registry-v1/manifest.json','b1d06d3872fbf6e666b494cf5324932164294e1b809f6802f3f558f32a8954fd')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&set(old['fullSourceUnits'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative=='tools/quality/architecture/RevokeProjectionValueContractTest.java'
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        suite=next(v.removeprefix('package ').removesuffix(';') for v in text.splitlines() if v.startswith('package '))+'.'+name
        assert suite not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','getConnection(','System.getenv(','Runtime.getRuntime','addShutdownHook','removeShutdownHook','preserveFatal(','attachSecondary(','Executors.','new Thread','randomUUID','Instant.now','MessageDigest'])
    for path,pin in PUBLIC_READS.items():assert data.sha((ROOT/path).read_bytes())==data.sha((COMPILE/'snapshot'/path).read_bytes())==current[path]==pin
    import classfile_code_metadata as metadata
    with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
        name='dev/codex/schubert/nk/web/revocation/PendingRevocationRepository.class'
        decoded=metadata.decode(jar.read(name),name)
        assert not any(m['name']=='<clinit>' for m in decoded['methods'])
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,independentNewQualityTests=10,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=0,pureRevokeProjectionValuesOnly=True,publicSyntheticThrowableCauseRetainedOnly=True,actualJmsIsolationOrCommitInvoked=False,repositoryPureMicrosecondGuardInvoked=True,actualClaimOrRetryInvoked=False,syntheticEncryptedPayloadMetadataOnly=True,actualPayloadEncryptionOrDecryption=False,jdkNamedTimeZoneInitializationInvoked=False,businessDateConversionInvoked=False,jdkTimezoneProviderCallsAndResourceReads=None,actualAdminMutationOrAuthorization=False,actualBusinessProviderInvoked=False,actualThrowableGraphTraversal=False,publicFixedUuidFixtureOnly=True,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg18270-revoke-values-ten-pt-v1';run.OUT=data.BASE/'PG18270-revoke-values-ten-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/RevokeValuesTenCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['RevokeProjectionValueContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
