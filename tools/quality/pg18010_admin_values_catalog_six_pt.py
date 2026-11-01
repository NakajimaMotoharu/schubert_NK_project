"""Independent pure admin metadata/outcome and fixed answer exception constructors, no business IO."""
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
MAIN_UNITS={PREFIX+'admin/UserCommandMetadata':dict(module='api',name=PREFIX+'admin/UserCommandMetadata',sha256='2f2eeb0e07a5682a657ea23ca912b036b14b08e3ad5cf30cd0d5582a526e14a0'),PREFIX+'admin/UserMutationResult':dict(module='api',name=PREFIX+'admin/UserMutationResult',sha256='fd070960f128b22813c6e01de6cdd6ddd3f4813291cf47abf435a08d8bd1d146'),PREFIX+'question/AnswerBusinessException':dict(module='api',name=PREFIX+'question/AnswerBusinessException',sha256='d62fea79f8c806dcb68ffa5ac25b68c006b6f778a8f00035201fafee2ddd3212')}
CLOSURES={n:[n] for n in MAIN_UNITS}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'AdminValueCatalogContractTest':6}
PINS={'AdminValueCatalogContractTest':'e2e051d2102aedfffaa76c7458d71cba2bfc5f066505ace7c838948e0d02a3e2'}
TESTS={'AdminValueCatalogContractTest':ROOT/'tools/quality/architecture/AdminValueCatalogContractTest.java'}
PUBLIC_READS={'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/header/ResultCode.java':'ade5ac5514ed62f2be57419eeab2d3a5e27da98a1c6607621be60e3a11c162f4','src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/admin/UserMutationResponseData.java':'5bf98b1c3f7c67fc33e331c122b64672eb216b2398208107ca225131e870629b','src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/UserId.java':'482cd1b41f0f5e2408086ca0ea4e6742a2a1c0c80bc541249261c9c339564383','src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/IdValue.java':'3bf4d89066c5da24649c0f970e5f0655c37d34f0bbd6120539b9a518c4905cd1','src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/TypedFieldValues.java':'1f109d93cb6e8e802ab1a9c0484cfe48689253a34f1322111dfbce58bd0a8cde'}
EXTRAS={}
FIXTURES={}
SESSION='PG18010-ADMIN-VALUE-CATALOG6'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG18009-admin-values-catalog-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17998-current2852-startup-environment-joint-registry-v1/manifest.json','195e4b6338efc446e399c2d782dcf55257da2e378a41bff7d5b29dba66b628a6')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&set(old['fullSourceUnits'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative=='tools/quality/architecture/AdminValueCatalogContractTest.java'
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
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,independentNewQualityTests=6,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=0,pureAdminValuesAndFixedExceptionCatalogOnly=True,actualAdminMutationOrAuthorization=False,actualProviderInvoked=False,actualThrowableGraphTraversal=False,publicFixedUuidFixtureOnly=True,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg18010-admin-values-catalog-six-pt-v1';run.OUT=data.BASE/'PG18010-admin-values-catalog-six-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/AdminValuesSixCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['AdminValueCatalogContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
