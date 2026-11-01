"""Five independent fixed query exception catalogs; no query, database or graph calls."""
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
PREFIX='dev/codex/schubert/nk/api/persistence/'
MAIN_UNITS={"dev/codex/schubert/nk/api/persistence/LogQueryException":{"module":"api","name":"dev/codex/schubert/nk/api/persistence/LogQueryException","sha256":"f515674300bc1dcf0fa23632cf608ad33021ef68f806d63664f0b94bce15a2de"},"dev/codex/schubert/nk/api/persistence/MediaQueryException":{"module":"api","name":"dev/codex/schubert/nk/api/persistence/MediaQueryException","sha256":"77c96848ca417d87938143b140df4ea8d430d45b1708c6dbde2079d733817e0c"},"dev/codex/schubert/nk/api/persistence/ScenarioQueryException":{"module":"api","name":"dev/codex/schubert/nk/api/persistence/ScenarioQueryException","sha256":"46cad487144bfa56615badc60b78136b54512edec3f5473ea905d627f182e59b"},"dev/codex/schubert/nk/api/persistence/UserQueryException":{"module":"api","name":"dev/codex/schubert/nk/api/persistence/UserQueryException","sha256":"43b3e1294cec96541b0899dbf6bff8478689fee51d92b4ea2494465f59593082"},"dev/codex/schubert/nk/api/persistence/QuestionQueryException":{"module":"api","name":"dev/codex/schubert/nk/api/persistence/QuestionQueryException","sha256":"c9c44b231ab9e0ac1fb7b43f2af2b73d076a6c46edb1513c96e56a8c74b5ce90"}}
CLOSURES={n:[n] for n in MAIN_UNITS}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'QueryCatalogContractTest':6}
PINS={'QueryCatalogContractTest':'decb0ad056970093f68efdb89b1ef2338e3fa2245fff166655a78ad427b4f875'}
TESTS={'QueryCatalogContractTest':ROOT/'tools/quality/architecture/QueryCatalogContractTest.java'}
PUBLIC_READS={'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/header/ResultCode.java':'ade5ac5514ed62f2be57419eeab2d3a5e27da98a1c6607621be60e3a11c162f4'}
EXTRAS={}
FIXTURES={}
SESSION='PG18030-QUERY-CATALOG5'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG18029-query-catalogs-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG18018-current2858-admin-values-registry-v1/manifest.json','401f67ec8f09c5604dd7341d042668bed9aa6efffff1419457e35cdf736a18c2')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&set(old['fullSourceUnits'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative=='tools/quality/architecture/QueryCatalogContractTest.java'
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
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,independentNewQualityTests=5,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=0,pureQueryFixedExceptionCatalogOnly=True,actualAdminMutationOrAuthorization=False,actualProviderInvoked=False,actualThrowableGraphTraversal=False,publicFixedUuidFixtureOnly=False,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg18030-query-catalogs-five-pt-v1';run.OUT=data.BASE/'PG18030-query-catalogs-five-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/QueryCatalogFiveCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['QueryCatalogContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
