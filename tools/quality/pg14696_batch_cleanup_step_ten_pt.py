"""Whole original counts/step values10; no SQL, cleanup service or actual resource."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
from pg14647_storage_catalog_whole_five_pt_v2 import source_operation_allowed,source_prevention
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'CleanupValueBoundaryTest':2,'CleanupStepValuesTest':8}
SESSION='PG14696-ORIGINAL-BATCH-CLEANUP-STEP10'
ROOT=run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={'CleanupValueBoundaryTest':'cb48cfbd5ae24de7bfc4f483aba7226402f0a4443602a26ebc4fb8b675c4ed16','CleanupStepValuesTest':'d9a284a002c02b27a17480e6c554f0d6af3b31384bcc7048d12a14eee70e055c'}
FIXTURES={}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14696-batch-cleanup-step-ten-pt-v1'
    run.OUT=run.host.BASE/'PG14696-batch-cleanup-step-ten-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalBatchCleanupStepJunitLauncher.java'
    run.NEW_TEST=TESTS['CleanupValueBoundaryTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='CleanupValueBoundaryTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    assert normal['source']==SOURCE and source_prevention()==6
    for n,p in TESTS.items():
        relative=str(p.relative_to(run.host.ROOT))
        assert relative=='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/'+n+'.java'
        assert normal['begin']['inputHashes'][relative]==run.host.sha(p)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[n]
        text=p.read_text()
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[n] and source_operation_allowed(text)
        assert '"dev.codex.schubert.nk.batch.repository.'+n+'", '+str(COUNTS[n]) in run.HELPER.read_text()
    run.step=environmental_step;run.main()
