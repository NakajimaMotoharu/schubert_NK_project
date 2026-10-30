"""Original RequiredColumn1; object identity/null SQLSTATE only, no actual JDBC."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"RequiredColumnTest":1}
SESSION='PG15307-ORIGINAL-REQUIRED-COLUMN1'
ROOT=data.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/database'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={"RequiredColumnTest":"27d0c6689cca24bba7735330ab00b8211a89475a3bc23dae04b77f9ee11f118a"}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15307-required-column-one-pt-v2';run.OUT=data.BASE/'PG15307-required-column-one-pt-v2'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalRequiredColumnJunitLauncher.java';run.NEW_TEST=TESTS['RequiredColumnTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='RequiredColumnTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG15284-current1748-profile-terminal-registry-v1/manifest.json','7bc09027b74939ddc45fb92d63bb82be1c096f898670f275bed940cbe507435d')
    assert not {'dev.codex.schubert.nk.api.database.'+name for name in COUNTS}&set(registry['suiteNames'])
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert text.count('@Test')==text.count('void requiredValuesRetainIdentityAndNullFailsWithSqlState()')==COUNTS[name]
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','FileSystems.','getFileStore(','Linux','getenv(','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','HttpClient','Clock.system'])
        assert not re.search(r'\.\s*(?:gc|setVerbose|dumpHeap)\s*\(',text)
        assert '"dev.codex.schubert.nk.api.database.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    files_call=re.compile(r'(?<![A-Za-z0-9_])Files\s*\.')
    assert not files_call.search('ServiceConfigFiles.Service.WEB') and all(files_call.search(v) for v in ['Files.readString(x)','java.nio.file.Files.readString(x)','Files.delete(x)'])
    assert not files_call.search(TESTS['RequiredColumnTest'].read_text())
    assert all('new ApiProcessMain(' not in p.read_text() and '.run(' not in p.read_text() and '.main(' not in p.read_text() for p in TESTS.values())
    def sql_imports(text):return re.findall(r'^import\s+(java\.sql\.[A-Za-z0-9_.]+)\s*;',text,re.MULTILINE)
    assert sql_imports(TESTS['RequiredColumnTest'].read_text())==['java.sql.SQLDataException']
    assert all(sql_imports('import '+name+';')!=['java.sql.SQLDataException'] for name in ['java.sql.Connection','java.sql.DriverManager','java.sql.Statement'])
    assert not any(term in TESTS['RequiredColumnTest'].read_text() for term in ['getConnection(','DataSource','DriverManager','PreparedStatement'])
    run.step=environmental_step;run.main()
