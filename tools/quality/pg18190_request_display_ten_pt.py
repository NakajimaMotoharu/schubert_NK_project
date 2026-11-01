"""Four request-only display contracts; pure form/locator/DTO values, no HTTP/auth/DB/Root."""
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
MAIN_UNITS={"dev/codex/schubert/nk/web/view/QuestionSubmitViewModel":{"module":"web","name":"dev/codex/schubert/nk/web/view/QuestionSubmitViewModel","sha256":"13b364659934a4d7cd92bbce8b7a66b1f1e7fb9877a40fad50ac57bdbdc6f053"},"dev/codex/schubert/nk/web/view/QuestionAcceptedViewModel":{"module":"web","name":"dev/codex/schubert/nk/web/view/QuestionAcceptedViewModel","sha256":"a6fdfd6dab35fc6bf9ed401e984253eee589f5d3d17b3d2fe731f10898bdc4e8"},"dev/codex/schubert/nk/web/view/UserCreateViewModel":{"module":"web","name":"dev/codex/schubert/nk/web/view/UserCreateViewModel","sha256":"a2500110cedb6b4b38221a483191d9164f757709e404dcb190eaf1a869a80e82"},"dev/codex/schubert/nk/web/receipt/ReceiptReference":{"module":"web","name":"dev/codex/schubert/nk/web/receipt/ReceiptReference","sha256":"b8dff7e53fd4b8646817eb6673a57479d3746a37d01585c3e35c2eee749ff829"}}
CLOSURES={n:[n] for n in MAIN_UNITS}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'RequestDisplayContractTest':10}
PINS={'RequestDisplayContractTest':'a15b7b47560b2b5590902e1bcf8907993c187c2e267dd82149032fcaf980807b'}
TESTS={'RequestDisplayContractTest':ROOT/'tools/quality/architecture/RequestDisplayContractTest.java'}
PUBLIC_READS={"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/form/QuestionSubmitForm.java":"725f0fbe38aaec853e50da6eb5ea060eb0a8fe7e4a18faa5ddb9febce3f03b6f","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/form/UserCreateForm.java":"5b599ddb57dfd4ba0b8a89547567b1d48bedb5d6ac09439c5dc0abd6cda25b86","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionOperationToken.java":"6a982c339aef53a2297725c114a8cfe023557b3cf36a953c599916e48eaa6f57","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionPrincipal.java":"29af626632ac4c2727f9d0963c3967cb0be7eda57daf762a482268c467dc9232","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/TopBarViewModel.java":"16afe37089d96cb31e7849e5bf5e289196588c6f4b8e1d4732fd402887e24a09","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/header/AuthenticationContext.java":"aaa18a4c954a425c943e8c30ea1752b665b249e86d8f1767e9e37f4aa61a6b66","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/UserRole.java":"b68402e5705ca2ac5093a1b98a44de5a9f45ed69cb9b231658b4903c51e0bf69","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/question/QuestionDetailResponseData.java":"c3caddc69e01cca280fb7e06822c9748ae38d142c81b47df8d447b0a049dcbdf","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/PayloadSemanticValidator.java":"f2b7b23daa77b820b218089247a82adb0daac8fe8188287b42a8b69c62a502a9","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/TypedFieldValues.java":"1f109d93cb6e8e802ab1a9c0484cfe48689253a34f1322111dfbce58bd0a8cde","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/time/JstWireTimestamp.java":"277dc29b07a2531b8c7d8307c0226762ff6b76fa2caef3849007bbcaf6aaffbc","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/FieldValueSet.java":"2c292124a30ee4ed275ad2d43818b46c73c8f5648edd60914992da786e6f555b","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/FieldValue.java":"6f50d333720aaedf58b714be1f84c298297ae80398e8b8f7afb0ec7341d98041","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/TypedPayloadValues.java":"5db4c6b32786b0803334a4c8f7949bf4be0b6936a71c94658f6cef78e970286b","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/LayoutId.java":"87c8f01b5f84f211a8902d323eba221d11dc6b6add1cfe2a514fdbb68e82bc24","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/QuestionId.java":"a0c57ac09481d1a033b35faf9059c7f9c2d152ad62563f9099078c97e3febf3c","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/AnswerState.java":"bf012f1ce68157a7d4b62e17f6f996362454d58684301de5fb079d9e2281d29c","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/IdValue.java":"3bf4d89066c5da24649c0f970e5f0655c37d34f0bbd6120539b9a518c4905cd1","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/LayoutValidationException.java":"b99e562fe3afd1f1e11a7ff415f25999c14e46016d5a115022706d4f8674a9df"}
EXTRAS={}
FIXTURES={}
SESSION='PG18190-REQUEST-DISPLAY10'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG18189-request-display-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG18178-current2907-inbox-stored-metadata-registry-v1/manifest.json','386637fbdac8b7eb7367b065c0fa6340f5c25ca9ce132ed37580885afc8d2778')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&set(old['fullSourceUnits'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative=='tools/quality/architecture/RequestDisplayContractTest.java'
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
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,independentNewQualityTests=10,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=0,pureRequestDisplayValuesOnly=True,requestScopedSyntheticFormBindingInvoked=True,syntheticOperationTokenValuesOnly=True,fixedUtcToJstWireDisplayFormattingInvoked=True,testOwnedCharBufferWiped=True,publicSyntheticAuthenticationContextValueOnly=True,syntheticAuthenticationContextValueUsed=True,nfcAndUtf8ValidationInvoked=True,memorySessionPrincipalValueOnly=True,jdkNamedTimeZoneInitializationInvoked=True,maintenanceBusinessDateMethodInvoked=False,jdkTimezoneProviderCallsAndResourceReads=None,actualAdminMutationOrAuthorization=False,actualBusinessProviderInvoked=False,actualThrowableGraphTraversal=False,publicFixedUuidFixtureOnly=True,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg18190-request-display-ten-pt-v1';run.OUT=data.BASE/'PG18190-request-display-ten-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/RequestDisplayTenCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['RequestDisplayContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
