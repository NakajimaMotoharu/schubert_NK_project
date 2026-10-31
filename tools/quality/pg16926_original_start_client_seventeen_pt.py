"""Original start-client seventeen: memory business ports plus one owned unprivileged true child, not a Unit start."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/batch/platform/'
NAME=PREFIX+'BackupUnitStartClient'
MAIN_UNITS={PREFIX+n:dict(module='batch',name=PREFIX+n,sha256=h) for n,h in [('BackupUnitStartClient','505591e7159e2e8d8cb86ffab1e7395ca9d7cdd9e4c796f14d66064a54cd600c'),('RootStartupContext','8281f715abd82572704c868764f642e10b19e10b4475fd0983735e0fbe340fa8'),('MaintenanceUnitStopClient','ae53eb1a23d05cadb270554222d74c84d64a29adedab5666f15b2e20135470c2')]}
CLOSURES={NAME:[NAME+s for s in ['','$1','$2','$Attempt','$Context','$Intent','$MarkerLease','$Policy','$RetirementGate','$Start','$Status','$Target']],PREFIX+'RootStartupContext':[PREFIX+'RootStartupContext'+s for s in ['','$Io','$NativeIo','$NativeIo$LinkRead','$NativeIo$UnitQuery','$Service','$Snapshot','$Verification']],PREFIX+'MaintenanceUnitStopClient':[PREFIX+'MaintenanceUnitStopClient'+s for s in ['','$Attempt','$Context','$NativeStart','$Policy','$Start','$Status']]}
METADATA={NAME+s for s in ['$Context','$Intent','$Policy','$RetirementGate','$Start']}|{PREFIX+'RootStartupContext'+s for s in ['$NativeIo$LinkRead','$NativeIo$UnitQuery','$Verification']}|{PREFIX+'MaintenanceUnitStopClient'+s for s in ['$Context','$Policy','$Start']}
METADATA_FLAGS={n:1537 if n.endswith('$RetirementGate') else 1536 for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'BackupUnitStartClientTest':17}
PINS={'BackupUnitStartClientTest':'f46a3c8a5e05ed6f8ab14bf7bb5baf4cfe0ae2fd80863d6a2db046fbdf556b53'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-batch/src/test/java/'+PREFIX+n+'.java') for n in COUNTS}
EXTRAS={'src/schubert-nk-batch/src/test/java/'+PREFIX+n+'.java':h for n,h in [('InspectorUnitProbeFixture','75b62aea8f3e4fbc558ec24698c7ff7d1faf4f477f34addb17e5e58f1283da2b'),('InspectorUnitSnapshotTest','edf0ce67d649d340e2e61907cc8228cd9c44fe08a21a9f011d81cdcbef4d1a63'),('RootStartupContextTest','f3de04b3c6043aed5e6871bc1de15b8108da8cf7adacad206d0a8a0b88a71811')]}
EXTRAS['src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/CallerMonitorProbe.java']='e502853332c70415707eb38f8aa52e0096f54c4a106c21a51d23cb47cbbda9fd'
BENIGN_CHILD=ROOT.__class__('/usr/bin/true')
BENIGN_CHILD_SHA='913a39cd38f353497086bcf317b12f91f93c23b51869cea763b8340b4f84cfd3'
FIXTURES={}
SESSION='PG16926-ORIGINAL-START-CLIENT-SEVENTEEN-OWNED-TRUE-CHILD'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG16924-original-start-client-fresh-review-binding-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG16914-current2476-memory-live-intent-fence-registry-v1/manifest.json','881b7f3d10d92ad54bfa23f3f407f4038edb3cbfd1eb85c43c07cb90337b9000')
    assert old['source']==SOURCE and set(MAIN_UNITS)-old['fullSourceUnits'].keys()=={PREFIX+'MaintenanceUnitStopClient'}
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.platform.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','java.nio.file.','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','Class.forName','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','.holdUnknownInterval(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook'])
        assert text.count('new MaintenanceUnitStopClient.NativeStart().execute(List.of("/usr/bin/true"))')==1
        assert 'assertTrue(harmless.waitFor(5, TimeUnit.SECONDS))' in text and 'assertEquals(0, harmless.exitValue())' in text
        assert 'assertNotNull(BackupUnitStartClient.create(context, expected));' in text and 'new RootStartupContextTest.Fixture()' in text
        assert not any(t in text for t in ['.createService(','.createCaddy(','beginNative(','.NativeIo(','RootStartupContext.create('])
    import stat
    binary=BENIGN_CHILD.stat();assert binary.st_uid==0 and stat.S_ISREG(binary.st_mode) and stat.S_IMODE(binary.st_mode)==0o755 and data.sha(BENIGN_CHILD.read_bytes())==BENIGN_CHILD_SHA
    for path,pin in EXTRAS.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,memoryBusinessPortsAndOneOwnedBenignChild=True,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=True,declaredOwnedBenignChildCount=1,ownedBenignChildPath=str(BENIGN_CHILD),ownedBenignChildSha256=BENIGN_CHILD_SHA,declaredOwnedMonitorWorkerCount=1,actualRootMemoryFixtureOnly=True,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,actualHookRegistrationOrRemovalInvoked=False,actualNativeHookOrProviderOperation=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16926-original-start-client-seventeen-pt-v1';run.OUT=data.BASE/'PG16926-original-start-client-seventeen-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/OriginalStartClientSeventeenCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['BackupUnitStartClientTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
