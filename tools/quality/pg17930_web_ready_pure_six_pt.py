"""Pure management conjunction: original four and independent presence two in one owned JVM."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME='dev/codex/schubert/nk/web/bootstrap/WebRuntimeHealth'
MAIN_UNITS={NAME:dict(module='web',name=NAME,sha256='5afec3b52675a18c3d34b676b0d3313dc42b58e7b7377b0658524530b675f5a9')}
CLOSURES={NAME:[NAME]}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'WebRuntimeHealthTest':4,'WebReadyPresenceContractTest':2}
PINS={'WebRuntimeHealthTest':'385348477db8c3f4a5966f049aee3fba659923b6cf872f4df00d5f52d6c86683','WebReadyPresenceContractTest':'55de5bfdeb285f66adb3f4664b82c39675dd82e36dc44d5e06c474535ec49f18'}
ROOT=data.ROOT
TESTS={'WebRuntimeHealthTest':ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimeHealthTest.java','WebReadyPresenceContractTest':ROOT/'tools/quality/architecture/WebReadyPresenceContractTest.java'}
PUBLIC_READS={}
EXTRAS={}
FIXTURES={}
SESSION='PG17930-WEB-PURE-READY-JOINT6'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17929-web-ready-pure-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17919-current2838-session-principal-registry-v2/manifest.json','ac992c8e92288235c219c8331a7801a36084b8e6387d5949945552515de5ee27')
    assert old['source']==SOURCE and old['fullSourceUnits'][NAME]['four100'] is False
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]
        if name=='WebRuntimeHealthTest':assert current[relative]==PINS[name]
        else:assert relative=='tools/quality/architecture/WebReadyPresenceContractTest.java'
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        suite=next(v.removeprefix('package ').removesuffix(';') for v in text.splitlines() if v.startswith('package '))+'.'+name
        assert (suite in old['suiteNames'])==(name=='WebRuntimeHealthTest')
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    text=(ROOT/source_path(MAIN_UNITS[NAME])).read_text()
    assert 'management != null && probe.test(management)' in text and '&& revokeRunning.test(retry)' in text
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites={'WebRuntimeHealthTest':4},independentNewQualityTests=2,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=4,pureCapturedManagementPredicateOnly=True,actualRootNativeObservations=0,actualNetworkActions=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,realRuntimeCredentialOrKeyLoaded=False,cryptoOrKeyOperationsInvoked=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17930-web-ready-pure-six-pt-v1';run.OUT=data.BASE/'PG17930-web-ready-pure-six-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/WebReadyPureSixCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['WebReadyPresenceContractTest'];run.TEST_ROOT=TESTS['WebRuntimeHealthTest'].parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
