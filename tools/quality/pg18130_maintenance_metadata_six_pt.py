"""Three plain maintenance/storage metadata contracts; no actual file, OS ownership or DB actions."""
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
MAIN_UNITS={"dev/codex/schubert/nk/batch/repository/InspectionSummary":{"module":"batch","name":"dev/codex/schubert/nk/batch/repository/InspectionSummary","sha256":"0af03ae228a8efec00535de709a528dfc9692cb2a51c4c2a4a0e0fb79cde12aa"},"dev/codex/schubert/nk/batch/repository/MaintenanceRunState":{"module":"batch","name":"dev/codex/schubert/nk/batch/repository/MaintenanceRunState","sha256":"d5b3b9e2cd40ba30304a6f69a065c63c2ada73af49781b644e1274f3419c4d24"},"dev/codex/schubert/nk/storage/StorageIdentity":{"module":"storage","name":"dev/codex/schubert/nk/storage/StorageIdentity","sha256":"e19734a40b13885ac0d62b3abb117a788d9a7e0839d002d5f655d162cce3cd74"}}
CLOSURES={n:[n] for n in MAIN_UNITS}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'MaintenanceMetadataContractTest':6}
PINS={'MaintenanceMetadataContractTest':'5934bf93b33093c0f26b346bfc3ca4ef0a6692b91a44186e5655dd6226c1fb0f'}
TESTS={'MaintenanceMetadataContractTest':ROOT/'tools/quality/architecture/MaintenanceMetadataContractTest.java'}
PUBLIC_READS={"src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/BatchRun.java":"c440d3e16da86b7814cf8fbd6247e48c1ab4cd6de2da3a114a38c308ae3c7ce4","src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/CleanupCounts.java":"9a7504e2b266c3de22ce10dfc8b15dadb0ce04f3a5f05bdd86d151c32d341f19","src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/MaintenanceActivation.java":"0467e9722cc3c46e238fcdb9e2d1deffde11b3a498e54e61c0f477d18440889e","src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/MaintenanceCompletion.java":"3713fb2ce03a4ec926c4d193051373348da922c15d5f22e8f43cabd215b36dcd"}
EXTRAS={}
FIXTURES={}
SESSION='PG18130-MAINT-METADATA6'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG18129-maintenance-metadata-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG18118-current2889-menu-projection-registry-v1/manifest.json','3cd4ab994fd60df80022a48d3c6095c36a073ae470d603886a325348aaa0433d')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&set(old['fullSourceUnits'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative=='tools/quality/architecture/MaintenanceMetadataContractTest.java'
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
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,independentNewQualityTests=6,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=0,pureMaintenanceStorageMetadataOnly=True,jdkNamedTimeZoneInitializationInvoked=True,businessDateConversionInvoked=False,jdkTimezoneProviderCallsAndResourceReads=None,actualAdminMutationOrAuthorization=False,actualBusinessProviderInvoked=False,actualThrowableGraphTraversal=False,publicFixedUuidFixtureOnly=True,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg18130-maintenance-metadata-six-pt-v1';run.OUT=data.BASE/'PG18130-maintenance-metadata-six-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/MaintenanceMetadataSixCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MaintenanceMetadataContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
