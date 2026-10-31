"""Original parent/Inspector/Caddy twelve: literal IO/Query only, no OS observations or native authority."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/bootstrap/'
MAIN_UNITS={PREFIX+n:dict(module='bootstrap',name=PREFIX+n,sha256=h) for n,h in [('ChildStartupContext','1064a82f50f9614a5469277543e584d687408e8d2bc07d9dc97558e07563d0fb'),('FixedServiceIdentity','2c09eebf305c537bf18c00ae38774ada72269b94529c2c6f749e55cc953cfaab'),('MaintenanceOwnerFrame','48645538321f59775ceca14b6c4ee201db6cbad142e7ca7551e35145f886f4e7')]}
CLOSURES={PREFIX+'ChildStartupContext':[PREFIX+'ChildStartupContext'+s for s in ['','$Inputs','$InspectorIdentity','$Io','$MaintenanceParent','$NativeIo','$Observed']],PREFIX+'FixedServiceIdentity':[PREFIX+'FixedServiceIdentity'+s for s in ['','$NativeQuery','$Query','$Start','$Value']],PREFIX+'MaintenanceOwnerFrame':[PREFIX+'MaintenanceOwnerFrame'+s for s in ['','$Clock','$Guard','$Parent','$ParentProbe']]}
METADATA={PREFIX+n for n in ['FixedServiceIdentity$Query','FixedServiceIdentity$Start','MaintenanceOwnerFrame$Clock','MaintenanceOwnerFrame$ParentProbe']}
GENERATED_METADATA=set()
COUNTS={'ChildMaintenanceInspectorTest':3,'ChildMaintenanceParentTest':6,'FixedCaddyIdentityTest':3}
PINS={'ChildMaintenanceInspectorTest':'9f644a08d2199fa1b758c07a9f288e3fbe1350df4515ae3eebd3b0e7060ea5ee','ChildMaintenanceParentTest':'628e58ac2145a1358179e0fe5e5c7db57ace3760391c8db1a2845925f0e3df07','FixedCaddyIdentityTest':'d1daa88df313bf24975c57e639067942035deedb75e0e75792e8007921666447'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-bootstrap/src/test/java/'+PREFIX+n+'.java') for n in COUNTS}
EXTRAS={}
FIXTURES={}
SESSION='PG16858-CHILD-PARENT-INSPECTOR-CADDY-ORIGINAL-TWELVE'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG16857-child-parent-inspector-caddy-fresh-review-binding-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG16846-current2422-child-broker-caddy-registry-v1/manifest.json','953d9299af7bb5233dcd1f5b8b83bb7bdc83e4156191144da96777bd330243b3')
    assert old['source']==SOURCE and set(MAIN_UNITS)<=old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.bootstrap.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','java.nio.file.','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','Class.forName','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','.holdUnknownInterval(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook'])
        assert ('new ChildStartupContext(' in text or 'new FixedServiceIdentity(' in text) and 'Thread.sleep' not in text
    for path,pin in EXTRAS.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,injectedDaemonObservationOnly=True,originalNssFixtureOnly=True,reviewedOriginalHelperInputs=EXTRAS,actualGetentOrSystemctlInvoked=False,actualProcRead=False,actualHookRegistrationOrRemovalInvoked=False,actualNativeHookOrProviderOperation=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16858-child-parent-inspector-caddy-original-twelve-pt-v1';run.OUT=data.BASE/'PG16858-child-parent-inspector-caddy-original-twelve-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/ChildParentInspectorCaddyTwelveCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['ChildMaintenanceInspectorTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
