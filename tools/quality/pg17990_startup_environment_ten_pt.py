"""Fixed injected environment guards and necessary API/Web input eight; nonsecret SHA256 only."""
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
A='dev/codex/schubert/nk/api/bootstrap/ApiStartupInputs'
W='dev/codex/schubert/nk/web/bootstrap/WebStartupInputs'
MAIN_UNITS={A:dict(module='api',name=A,sha256='e6d69bfa6580bba22f2558c37d0ab43799ee5cc515e00a8d64370168333648e6'),W:dict(module='web',name=W,sha256='aacdcad0881ad85dee12ca67a92396bcfa4f0aefd91e24c033d7e46d1f840042')}
CLOSURES={n:[n,n+'$Values'] for n in MAIN_UNITS}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'ApiStartupInputsTest':4,'WebStartupInputsTest':4,'ApiEnvironmentGateContractTest':1,'WebEnvironmentGateContractTest':1}
PINS={'ApiStartupInputsTest':'3cecaf9d04173e9b973683a95f94a566ac47506654cad33170134814a54be3d5','WebStartupInputsTest':'4994569f2e6c1dd29ceff084562a25818294e11be3c41bec23cb938422d84d18','ApiEnvironmentGateContractTest':'0f6d43bd4e7b96046cd4acae44f9cbcdb58f97c76befcee3701afcb0d0ed40a2','WebEnvironmentGateContractTest':'f62b8d2f648950b7e76edced38b81e17f03bfe1bccf941ce696937c742d656d7'}
TESTS={'ApiStartupInputsTest':ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiStartupInputsTest.java','WebStartupInputsTest':ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebStartupInputsTest.java','ApiEnvironmentGateContractTest':ROOT/'tools/quality/architecture/ApiEnvironmentGateContractTest.java','WebEnvironmentGateContractTest':ROOT/'tools/quality/architecture/WebEnvironmentGateContractTest.java'}
PUBLIC_READS={'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiConfigurationLoader.java':'b83a846f6559b6ce4f89af5cbcb5f6cdee602ab0c8f9a7afe85fa1b26e25b569','src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebConfigurationLoader.java':'61b84b53aabf00554608ffcaaad8445a08f9fb2cb3db8bb07501dc24d2dd7685','src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiNonSecretConfig.java':'44f593abd6204f9dbc9ebf672405e4adac7ff793f16c91c71f411d21d3b8ac45','src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebNonSecretConfig.java':'a0254c980bdbead9800395cc2ea98704708cda4d7d81763fcd4d67b64f1c7620','src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/ChildStartupContext.java':'1064a82f50f9614a5469277543e584d687408e8d2bc07d9dc97558e07563d0fb','src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ServiceCredentialLocation.java':'5764718de5644b4e008e5407748b277cdd1e87abf001889a555a2e802c58b99a','src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/NonSecretConfigSource.java':'319e6cc5885f7aded8b475e874265261480b0fafb966ea62bb5290f02282345b'}
EXTRAS={}
FIXTURES={}
SESSION='PG17990-STARTUP-ENVIRONMENT-JOINT10'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17989-startup-environment-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17978-current2850-pure-retirement-joint-registry-v1/manifest.json','a26ab8e71f29f594a80d960d6ad4ce72e5362ef798ee6526aed3fe78e6dbd7a2')
    assert old['source']==SOURCE and all(old['fullSourceUnits'][n]['four100'] is False and n not in old['jointQualificationReplacedUnitHistory'] for n in MAIN_UNITS)
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT));original=name in ['ApiStartupInputsTest','WebStartupInputsTest']
        assert data.sha(path.read_bytes())==PINS[name]
        if original:assert current[relative]==PINS[name]
        else:assert relative=='tools/quality/architecture/'+name+'.java' and 'assertEquals(0, reads.get())' in text
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        suite=next(v.removeprefix('package ').removesuffix(';') for v in text.splitlines() if v.startswith('package '))+'.'+name
        assert (suite in old['suiteNames'])==original
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','getConnection(','System.getenv(','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo','.production('])
    for path,pin in PUBLIC_READS.items():assert data.sha((ROOT/path).read_bytes())==data.sha((COMPILE/'snapshot'/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites={'ApiStartupInputsTest':4,'WebStartupInputsTest':4},independentNewQualityTests=2,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=8,suppliedNonsecretEnvironmentGuardOnly=True,childDescriptorNameRecognitionOnly=True,actualDescriptorAdoptionOrNativeIo=False,cryptoOrKeyOperationsInvoked=True,publicDigestOnly=True,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17990-startup-environment-ten-pt-v1';run.OUT=data.BASE/'PG17990-startup-environment-ten-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/StartupEnvironmentTenCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['ApiEnvironmentGateContractTest'];run.TEST_ROOT=run.NEW_TEST.parent
    run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='ApiEnvironmentGateContractTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
