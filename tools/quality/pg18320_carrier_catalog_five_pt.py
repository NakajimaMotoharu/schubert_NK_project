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
MAIN_UNITS={"dev/codex/schubert/nk/api/application/scenario/ScenarioQuerySnapshot":{"module":"api","name":"dev/codex/schubert/nk/api/application/scenario/ScenarioQuerySnapshot","sha256":"11b7346adb9a501dea51e3b051de978998742d6a875dd2c7b4e8cbb837365443"},"dev/codex/schubert/nk/api/maintenance/InboxMaintenanceException":{"module":"api","name":"dev/codex/schubert/nk/api/maintenance/InboxMaintenanceException","sha256":"db4f04b21728a88b23ef1ffe8ca1e1792b12ca113f26dede9f486979e0abe861"},"dev/codex/schubert/nk/api/logging/LogProjectionDatabaseException":{"module":"api","name":"dev/codex/schubert/nk/api/logging/LogProjectionDatabaseException","sha256":"dcd291953325f6023c13cc65a096031c910891267080ebe47a1f7d035e85865b"},"dev/codex/schubert/nk/web/config/ScenarioLogMvcConfiguration":{"module":"web","name":"dev/codex/schubert/nk/web/config/ScenarioLogMvcConfiguration","sha256":"65811bdf21928fec013a473ea67a7df07752e2531587e847b821f21c888b66ba"}}
CLOSURES={"dev/codex/schubert/nk/api/application/scenario/ScenarioQuerySnapshot":["dev/codex/schubert/nk/api/application/scenario/ScenarioQuerySnapshot","dev/codex/schubert/nk/api/application/scenario/ScenarioQuerySnapshot$Detail","dev/codex/schubert/nk/api/application/scenario/ScenarioQuerySnapshot$Inline"],"dev/codex/schubert/nk/api/maintenance/InboxMaintenanceException":["dev/codex/schubert/nk/api/maintenance/InboxMaintenanceException"],"dev/codex/schubert/nk/api/logging/LogProjectionDatabaseException":["dev/codex/schubert/nk/api/logging/LogProjectionDatabaseException"],"dev/codex/schubert/nk/web/config/ScenarioLogMvcConfiguration":["dev/codex/schubert/nk/web/config/ScenarioLogMvcConfiguration"]}
METADATA={"dev/codex/schubert/nk/api/application/scenario/ScenarioQuerySnapshot"}
METADATA_FLAGS={"dev/codex/schubert/nk/api/application/scenario/ScenarioQuerySnapshot":1537}
GENERATED_METADATA=set()
COUNTS={"ScenarioCarrierSuccessContractTest":2,"ProjectionFailureValueContractTest":1,"InboxFailureValueContractTest":1,"CompositeMvcDeclarationContractTest":1}
PINS={"ScenarioCarrierSuccessContractTest":"5d3844a638c04c143a729b8e49450dc34db6697778ba7ed4b025a30f716ae28f","ProjectionFailureValueContractTest":"fdccaa0130f6740a1476002fc690f48c1560422b2b956bb4066e950d2999accf","InboxFailureValueContractTest":"72f318b93ec84fc8efdb368fb68d8e54636108ca3b6b64d2a08dd70710bdc52c","CompositeMvcDeclarationContractTest":"cd5950adcbe73f542da9e227e59d3b0955ba0c81687e17ed17712e142be21396"}
TESTS={n:ROOT/('tools/quality/architecture/'+n+'.java') for n in COUNTS}
PUBLIC_READS={"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/persistence/ScenarioDetailSnapshot.java":"a9adb21b9bddf514ad3b44218465762c767d8f4f8ba34d38c4526df74eb0dcc6","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/TypedPayloadValues.java":"5db4c6b32786b0803334a4c8f7949bf4be0b6936a71c94658f6cef78e970286b","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/LayoutId.java":"87c8f01b5f84f211a8902d323eba221d11dc6b6add1cfe2a514fdbb68e82bc24","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/scenario/GameListResponseData.java":"155ecfd10ec246a8beed2bbcf6799cb70fbd180f6fad5ec23cef3168258939ab","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/scenario/ScenarioDetailResponseData.java":"10e780b70f67c15c27e9f306b98ea2482927bbec124cb3de66239953ff5c994a","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/ScriptFileId.java":"c4e173ae47563d5220fac49b5664d2d7493f5e273eefaabca97899f3e93ccae7","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/DisplayPath.java":"2718fe6494806fc87dc3d081f82ed220616a07d53bf6eb39a23de579b3c6e7e3","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/GameCode.java":"fd1c8af391cdd029dca64986c4bf8e7660ef06382c2ac6ce199c0e22bca40b92","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/DeliveryMode.java":"5b4b7af1fc8cd8d9049ac0da29be74c82e61d1b68653eb3767690962778955a9","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/config/ScenarioMvcConfiguration.java":"747df2fc1f4e02239af03a172f99c8731634d59dac907d0235371f1b48b5a933","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/config/LogMvcConfiguration.java":"2bd503e7b08e3b6cb85f7bf14f8677c50a98c086509d8dfebc66049615e29958"}
EXTRAS={}
FIXTURES={}
SESSION='PG18320-CARRIER-CATALOG5'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG18319-carrier-catalog-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG18308-current2959-web-terminal-flag-registry-v1/manifest.json','a463cf67fb028fe17452fec23ee2ddbd8cb8a458c6533fa70bae7b0592dc4933')
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
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,independentNewQualityTests=5,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=0,pureSuccessCarrierAndFixedCatalogOnly=True,queryNullCasesDynamicallyVerified=False,wholeQueryProgramAccepted=False,publicClassAnnotationMetadataOnly=True,privateReflectiveAccessUsed=False,applicationContextOrControllerInvoked=False,normalProtocolCodecFixtureConstructionInvoked=True,nfcAndUtf8ValidationInvoked=True,jdkNamedTimeZoneInitializationInvoked=False,businessDateConversionInvoked=False,jdkTimezoneProviderCallsAndResourceReads=None,actualAdminMutationOrAuthorization=False,actualBusinessProviderInvoked=False,actualThrowableGraphTraversal=False,publicFixedUuidFixtureOnly=False,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg18320-carrier-catalog-five-pt-v1';run.OUT=data.BASE/'PG18320-carrier-catalog-five-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/CarrierCatalogFiveCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['ScenarioCarrierSuccessContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,)+tuple(p for p in TESTS.values() if p!=run.NEW_TEST);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
