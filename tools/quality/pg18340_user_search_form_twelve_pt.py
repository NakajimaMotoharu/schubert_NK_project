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
MAIN_UNITS={"dev/codex/schubert/nk/web/form/UserSearchForm":{"module":"web","name":"dev/codex/schubert/nk/web/form/UserSearchForm","sha256":"d00242a9223aa067fc609945fc6e5bf382429c121b3c49600a3c3a056778c906"}}
CLOSURES={"dev/codex/schubert/nk/web/form/UserSearchForm":["dev/codex/schubert/nk/web/form/UserSearchForm"]}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'UserSearchInputContractTest':12}
PINS={'UserSearchInputContractTest':'efe1a92efbd88de4013a21ec87c619510c38499c66c9e3680a854f2ae4733850'}
TESTS={'UserSearchInputContractTest':ROOT/'tools/quality/architecture/UserSearchInputContractTest.java'}
PUBLIC_READS={"src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/admin/UserSearchRequestData.java":"58ff4b6dbd140e907ed8d9dd7d9f5225be0972ef6d9fb506a97ffb9c8e11ec7a","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/TypedFieldValues.java":"1f109d93cb6e8e802ab1a9c0484cfe48689253a34f1322111dfbce58bd0a8cde","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/UserRole.java":"b68402e5705ca2ac5093a1b98a44de5a9f45ed69cb9b231658b4903c51e0bf69","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/UserState.java":"39ae05a1645dd3297a674075a8cb63832ccdb31f00921e1167dfa6eb2be8c13c"}
EXTRAS={}
FIXTURES={}
SESSION='PG18340-USER-SEARCH12'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG18339-user-search-form-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG18328-current2964-carrier-catalog-registry-v1/manifest.json','462e898663d60b1c68c54956fffe07e494472fa187a13b094ed44247d780705d')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&set(old['fullSourceUnits'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative=='tools/quality/architecture/UserSearchInputContractTest.java'
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
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,independentNewQualityTests=12,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=0,pureUserSearchFormOnly=True,localDisplayRoleGuardInvoked=False,requestScopedSyntheticSearchFormBindingInvoked=True,fixedOffsetJstDisplayFormattingInvoked=False,publicSyntheticAuthenticationContextValueOnly=False,syntheticAuthenticationContextValueUsed=False,nfcAndUtf8ValidationInvoked=True,memorySessionPrincipalValueOnly=False,jdkNamedTimeZoneInitializationInvoked=False,maintenanceBusinessDateMethodInvoked=False,jdkTimezoneProviderCallsAndResourceReads=None,actualExternalAuthorizationOrMutation=False,actualBusinessProviderInvoked=False,actualThrowableGraphTraversal=False,publicFixedUuidFixtureOnly=False,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg18340-user-search-form-twelve-pt-v1';run.OUT=data.BASE/'PG18340-user-search-form-twelve-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/UserSearchTwelveCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['UserSearchInputContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
