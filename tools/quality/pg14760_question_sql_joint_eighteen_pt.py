"""Whole valid Question/Notification SQL10 plus necessary original plain8, no actual DB."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
from pg14647_storage_catalog_whole_five_pt_v2 import source_operation_allowed
from reviewed_jdbc_fixture_scope_v2 import eligible
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'QuestionQueryPlainContractTest':8,'QuestionSqlContractTest':10}
SESSION='PG14760-ORIGINAL-QUESTION-SQL-JOINT18'
ROOT=data.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={'QuestionQueryPlainContractTest':'4ebc371e0b1680ad73d5a137eecaff9ca77976ca222304c13cc027a8325c1132','QuestionSqlContractTest':'091d86412f47c06d63eb91df04eabd1e1bab46ec5721cb0ebd7fafd333e8f576'}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
REQUIRED={'QuestionSqlContractTest':('Proxy.newProxyInstance(','Connection.class','PreparedStatement.class','ResultSet.class','case "getAutoCommit" -> false','case "isReadOnly" -> true','List.of("RS", "PS")')}

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14760-question-sql-joint-eighteen-pt-v1';run.OUT=data.BASE/'PG14760-question-sql-joint-eighteen-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalQuestionSqlJointJunitLauncher.java'
    run.NEW_TEST=TESTS['QuestionQueryPlainContractTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={'QuestionSqlContractTest':TESTS['QuestionSqlContractTest']}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);assert normal['source']==SOURCE
    for n,p in TESTS.items():
        relative=str(p.relative_to(data.ROOT));assert relative=='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/'+n+'.java'
        assert run.host.sha(p)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==PINS[n]
        text=p.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[n]
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','@AfterAll','@TempDir','TemporaryInfrastructureException','preserveFatal(','Mac.','Cipher.'])
        assert '"dev.codex.schubert.nk.api.application.question.'+n+'", '+str(COUNTS[n]) in run.HELPER.read_text()
        if n=='QuestionSqlContractTest':assert eligible({n:text},REQUIRED)
        else:assert source_operation_allowed(text)
    text=TESTS['QuestionSqlContractTest'].read_text()
    for forbidden in ['DriverManager','DataSource','getConnection(','Class.forName(','ProcessBuilder','preserveFatal(']:assert not eligible({'QuestionSqlContractTest':text+'\n'+forbidden},REQUIRED)
    run.step=environmental_step;run.main()
