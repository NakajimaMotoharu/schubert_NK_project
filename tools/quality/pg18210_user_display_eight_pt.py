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
MAIN_UNITS={"dev/codex/schubert/nk/web/view/UserListViewModel":{"module":"web","name":"dev/codex/schubert/nk/web/view/UserListViewModel","sha256":"3ab853dea7f6e95aa94c6553180ad7d355c1af6761636dc9828a9ada969f5eb6"},"dev/codex/schubert/nk/web/view/UserDetailViewModel":{"module":"web","name":"dev/codex/schubert/nk/web/view/UserDetailViewModel","sha256":"c4d5545b5424c3fabc6b5563bd77e29f507a3f97c69ac2ae89ba34c680e902e3"}}
CLOSURES={"dev/codex/schubert/nk/web/view/UserListViewModel":["dev/codex/schubert/nk/web/view/UserListViewModel","dev/codex/schubert/nk/web/view/UserListViewModel$Row"],"dev/codex/schubert/nk/web/view/UserDetailViewModel":["dev/codex/schubert/nk/web/view/UserDetailViewModel"]}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'UserDisplayContractTest':8}
PINS={'UserDisplayContractTest':'74e37d277cb69b31bbae8b2da0caceb5abe7e7c9cde7714309a2a0b3ef52c970'}
TESTS={'UserDisplayContractTest':ROOT/'tools/quality/architecture/UserDisplayContractTest.java'}
PUBLIC_READS={"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/form/UserSearchForm.java":"d00242a9223aa067fc609945fc6e5bf382429c121b3c49600a3c3a056778c906","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/PageViewModel.java":"29de4e2f08b7d0ca5bcb61952e3e50b6d7a501846b61da67e02e3f7e882a6593","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionPrincipal.java":"29af626632ac4c2727f9d0963c3967cb0be7eda57daf762a482268c467dc9232","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/TopBarViewModel.java":"16afe37089d96cb31e7849e5bf5e289196588c6f4b8e1d4732fd402887e24a09","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/header/AuthenticationContext.java":"aaa18a4c954a425c943e8c30ea1752b665b249e86d8f1767e9e37f4aa61a6b66","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/admin/UserRecord.java":"5c74402ddfb935a3a7f59af52fa6758859c43d67ceedb6f0e082ad7548ba392a","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/admin/UserDetailResponseData.java":"38f7177993c2eba0e5fce69a85d55ec420a25b9d6cb1900bbaa4ea49121607cf","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/common/PagedResponseData.java":"54c61eaac197e54d18a76d5c7f129d3b88f494e2022cc764155200ac44e70591","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/UserState.java":"39ae05a1645dd3297a674075a8cb63832ccdb31f00921e1167dfa6eb2be8c13c","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/UserRole.java":"b68402e5705ca2ac5093a1b98a44de5a9f45ed69cb9b231658b4903c51e0bf69","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/UserId.java":"482cd1b41f0f5e2408086ca0ea4e6742a2a1c0c80bc541249261c9c339564383","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/IdValue.java":"3bf4d89066c5da24649c0f970e5f0655c37d34f0bbd6120539b9a518c4905cd1","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/TypedFieldValues.java":"1f109d93cb6e8e802ab1a9c0484cfe48689253a34f1322111dfbce58bd0a8cde"}
EXTRAS={}
FIXTURES={}
SESSION='PG18210-USER-DISPLAY8'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG18209-user-display-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG18198-current2917-request-display-registry-v1/manifest.json','6551658fcc9bad07e701e3eb28bfbdbd51d660dd9606b17d6e28ba5e8a163054')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&set(old['fullSourceUnits'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative=='tools/quality/architecture/UserDisplayContractTest.java'
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
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,independentNewQualityTests=8,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=0,pureUserDisplayValuesOnly=True,localDisplayRoleGuardInvoked=True,requestScopedSyntheticSearchFormBindingInvoked=True,fixedOffsetJstDisplayFormattingInvoked=True,publicSyntheticAuthenticationContextValueOnly=True,syntheticAuthenticationContextValueUsed=True,nfcAndUtf8ValidationInvoked=True,memorySessionPrincipalValueOnly=True,jdkNamedTimeZoneInitializationInvoked=False,maintenanceBusinessDateMethodInvoked=False,jdkTimezoneProviderCallsAndResourceReads=None,actualExternalAuthorizationOrMutation=False,actualBusinessProviderInvoked=False,actualThrowableGraphTraversal=False,publicFixedUuidFixtureOnly=False,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg18210-user-display-eight-pt-v1';run.OUT=data.BASE/'PG18210-user-display-eight-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/UserDisplayEightCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['UserDisplayContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
