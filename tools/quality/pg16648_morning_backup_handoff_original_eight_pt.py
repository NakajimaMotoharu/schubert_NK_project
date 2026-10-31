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
MAIN_UNITS=json.loads("{\"dev/codex/schubert/nk/batch/file/MorningBackupPreparation\":{\"module\":\"batch\",\"name\":\"dev/codex/schubert/nk/batch/file/MorningBackupPreparation\",\"sha256\":\"33375542a65e27b2dc40ab5ed20950a27e0e1f12d6eaf6bc6906751b25dd305a\"},\"dev/codex/schubert/nk/batch/file/MorningBackupCompletion\":{\"module\":\"batch\",\"name\":\"dev/codex/schubert/nk/batch/file/MorningBackupCompletion\",\"sha256\":\"aa0cbbd857fc274a2a09f5f1563602ef23f8e7530f6bf425b11148c5e0c5b43b\"}}")
CLOSURES=json.loads("{\"dev/codex/schubert/nk/batch/file/MorningBackupPreparation\":[\"dev/codex/schubert/nk/batch/file/MorningBackupPreparation\",\"dev/codex/schubert/nk/batch/file/MorningBackupPreparation$Continuation\",\"dev/codex/schubert/nk/batch/file/MorningBackupPreparation$Publisher\"],\"dev/codex/schubert/nk/batch/file/MorningBackupCompletion\":[\"dev/codex/schubert/nk/batch/file/MorningBackupCompletion\"]}")
METADATA=set(json.loads("[\"dev/codex/schubert/nk/batch/file/MorningBackupPreparation$Continuation\",\"dev/codex/schubert/nk/batch/file/MorningBackupPreparation$Publisher\"]"))
COUNTS=json.loads("{\"MorningBackupPreparationTest\":6,\"MorningBackupCompletionTest\":2}")
PINS=json.loads("{\"MorningBackupPreparationTest\":\"88b9b065043bbec45d836635cab6c7119f740a888abc0e068f396d622f11984a\",\"MorningBackupCompletionTest\":\"8c04d23af4a8b217c6132716630c0d3318c8a44584a29004aec2bdbe07ecb939\"}")
EXTRAS=json.loads("{\"platform/ExpiryReceiptFixture.java\":\"abf309d8c2126bbad37c7c2024c95aa6a59965f74053f306fd7ed337c7747375\",\"repository/BackupStepFixture.java\":\"c41b963d540a369a519b5a3b3504faf8187ab6f63f3dde5d72f59aad3e3171ec\",\"repository/BatchDatabaseFixture.java\":\"ad3567863c78e5cbbbe28cd1c2b38c2005113abb3bd0f9184cda190d0c886023\"}")
FIXTURES=json.loads("{}")
SESSION='PG16648-MORNING-BACKUP-HANDOFF-ORIGINAL-EIGHT'
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch'
TESTS={name:ROOT/'file'/(name+'.java') for name in COUNTS}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG16647-handoff-static-review-equivalence-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    old=data.read_checked(data.BASE/'PG13936-morning-backup-handoff-whole-eight-pt-v1/manifest.json','f954b3d94e705c742822ed8bb83c685f5599386b0bafba3f527654b54ca1cd14')
    before=old['begin']['sourceHashes'];current=normal['begin']['inputHashes']
    changed=sorted(p for p in before.keys()|current.keys() if before.get(p)!=current.get(p))
    prefix='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/'
    assert changed==sorted(prefix+p for p in ['question/QuestionQueryApplicationService.java','admin/UserQueryApplicationService.java','log/LogQueryApplicationService.java'])
    assert normal['source']==SOURCE and old['source']=='0061d178cda80c2ce3926290619c64db125dbcfc'
    previous=data.read_checked(data.BASE/'PG16638-current2315-family-disclosure-registry-v1/manifest.json','3cdc3ae1a4d5d022b461d00366eb7f00b11b8b89b3444029ec597ffc3ae23401')
    assert previous['source']==SOURCE and not set(MAIN_UNITS)&previous['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));text=path.read_text()
        assert run.host.sha(path)==PINS[name]==current[relative]==before[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.file.'+name not in previous['suiteNames']
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningParentBudget.create','MorningProcessMain.runCompleted(','MorningProcessMain.main(','RootFailedStartRecovery'])
    for path,pin in EXTRAS.items():assert run.host.sha(ROOT/path)==pin==current[str((ROOT/path).relative_to(data.ROOT))]==before[str((ROOT/path).relative_to(data.ROOT))]
    for path,pin in FIXTURES.items():assert run.host.sha(data.ROOT/path)==pin==current[path]==before[path]
    with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
        for name,row in MAIN_UNITS.items():
            path=source_path(row);assert row['sha256']==current[path]==before[path]==run.host.sha(data.ROOT/path)
            assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    reviews=['evidence/01_PT/018_NK-OPS-001/2542_MorningBackupHandoff_memory全8_通常PT仕様.md']
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reuseKind='UNCHANGED_STATIC_REVIEW_INPUTS_NOT_RUNTIME_RESULTS',priorSource=old['source'],priorPublicInputManifestSha256='f954b3d94e705c742822ed8bb83c685f5599386b0bafba3f527654b54ca1cd14',currentNormalManifestSha256=COMPILE_SHA,changedPathsOutsideReviewedBatchCallTree=changed,reviewDocuments={p:run.host.sha(data.ROOT/p) for p in reviews},originalWholeSuites=COUNTS,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16648-morning-backup-handoff-original-eight-pt-v1';run.OUT=data.BASE/'PG16648-morning-backup-handoff-original-eight-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/MorningBackupHandoffCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MorningBackupPreparationTest'];run.TEST_ROOT=ROOT/'file'
    run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
