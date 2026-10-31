"""Original Broker/Caddy seven: injected literal IO and original in-memory NSS helper, no daemon access."""
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
MAIN_UNITS={PREFIX+n:dict(module='bootstrap',name=PREFIX+n,sha256=h) for n,h in [('ChildStartupContext','1064a82f50f9614a5469277543e584d687408e8d2bc07d9dc97558e07563d0fb'),('FixedServiceIdentity','2c09eebf305c537bf18c00ae38774ada72269b94529c2c6f749e55cc953cfaab')]}
CLOSURES={PREFIX+'ChildStartupContext':[PREFIX+'ChildStartupContext'+s for s in ['','$Inputs','$InspectorIdentity','$Io','$MaintenanceParent','$NativeIo','$Observed']],PREFIX+'FixedServiceIdentity':[PREFIX+'FixedServiceIdentity'+s for s in ['','$NativeQuery','$Query','$Start','$Value']]}
METADATA={PREFIX+'FixedServiceIdentity$Query',PREFIX+'FixedServiceIdentity$Start'}
GENERATED_METADATA=set()
COUNTS={'ChildBrokerTest':5,'ChildCaddyTest':2}
PINS={'ChildBrokerTest':'01de344d9a2ca038509fddf76ad26d9dfe349e132bf7360871f34a17f7aa4f7c','ChildCaddyTest':'7305593a16f3fdb2220f2c9baee829e9bd0feea58d68d3f4e14de590da23c4bb'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-bootstrap/src/test/java/'+PREFIX+n+'.java') for n in COUNTS}
EXTRAS={'src/schubert-nk-bootstrap/src/test/java/'+PREFIX+'FixedServiceIdentityTest.java':'36db394994872a0265083932a89d19b98120abc3e8e27841e4d1acacb89b6392'}
FIXTURES={}
SESSION='PG16840-CHILD-BROKER-CADDY-ORIGINAL-SEVEN'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG16839-child-broker-caddy-fresh-review-binding-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG16830-current2415-web-uninstalled-lifetime-registry-v1/manifest.json','3683ebc7ba48e13e970c847b20f9e240a60de7423a9d85255de58bcf1642d306')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.bootstrap.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','java.nio.file.','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','Class.forName','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','.holdUnknownInterval(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook'])
        assert 'new ChildStartupContext(' in text and 'Thread.sleep' not in text
    for path,pin in EXTRAS.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    helper=(ROOT/next(iter(EXTRAS))).read_text()
    assert 'return new FixedServiceIdentity(this);' in helper and 'final Map<String, String> values = new HashMap<>(GOLDEN);' in helper
    assert 'commands.add(command);' in helper and 'return bytes(values.getOrDefault(command.get(1) + "/" + command.get(2), ""));' in helper
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,injectedDaemonObservationOnly=True,originalNssFixtureOnly=True,reviewedOriginalHelperInputs=EXTRAS,actualGetentOrSystemctlInvoked=False,actualProcRead=False,actualHookRegistrationOrRemovalInvoked=False,actualNativeHookOrProviderOperation=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16840-child-broker-caddy-original-seven-pt-v1';run.OUT=data.BASE/'PG16840-child-broker-caddy-original-seven-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/ChildBrokerCaddySevenCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['ChildBrokerTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()

