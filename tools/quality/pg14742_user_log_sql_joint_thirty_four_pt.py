"""Whole valid JDBC-interface18 plus necessary original plain16 in one current exec; never DB."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
from pg14647_storage_catalog_whole_five_pt_v2 import source_operation_allowed
import pg14630_api_plain_whole_sixteen_pt as plain
from reviewed_jdbc_fixture_scope_v2 import eligible
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE=plain.SOURCE
COMPILE=plain.COMPILE
COMPILE_SHA=plain.COMPILE_SHA
COUNTS={**plain.COUNTS,'UserQuerySqlContractTest':9,'LogSqlContractTest':9}
SESSION='PG14742-ORIGINAL-USER-LOG-SQL-JOINT34'
ROOT=plain.ROOT
PATHS={**plain.TEST_PATHS,
 'UserQuerySqlContractTest':'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/UserQuerySqlContractTest.java',
 'LogSqlContractTest':'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/log/LogSqlContractTest.java'}
TESTS={n:data.ROOT/p for n,p in PATHS.items()}
PINS={**plain.PINS,'UserQuerySqlContractTest':'7c08ce9b15f707354b77a02537dafa95d3c21c2976d522ca9c8b436ea2492bb9','LogSqlContractTest':'e364cbaac8b3438dd07fb904938b13bb70673ee43836da55d4c788208335eddf'}
FIXTURES={}
REPORTER=plain.REPORTER
SQL_NAMES={'UserQuerySqlContractTest','LogSqlContractTest'}
REQUIRED={n:('Proxy.newProxyInstance(','Connection.class','PreparedStatement.class','ResultSet.class','case "getAutoCommit" -> false','case "isReadOnly" -> true','List.of("RS", "PS")') for n in SQL_NAMES}

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14742-user-log-sql-joint-thirty-four-pt-v1';run.OUT=data.BASE/'PG14742-user-log-sql-joint-thirty-four-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalUserLogSqlJointJunitLauncher.java'
    run.NEW_TEST=TESTS['UserQueryCanonicalCoreTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='UserQueryCanonicalCoreTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);assert normal['source']==SOURCE
    texts={}
    for n,p in TESTS.items():
        assert p.parent.parent==ROOT and p.parent.name in {'admin','log'} and str(p.relative_to(data.ROOT))==PATHS[n]
        assert run.host.sha(p)==normal['begin']['inputHashes'][PATHS[n]]==run.host.sha(COMPILE/'snapshot'/PATHS[n])==PINS[n]
        text=p.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[n]
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','@AfterAll','@TempDir','TemporaryInfrastructureException','preserveFatal(','Mac.','Cipher.'])
        fq=PATHS[n].split('/src/test/java/',1)[1][:-5].replace('/','.')
        assert '"'+fq+'", '+str(COUNTS[n]) in run.HELPER.read_text()
        if n in SQL_NAMES:texts[n]=text
        else:assert source_operation_allowed(text)
    assert eligible(texts,REQUIRED)
    for forbidden in ['DriverManager','DataSource','getConnection(','Class.forName(','ProcessBuilder','preserveFatal(']:
        bad=dict(texts);bad['UserQuerySqlContractTest']+='\n'+forbidden
        assert not eligible(bad,REQUIRED)
    run.step=environmental_step;run.main()
