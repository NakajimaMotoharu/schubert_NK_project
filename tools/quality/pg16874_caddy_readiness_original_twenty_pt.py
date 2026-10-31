"""Original Caddy readiness twenty with fixed observations and owned memory streams, no daemon/TLS connection."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME='dev/codex/schubert/nk/batch/platform/MorningCaddyReadiness'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='e5e4b289865f86279ec541a13753fa4cc44f8f8ccacbf9d28a9f8d92735ccb9d')}
CLOSURES={NAME:[NAME+s for s in ['','$Guard','$Io','$NativeIo']]}
METADATA={NAME+'$Guard',NAME+'$Io'}
GENERATED_METADATA=set()
COUNTS={'MorningCaddyReadinessTest':20}
PINS={'MorningCaddyReadinessTest':'fe14df69a1b4e7deb21b0afe03825fbf1fb02b30055b42c73f8ab29f3ce7a359'}
ROOT=data.ROOT
TESTS={'MorningCaddyReadinessTest':ROOT/('src/schubert-nk-batch/src/test/java/'+NAME+'Test.java')}
EXTRAS={}
FIXTURES={}
SESSION='PG16874-CADDY-READINESS-ORIGINAL-TWENTY'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG16873-caddy-readiness-fresh-review-binding-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG16864-current2434-child-parent-inspector-caddy-registry-v1/manifest.json','a93769619fd0f679ed33269e174934ddbedadd97d72dc1b8ecf3c738bf9d7cc1')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.platform.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','java.nio.file.','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','Class.forName','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','.holdUnknownInterval(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook'])
        assert text.count('Executors.newFixedThreadPool(2)')==1 and text.count('executor.submit(')==2
        assert 'MorningCaddyReadiness.create(null, null, null)' in text and 'assertTrue(ready.await(10, TimeUnit.SECONDS))' in text
        assert 'new NativeIo' not in text and 'coldInvocation(' not in text and 'CaddyPublicConfiguration.' not in text
        assert 'new MorningCaddyReadiness(this::guard, this)' in text
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,injectedCaddyReadinessOnly=True,publicFactoryNullRejectionOnly=True,declaredOwnExecutorInstances=1,declaredOwnTaskCount=2,actualHttpConnectionOpened=False,actualGetentOrSystemctlInvoked=False,actualProcRead=False,actualHookRegistrationOrRemovalInvoked=False,actualNativeHookOrProviderOperation=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16874-caddy-readiness-original-twenty-pt-v1';run.OUT=data.BASE/'PG16874-caddy-readiness-original-twenty-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/CaddyReadinessTwentyCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MorningCaddyReadinessTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
