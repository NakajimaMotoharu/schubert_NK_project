"""Original whole Bootstrap closing three: injected instance-main, never actual bootstrap admission."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME='dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain'
MAIN_UNITS={NAME:dict(module='api',name=NAME,sha256='d6d87b4250ff3cf604308c3373d052a46283130a556c37c25c4e858ef1991f61')}
CLOSURES={NAME:[NAME,NAME+'$Capture',NAME+'$Operation']}
METADATA={NAME+'$Capture',NAME+'$Operation'}
COUNTS={'BootstrapClosingBoundaryTest':3}
PINS={'BootstrapClosingBoundaryTest':'e184974448903eba7e0d77096752325b1f2efc57e3daf88bd9bcfa1c3156c9a9'}
ROOT=data.ROOT
TESTS={'BootstrapClosingBoundaryTest':ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/BootstrapClosingBoundaryTest.java'}
EXTRAS={}
FIXTURES={}
SESSION='PG16760-BOOTSTRAP-CLOSING-ORIGINAL-THREE'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG16759-bootstrap-closing-fresh-review-binding-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG16750-current2374-broker-xml-registry-v1/manifest.json','afa9060c34781dc13ea5bc9ad56554b00bc0df56f906c6bb877e97b043aa1399')
    assert old['source']==SOURCE and set(MAIN_UNITS)<=old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.api.bootstrap.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','Files.','new BatchDatabaseFixture','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','Class.forName','System.exit','new BootstrapAdminMain()','createAndCommit('])
        assert text.count('new BootstrapAdminMain(')==8 and '.main(new String[0])' in text
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,explicitInjectedInstanceMainOnly=True,actualAdministratorOrProcessTerminationInvoked=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16760-bootstrap-closing-original-three-pt-v1';run.OUT=data.BASE/'PG16760-bootstrap-closing-original-three-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/BootstrapClosingThreeCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['BootstrapClosingBoundaryTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
