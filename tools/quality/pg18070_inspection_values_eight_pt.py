"""Independent immutable inspection values; no executor, SQL or process gate."""
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
MAIN_UNITS={"dev/codex/schubert/nk/api/maintenance/InspectionRun":{"module":"api","name":"dev/codex/schubert/nk/api/maintenance/InspectionRun","sha256":"7db64d61edb32a3df73d75d163c098eda5954afef235e1428d28b8d1e3ab8575"},"dev/codex/schubert/nk/api/maintenance/InspectionStep":{"module":"api","name":"dev/codex/schubert/nk/api/maintenance/InspectionStep","sha256":"a1f815151a650c7fd50422585f5cf08d187c1ce7f6c114324e023d0a70155abb"},"dev/codex/schubert/nk/api/maintenance/InspectionProgress":{"module":"api","name":"dev/codex/schubert/nk/api/maintenance/InspectionProgress","sha256":"fe4338f4db6a24eb7c33ffe8da1b208d677caa90c29cd064b3a094dca15a58f3"},"dev/codex/schubert/nk/api/maintenance/InspectionExecution":{"module":"api","name":"dev/codex/schubert/nk/api/maintenance/InspectionExecution","sha256":"39f9e544873527dae906ac30f48bee559bae330382a6ce3080c37f0b68cbdb4a"}}
CLOSURES={"dev/codex/schubert/nk/api/maintenance/InspectionRun":["dev/codex/schubert/nk/api/maintenance/InspectionRun"],"dev/codex/schubert/nk/api/maintenance/InspectionStep":["dev/codex/schubert/nk/api/maintenance/InspectionStep","dev/codex/schubert/nk/api/maintenance/InspectionStep$Outcome"],"dev/codex/schubert/nk/api/maintenance/InspectionProgress":["dev/codex/schubert/nk/api/maintenance/InspectionProgress"],"dev/codex/schubert/nk/api/maintenance/InspectionExecution":["dev/codex/schubert/nk/api/maintenance/InspectionExecution","dev/codex/schubert/nk/api/maintenance/InspectionExecution$Status"]}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'InspectionValueContractTest':8}
PINS={'InspectionValueContractTest':'1acc091326f45f9b2c66871b3cccb229fbdbb11d3945992106155d5d24ee0c70'}
TESTS={'InspectionValueContractTest':ROOT/'tools/quality/architecture/InspectionValueContractTest.java'}
PUBLIC_READS={}
EXTRAS={}
FIXTURES={}
SESSION='PG18070-INSPECTION-VALUES8'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG18069-inspection-values-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG18059-current2863-caddy-passive-registry-v2/manifest.json','e3d39ba1ef37df634338d1be0bc6cb02f0104c16c3c6c634071d772288f78bba')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&set(old['fullSourceUnits'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative=='tools/quality/architecture/InspectionValueContractTest.java'
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
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,independentNewQualityTests=8,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=0,pureInspectionImmutableValuesOnly=True,actualAdminMutationOrAuthorization=False,actualProviderInvoked=False,actualThrowableGraphTraversal=False,publicFixedUuidFixtureOnly=True,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg18070-inspection-values-eight-pt-v1';run.OUT=data.BASE/'PG18070-inspection-values-eight-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/InspectionValuesEightCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['InspectionValueContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
