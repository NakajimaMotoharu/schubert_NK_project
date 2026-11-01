"""Three pure menu catalog/model Sources, no HTTP or DB; independent Current/UI expectations."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pathlib import Path
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
ROOT=data.ROOT
PREFIX='dev/codex/schubert/nk/api/application/'
MAIN_UNITS={"dev/codex/schubert/nk/web/view/MenuCard":{"module":"web","name":"dev/codex/schubert/nk/web/view/MenuCard","sha256":"7fa6583a49c37dedd196d696a2c0d7c45f2e7b7097044d63aa2aef5ef2915ad3"},"dev/codex/schubert/nk/web/view/MenuViewModel":{"module":"web","name":"dev/codex/schubert/nk/web/view/MenuViewModel","sha256":"892c36828ff005248b7d62b593124f9d853c583caf80a3e3e3bef142841057a3"},"dev/codex/schubert/nk/web/controller/MenuController":{"module":"web","name":"dev/codex/schubert/nk/web/controller/MenuController","sha256":"b8fc0125b76a6f02f9d262e24f2636c61a20605668edcaefad389ad1e8f7a1f0"}}
CLOSURES={n:[n] for n in MAIN_UNITS}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'MenuProjectionContractTest':6}
PINS={'MenuProjectionContractTest':'2db272432000f15b19883bd999415755f5bea57a14e046962c34cbda6e760a78'}
TESTS={'MenuProjectionContractTest':ROOT/'tools/quality/architecture/MenuProjectionContractTest.java'}
PUBLIC_READS={"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/TopBarViewModel.java":"16afe37089d96cb31e7849e5bf5e289196588c6f4b8e1d4732fd402887e24a09","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionPrincipal.java":"29af626632ac4c2727f9d0963c3967cb0be7eda57daf762a482268c467dc9232","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionStoreException.java":"93717ee948f88bd799a14cdad397c0d92e584711c32f571df8592be379033ed1","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/header/AuthenticationContext.java":"aaa18a4c954a425c943e8c30ea1752b665b249e86d8f1767e9e37f4aa61a6b66","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/UserRole.java":"b68402e5705ca2ac5093a1b98a44de5a9f45ed69cb9b231658b4903c51e0bf69"}
EXTRAS={}
FIXTURES={}
SESSION='PG18110-MENU-PROJECTION6'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG18109-menu-projection-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
CURRENT_TEMPLATE=Path('/home/mini/codex/project1/schubert_project/program/app/src/main/resources/templates/menu.html')
CURRENT_TEMPLATE_SHA='9b45b5b83c14e945c6dd446889b020749bfdb87dd1f5f83d093a30d9bb074cd1'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    assert data.sha(CURRENT_TEMPLATE.read_bytes())==CURRENT_TEMPLATE_SHA
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG18098-current2883-auth-values-registry-v1/manifest.json','6435d0129082e022ea83152bcf8cf25ff350290b724ba885ad1df22cf5938a12')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&set(old['fullSourceUnits'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative=='tools/quality/architecture/MenuProjectionContractTest.java'
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
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,independentNewQualityTests=6,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=0,pureMenuCatalogAndModelProjectionOnly=True,actualAdminMutationOrAuthorization=False,actualProviderInvoked=False,actualThrowableGraphTraversal=False,publicFixedUuidFixtureOnly=False,publicSyntheticAuthenticationContextValueOnly=True,syntheticAuthenticationContextValueUsed=True,nfcAndUtf8ValidationInvoked=True,memorySessionPrincipalValueOnly=True,currentIndependentOracleTemplate=dict(path=str(CURRENT_TEMPLATE),sha256=CURRENT_TEMPLATE_SHA,readOnly=True,copiedToGit=False),cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg18110-menu-projection-six-pt-v1';run.OUT=data.BASE/'PG18110-menu-projection-six-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/MenuProjectionSixCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MenuProjectionContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
