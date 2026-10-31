"""Current-source whole8; reuse unchanged static review only, never old Product results."""
import json
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
MAIN_UNITS=json.loads("{\"dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame\":{\"module\":\"bootstrap\",\"name\":\"dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame\",\"sha256\":\"48645538321f59775ceca14b6c4ee201db6cbad142e7ca7551e35145f886f4e7\"}}")
CLOSURES=json.loads("{\"dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame\":[\"dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame\",\"dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame$Clock\",\"dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame$Guard\",\"dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame$Parent\",\"dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame$ParentProbe\"]}")
METADATA=set(json.loads("[\"dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame$Clock\",\"dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame$ParentProbe\"]"))
COUNTS=json.loads("{\"MaintenanceParentGuardTest\":6}")
PINS=json.loads("{\"MaintenanceParentGuardTest\":\"221f3b79003cf5c2a3e6c51386d5f3099948041d68d2bb94cefbba58334fd03a\"}")
EXTRAS=json.loads("{}")
FIXTURES=json.loads("{}")
SESSION='PG16696-MAINTENANCE-PARENT-GUARD-ORIGINAL-SIX'
ROOT=data.ROOT
TESTS={name:data.ROOT/path for name,path in json.loads("{\"MaintenanceParentGuardTest\":\"src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/MaintenanceParentGuardTest.java\"}").items()}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG16695-parent-guard-static-review-equivalence-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    old=data.read_checked(data.BASE/'PG14012-maintenance-parent-guard-whole-six-pt-v1/manifest.json','044da488f5421a50834320c1b708a5ecc8ddc2e071030ee0ea61cc9fc6777f98')
    before=old['begin']['sourceHashes'];current=normal['begin']['inputHashes']
    changed=sorted(p for p in before.keys()|current.keys() if before.get(p)!=current.get(p))
    prefix='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/'
    assert changed==sorted(prefix+p for p in ['question/QuestionQueryApplicationService.java','admin/UserQueryApplicationService.java','log/LogQueryApplicationService.java'])
    assert normal['source']==SOURCE and old['source']=='0061d178cda80c2ce3926290619c64db125dbcfc'
    previous=data.read_checked(data.BASE/'PG16686-current2350-terminal-stop-registry-v1/manifest.json','15e805c911a7c73dae491adb1c8f00cae23c9de3985dcc541db75e87471026c3')
    assert previous['source']==SOURCE and not set(MAIN_UNITS)&previous['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));text=path.read_text()
        assert run.host.sha(path)==PINS[name]==current[relative]==before[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert ('.'.join(path.relative_to(data.ROOT).as_posix().split('/src/test/java/',1)[1][:-5].split('/'))) not in previous['suiteNames']
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningParentBudget.create','MorningProcessMain.runCompleted(','MorningProcessMain.main(','RootFailedStartRecovery','LinuxMonotonicClock.create(','.parentsGuard()','new ChildStartupContext('])
    for path,pin in EXTRAS.items():assert run.host.sha(ROOT/path)==pin==current[str((ROOT/path).relative_to(data.ROOT))]==before[str((ROOT/path).relative_to(data.ROOT))]
    for path,pin in FIXTURES.items():assert run.host.sha(data.ROOT/path)==pin==current[path]==before[path]
    for name,row in MAIN_UNITS.items():
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:
            path=source_path(row);assert row['sha256']==current[path]==before[path]==run.host.sha(data.ROOT/path)
            assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    reviews=['evidence/01_PT/018_NK-OPS-001/2555_MaintenanceParentGuard元whole六_単体テスト仕様書.md']
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reuseKind='UNCHANGED_STATIC_REVIEW_INPUTS_NOT_RUNTIME_RESULTS',priorSource=old['source'],priorPublicInputManifestSha256='044da488f5421a50834320c1b708a5ecc8ddc2e071030ee0ea61cc9fc6777f98',currentNormalManifestSha256=COMPILE_SHA,changedPathsOutsideReviewedBatchCallTree=changed,reviewDocuments={p:run.host.sha(data.ROOT/p) for p in reviews},originalWholeSuites=COUNTS,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16696-maintenance-parent-guard-original-six-pt-v1';run.OUT=data.BASE/'PG16696-maintenance-parent-guard-original-six-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/MaintenanceParentGuardCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MaintenanceParentGuardTest'];run.TEST_ROOT=TESTS['MaintenanceParentGuardTest'].parent
    run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
