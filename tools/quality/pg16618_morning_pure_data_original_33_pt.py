"""Current-source whole33; reuse unchanged static review only, never old Product results."""
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
MAIN_UNITS=json.loads("{\"dev/codex/schubert/nk/batch/file/MorningPrestartEvidence\":{\"module\":\"batch\",\"name\":\"dev/codex/schubert/nk/batch/file/MorningPrestartEvidence\",\"sha256\":\"f04b8a65d583e42b655bc769d1dc69218e50b57a3c4f9664caa4aade954498a8\"},\"dev/codex/schubert/nk/batch/file/MorningCompletionEvidence\":{\"module\":\"batch\",\"name\":\"dev/codex/schubert/nk/batch/file/MorningCompletionEvidence\",\"sha256\":\"6e8eca6f18bfd2a3ef516edb4e6825c2a435f6f5cdd3c98af0065b7d679ccf27\"},\"dev/codex/schubert/nk/batch/file/MorningCompletionChecks\":{\"module\":\"batch\",\"name\":\"dev/codex/schubert/nk/batch/file/MorningCompletionChecks\",\"sha256\":\"aaf7bd560303448b658017fe295435e342d89f0ab21e0be0bdabe3303326ebf9\"},\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner\":{\"module\":\"batch\",\"name\":\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner\",\"sha256\":\"caca5ef9c6f8ab5e5084bf0ee363871b5e61fce4f023fd3daf9ca484faa0d99a\"}}")
CLOSURES=json.loads("{\"dev/codex/schubert/nk/batch/file/MorningPrestartEvidence\":[\"dev/codex/schubert/nk/batch/file/MorningPrestartEvidence\"],\"dev/codex/schubert/nk/batch/file/MorningCompletionEvidence\":[\"dev/codex/schubert/nk/batch/file/MorningCompletionEvidence\",\"dev/codex/schubert/nk/batch/file/MorningCompletionEvidence$Read\"],\"dev/codex/schubert/nk/batch/file/MorningCompletionChecks\":[\"dev/codex/schubert/nk/batch/file/MorningCompletionChecks\"],\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner\":[\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner\",\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner$Stop\",\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner$Launch\",\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner$CompletionProgress\",\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner$CompletionRetirement\",\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner$Completion\",\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner$Started\",\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner$ApiRetained\",\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner$CompletionPhase\"]}")
METADATA=set(json.loads("[\"dev/codex/schubert/nk/batch/file/MorningCompletionEvidence$Read\",\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner$Stop\",\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner$Launch\",\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner$CompletionRetirement\",\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner$Completion\",\"dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner$ApiRetained\"]"))
COUNTS=json.loads("{\"MorningBackupObservedCompletionTest\":2,\"MorningCompletionChecksTest\":5,\"MorningCompletionEvidenceTest\":11,\"MorningCompletionRetirementTest\":6,\"MorningPrestartEvidenceTest\":5,\"StoppedBackupCompletionTest\":4}")
PINS=json.loads("{\"MorningBackupObservedCompletionTest\":\"69e9b899b3d8fb8825563d50f9e8fafa628911f316fd2e2ca8bd19710bff2f10\",\"MorningCompletionChecksTest\":\"f725443f8c024f5b8406605341f33971634515743b03c9e1a8dd37c5d872c598\",\"MorningCompletionEvidenceTest\":\"1f52f96a806c8d38bb2df64d2eb0376f25b344af6f3428e4ff00f009d86f3b0c\",\"MorningCompletionRetirementTest\":\"c24a17af3121d4121e1df4bf0de4c4c81708197d651a9a290003c446e18ffdf8\",\"MorningPrestartEvidenceTest\":\"b58a35ec59e2f413756b7acb5bcf779939348df891d8cb12937b9af0fbc18440\",\"StoppedBackupCompletionTest\":\"a01fc1385cdbf56e06787116be9178b1707314acee83a5a475541bcd6c80c49b\"}")
EXTRAS=json.loads("{\"file/MorningCompletedMainTest.java\":\"2ebc63c919fc2db084c905f67191f6927fc37bc45d80a10b60a52e792c0d04b6\",\"platform/ExpiryReceiptFixture.java\":\"abf309d8c2126bbad37c7c2024c95aa6a59965f74053f306fd7ed337c7747375\",\"platform/StoppedBackupFixture.java\":\"11ef7eaebae015e6d42f8b8808c5e794be382b0e316b32e03253e426cd2c070b\",\"repository/BackupStepFixture.java\":\"c41b963d540a369a519b5a3b3504faf8187ab6f63f3dde5d72f59aad3e3171ec\",\"repository/BatchDatabaseFixture.java\":\"ad3567863c78e5cbbbe28cd1c2b38c2005113abb3bd0f9184cda190d0c886023\"}")
FIXTURES=json.loads("{\"src/schubert-nk-batch/src/test/resources/ops/issuer-prestart-failed-v2-golden.txt\":\"eda4285f0df2c54a4ca10946013dbfc145440da6999637ca035f56ec86a66d4a\",\"src/schubert-nk-batch/src/test/resources/ops/issuer-prestart-new-v2-golden.txt\":\"842b41b0e1f131f65fef2127bee72ae840e94dfa67c4c3240799608d8a553b1c\",\"src/schubert-nk-batch/src/test/resources/ops/issuer-prestart-reused-v2-golden.txt\":\"f5877b39aece1cbbd31e9016fdb34ea65fb4ddc933e93428ab4d6b2f0ad6849e\"}")
SESSION='PG16618-MORNING-PURE-DATA-AND-BOUNDARIES-33'
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch'
TESTS={name:ROOT/'file'/(name+'.java') for name in COUNTS}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG16617-morning-static-review-equivalence-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    old=data.read_checked(data.BASE/'PG13904-morning-data-envelopes-whole-twenty-pt-v1/manifest.json','3cb373c20b75009922a836d586140ab315c109745a407e7d990fccc969125bd8')
    before=old['begin']['sourceHashes'];current=normal['begin']['inputHashes']
    changed=sorted(p for p in before.keys()|current.keys() if before.get(p)!=current.get(p))
    prefix='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/'
    assert changed==sorted(prefix+p for p in ['question/QuestionQueryApplicationService.java','admin/UserQueryApplicationService.java','log/LogQueryApplicationService.java'])
    assert normal['source']==SOURCE and old['source']=='0061d178cda80c2ce3926290619c64db125dbcfc'
    previous=data.read_checked(data.BASE/'PG16608-current2282-application-unit-registry-v1/manifest.json','2474e9273df26df9b0d3af9822dbe6ebb927429ef9e1f0b72b9543b2d6b9576e')
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
    reviews=['evidence/01_PT/018_NK-OPS-001/2534_MorningDataEnvelope全20_通常PT仕様.md','evidence/01_PT/018_NK-OPS-001/2536_MorningCompletionBoundary全13_通常PT仕様.md']
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reuseKind='UNCHANGED_STATIC_REVIEW_INPUTS_NOT_RUNTIME_RESULTS',priorSource=old['source'],priorPublicInputManifestSha256='3cb373c20b75009922a836d586140ab315c109745a407e7d990fccc969125bd8',currentNormalManifestSha256=COMPILE_SHA,changedPathsOutsideReviewedBatchCallTree=changed,reviewDocuments={p:run.host.sha(data.ROOT/p) for p in reviews},originalWholeSuites=COUNTS,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16618-morning-pure-data-original-33-pt-v1';run.OUT=data.BASE/'PG16618-morning-pure-data-original-33-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/MorningPure33CurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MorningPrestartEvidenceTest'];run.TEST_ROOT=ROOT/'file'
    run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
