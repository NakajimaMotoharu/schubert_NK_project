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
MAIN_UNITS={"dev/codex/schubert/nk/web/form/QuestionSearchForm":{"module":"web","name":"dev/codex/schubert/nk/web/form/QuestionSearchForm","sha256":"1308c621d4fb8673cae5440a7691ba1a17bf20b13f53251ab23dfb220f4351b4"},"dev/codex/schubert/nk/web/form/NotificationSearchForm":{"module":"web","name":"dev/codex/schubert/nk/web/form/NotificationSearchForm","sha256":"2ef67ea5d4b3829d5c48b8e2c6734473d3cdca1e09f24b7ff8c2859053297cfa"}}
CLOSURES={"dev/codex/schubert/nk/web/form/QuestionSearchForm":["dev/codex/schubert/nk/web/form/QuestionSearchForm"],"dev/codex/schubert/nk/web/form/NotificationSearchForm":["dev/codex/schubert/nk/web/form/NotificationSearchForm"]}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={"QuestionSearchInputContractTest":14,"NotificationSearchInputContractTest":12}
PINS={"QuestionSearchInputContractTest":"8be5ab3dc80b86f94cdc48ac49cfcfa0a439766c43a4db5b51c4c32011e08489","NotificationSearchInputContractTest":"3cd834e9f5d8e41ba0ac27d90ec9af2f5b4d7ea670099a03c5547817fff77717"}
TESTS={n:ROOT/('tools/quality/architecture/'+n+'.java') for n in COUNTS}
PUBLIC_READS={"src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/TypedFieldValues.java":"1f109d93cb6e8e802ab1a9c0484cfe48689253a34f1322111dfbce58bd0a8cde","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/UserRole.java":"b68402e5705ca2ac5093a1b98a44de5a9f45ed69cb9b231658b4903c51e0bf69","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/question/QuestionSearchRequestData.java":"e93c0affdb135f6af27adbc223d5de106748df8514188513a3ab4f66687c9128","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/question/NotificationSearchRequestData.java":"c33f1d8853f19f0b927b903f2856d6029bc807f666de8700f26c8e062ec600e2","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/AnswerState.java":"bf012f1ce68157a7d4b62e17f6f996362454d58684301de5fb079d9e2281d29c","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/NotificationType.java":"0226b90638a1c81e4a60cedb85ac3aa261069a982a745d79711a691bc0f76753"}
EXTRAS={}
FIXTURES={}
SESSION='PG18360-QUESTION-NOTIFICATION-SEARCH26'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG18359-question-notification-search-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG18348-current2976-user-search-registry-v1/manifest.json','b8906f29f42b0fb00d358003843fc7ba531c752f4653c0221bb8f300b016eab7')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&set(old['fullSourceUnits'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative in {'tools/quality/architecture/'+n+'.java' for n in COUNTS}
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
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,independentNewQualityTests=26,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=0,pureQuestionNotificationSearchFormsOnly=True,localSearchRoleGuardInvoked=True,localDisplayRoleGuardInvoked=False,requestScopedSyntheticSearchFormBindingInvoked=True,fixedOffsetJstDisplayFormattingInvoked=True,publicSyntheticAuthenticationContextValueOnly=False,syntheticAuthenticationContextValueUsed=False,nfcAndUtf8ValidationInvoked=True,memorySessionPrincipalValueOnly=False,jdkNamedTimeZoneInitializationInvoked=False,maintenanceBusinessDateMethodInvoked=False,jdkTimezoneProviderCallsAndResourceReads=None,actualExternalAuthorizationOrMutation=False,actualBusinessProviderInvoked=False,actualThrowableGraphTraversal=False,publicFixedUuidFixtureOnly=False,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg18360-question-notification-search26-pt-v1';run.OUT=data.BASE/'PG18360-question-notification-search26-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/QuestionNotificationSearch26CurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['QuestionSearchInputContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,)+tuple(p for p in TESTS.values() if p!=run.NEW_TEST);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
