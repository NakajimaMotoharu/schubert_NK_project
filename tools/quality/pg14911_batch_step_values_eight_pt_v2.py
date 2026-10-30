"""Original whole immutable step8; diagnostic nested record only, never constructs parent Repository/DB."""
import re
import classfile_code_metadata as code
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'BatchStepValuesTest':8}
SESSION='PG14911-ORIGINAL-BATCH-STEP-VALUES8'
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository'
TESTS={'BatchStepValuesTest':ROOT/'BatchStepValuesTest.java'}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14911-batch-step-values-eight-pt-v2';run.OUT=data.BASE/'PG14911-batch-step-values-eight-pt-v2'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalBatchStepValuesJunitLauncher.java';run.NEW_TEST=TESTS['BatchStepValuesTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);p=run.NEW_TEST;relative=str(p.relative_to(data.ROOT))
    assert normal['begin']['inputHashes'][relative]==run.host.sha(p)==run.host.sha(COMPILE/'snapshot'/relative)=='4f6c9eca1af5970e44717d214fa1ef83459c853268548f33633cf65ba0d32a81'
    text=p.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==8
    assert text.count('Class.forName(')==1 and 'Class.forName("dev.codex.schubert.nk.batch.repository.BatchRunRepository$History")' in text
    assert not any(term in text for term in ['new BatchRunRepository','ProcessBuilder','DriverManager','Files.','Linux','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
    history=COMPILE/'snapshot/src/schubert-nk-batch/target/classes/dev/codex/schubert/nk/batch/repository/BatchRunRepository$History.class'
    binary='dev/codex/schubert/nk/batch/repository/BatchRunRepository$History.class'
    parsed=code.decode(history.read_bytes(),binary)
    for wrong in ['BatchRunRepository$History.class','dev/codex/schubert/nk/batch/repository/Other.class']:
        try:code.decode(history.read_bytes(),wrong)
        except ValueError:pass
        else:raise AssertionError('wrong binary name accepted')
    assert parsed['sourceFile']=='BatchRunRepository.java' and '<clinit>' not in {m['name'] for m in parsed['methods']} and {'<init>','toString'}<={m['name'] for m in parsed['methods']}
    assert '"dev.codex.schubert.nk.batch.repository.BatchStepValuesTest", 8' in run.HELPER.read_text()
    run.step=environmental_step;run.main()
