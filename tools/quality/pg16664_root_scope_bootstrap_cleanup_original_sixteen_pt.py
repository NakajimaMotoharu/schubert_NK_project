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
MAIN_UNITS=json.loads("{\"dev/codex/schubert/nk/batch/file/RootServiceAdmissionScope\":{\"module\":\"batch\",\"name\":\"dev/codex/schubert/nk/batch/file/RootServiceAdmissionScope\",\"sha256\":\"4575d2e8e24004b2b16224a52275f407d0cd95c9492a4133b958c1786f74adf0\"},\"dev/codex/schubert/nk/batch/file/CleanupPreflight\":{\"module\":\"batch\",\"name\":\"dev/codex/schubert/nk/batch/file/CleanupPreflight\",\"sha256\":\"1f182646860d9e15bdc8c539d41698583d3026db01edcc2950f498a66223a8ac\"},\"dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain\":{\"module\":\"api\",\"name\":\"dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain\",\"sha256\":\"d6d87b4250ff3cf604308c3373d052a46283130a556c37c25c4e858ef1991f61\"}}")
CLOSURES=json.loads("{\"dev/codex/schubert/nk/batch/file/RootServiceAdmissionScope\":[\"dev/codex/schubert/nk/batch/file/RootServiceAdmissionScope\",\"dev/codex/schubert/nk/batch/file/RootServiceAdmissionScope$Exclusive\",\"dev/codex/schubert/nk/batch/file/RootServiceAdmissionScope$Gate\",\"dev/codex/schubert/nk/batch/file/RootServiceAdmissionScope$Work\"],\"dev/codex/schubert/nk/batch/file/CleanupPreflight\":[\"dev/codex/schubert/nk/batch/file/CleanupPreflight\",\"dev/codex/schubert/nk/batch/file/CleanupPreflight$Database\",\"dev/codex/schubert/nk/batch/file/CleanupPreflight$Gate\",\"dev/codex/schubert/nk/batch/file/CleanupPreflight$Original\",\"dev/codex/schubert/nk/batch/file/CleanupPreflight$Request\"],\"dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain\":[\"dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain\",\"dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain$Capture\",\"dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain$Operation\"]}")
METADATA=set(json.loads("[\"dev/codex/schubert/nk/batch/file/RootServiceAdmissionScope$Exclusive\",\"dev/codex/schubert/nk/batch/file/RootServiceAdmissionScope$Gate\",\"dev/codex/schubert/nk/batch/file/RootServiceAdmissionScope$Work\",\"dev/codex/schubert/nk/batch/file/CleanupPreflight$Database\",\"dev/codex/schubert/nk/batch/file/CleanupPreflight$Gate\",\"dev/codex/schubert/nk/batch/file/CleanupPreflight$Original\",\"dev/codex/schubert/nk/batch/file/CleanupPreflight$Request\",\"dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain$Capture\",\"dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain$Operation\"]"))
COUNTS=json.loads("{\"RootServiceAdmissionScopeTest\":6,\"BootstrapEntryBoundaryTest\":5,\"CleanupPreflightTest\":5}")
PINS=json.loads("{\"RootServiceAdmissionScopeTest\":\"71560f91ff65ee491900b4ef86083f429afee1524d4f5f05ff8cba6df9a8bd71\",\"BootstrapEntryBoundaryTest\":\"0f56a6cce8881002a8210daf81a6c19328badd632fa3b63d597d683ec5de3fc8\",\"CleanupPreflightTest\":\"b5577eb35b6a8db2b53b5b2faf03b80dd4b63feaa542cee3d147837d13fde12a\"}")
EXTRAS=json.loads("{\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/BackupArtifactFixture.java\":\"62a55866ed181dd886a8b5988fa5922675259b261ad31133a601c7b8361dcbf4\",\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/backup/BackupManifestFixture.java\":\"dc52d8ad7f4cc73b2947257e458bb8e36f10221789218812c44010c72951e976\"}")
FIXTURES=json.loads("{}")
SESSION='PG16664-ROOTSCOPE-BOOTSTRAP-CLEANUP-ORIGINAL-SIXTEEN'
ROOT=data.ROOT
TESTS={name:data.ROOT/path for name,path in json.loads("{\"RootServiceAdmissionScopeTest\":\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootServiceAdmissionScopeTest.java\",\"BootstrapEntryBoundaryTest\":\"src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/BootstrapEntryBoundaryTest.java\",\"CleanupPreflightTest\":\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/CleanupPreflightTest.java\"}").items()}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG16663-root-scope-static-review-equivalence-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    old=data.read_checked(data.BASE/'PG13928-root-bootstrap-cleanup-whole-sixteen-pt-v1/manifest.json','1d1468e9a07343a3ef1bbcb183fea56af22dca9090721f26afec7f3369b869a9')
    before=old['begin']['sourceHashes'];current=normal['begin']['inputHashes']
    changed=sorted(p for p in before.keys()|current.keys() if before.get(p)!=current.get(p))
    prefix='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/'
    assert changed==sorted(prefix+p for p in ['question/QuestionQueryApplicationService.java','admin/UserQueryApplicationService.java','log/LogQueryApplicationService.java'])
    assert normal['source']==SOURCE and old['source']=='0061d178cda80c2ce3926290619c64db125dbcfc'
    previous=data.read_checked(data.BASE/'PG16654-current2323-morning-handoff-registry-v1/manifest.json','3d9c9848fab1ff1d26d5da039160e9d416a5a7abf7c6e5f8a45c9bb76078293d')
    assert previous['source']==SOURCE and not set(MAIN_UNITS)&previous['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));text=path.read_text()
        assert run.host.sha(path)==PINS[name]==current[relative]==before[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert ('.'.join(path.relative_to(data.ROOT).as_posix().split('/src/test/java/',1)[1][:-5].split('/'))) not in previous['suiteNames']
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningParentBudget.create','MorningProcessMain.runCompleted(','MorningProcessMain.main(','RootFailedStartRecovery'])
    for path,pin in EXTRAS.items():assert run.host.sha(ROOT/path)==pin==current[str((ROOT/path).relative_to(data.ROOT))]==before[str((ROOT/path).relative_to(data.ROOT))]
    for path,pin in FIXTURES.items():assert run.host.sha(data.ROOT/path)==pin==current[path]==before[path]
    for name,row in MAIN_UNITS.items():
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:
            path=source_path(row);assert row['sha256']==current[path]==before[path]==run.host.sha(data.ROOT/path)
            assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    reviews=['evidence/01_PT/018_NK-OPS-001/2540_RootBootstrapCleanup_memory全16_通常PT仕様.md']
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reuseKind='UNCHANGED_STATIC_REVIEW_INPUTS_NOT_RUNTIME_RESULTS',priorSource=old['source'],priorPublicInputManifestSha256='1d1468e9a07343a3ef1bbcb183fea56af22dca9090721f26afec7f3369b869a9',currentNormalManifestSha256=COMPILE_SHA,changedPathsOutsideReviewedBatchCallTree=changed,reviewDocuments={p:run.host.sha(data.ROOT/p) for p in reviews},originalWholeSuites=COUNTS,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16664-root-scope-bootstrap-cleanup-original-sixteen-pt-v1';run.OUT=data.BASE/'PG16664-root-scope-bootstrap-cleanup-original-sixteen-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/RootBootstrapCleanupMemoryJunitLauncher.java'
    run.NEW_TEST=TESTS['RootServiceAdmissionScopeTest'];run.TEST_ROOT=TESTS['RootServiceAdmissionScopeTest'].parent
    run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
