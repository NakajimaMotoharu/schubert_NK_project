"""Seven original semantic31 suites with original public named-field oracle and fixed TSV; pure values only."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"SemanticFieldValueTest":4,"PayloadSemanticValidatorTest":8,"SemanticDirectBoundaryTest":3,"PayloadTypeCatalogTest":6,"PayloadPaginationBoundaryTest":3,"ProtocolSemanticTypeTest":5,"EnumWireCompatibilityTest":2}
SESSION='PG14360-ORIGINAL-PROTOCOL-SEMANTIC31'
ROOT=run.host.ROOT/'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout'
TESTS={name:(ROOT/'semantic' if name in {'ProtocolSemanticTypeTest','EnumWireCompatibilityTest'} else ROOT)/(name+'.java') for name in COUNTS}
PINS={"SemanticFieldValueTest":"b399e53307dabab625ac8cd2449b8edf87c8873e47265cdbea806d907c86354f","PayloadSemanticValidatorTest":"fe63057e3a11162c11ef99ed376885da8c8b8202f41fbe0c4a10977f691d425c","SemanticDirectBoundaryTest":"a1febb6ee40532721d36d3928b9957a2efe4fafd7d2dda6d6e9dfa49f0d3b459","PayloadTypeCatalogTest":"81a4bddc084404e7e50234d039316b66cb1ba30a7c0fc27c50d191e7fb33c9fd","PayloadPaginationBoundaryTest":"6f8038c90b3854656b38c6b641a0c6ae4f5d0db66a12c562edf594e52c9c739d","ProtocolSemanticTypeTest":"dd40230045fec910c3ab2d1cada147a56859a8ff1d3081c70891551b061ba5aa","EnumWireCompatibilityTest":"e62586bd50012c93080f1772c5c2cb670837b8542d6fc6a6cf1c0e9527a58213"}
FIXTURES={"src/schubert-nk-protocol/src/test/resources/protocol/fields-ui234-236.tsv":"b07bd90705a4761ebcc97b859bd495dadaf26501fcee3b60c4edd72474a4811b","src/schubert-nk-protocol/src/test/resources/protocol/named-types-ss323.tsv":"9529fce86672b27a435665331648110521be6f59c5fe3fe5ca516df5234c7a76","src/schubert-nk-protocol/src/test/resources/protocol/named-accessors-independent.tsv":"27b9a458374f5b9edda50d78fae42ee76dabf15d8d1ecd9c94e56dbab63162d5"}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14360-protocol-semantic-whole-thirty-one-pt-v1'
    run.OUT=run.host.BASE/'PG14360-protocol-semantic-whole-thirty-one-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalProtocolSemanticJunitLauncher.java'
    run.NEW_TEST=TESTS['SemanticFieldValueTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='SemanticFieldValueTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,ROOT/'IndependentNamedFieldOracle.java');run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"dev.codex.schubert.nk.protocol.'+('layout.semantic.' if name in {'ProtocolSemanticTypeTest','EnumWireCompatibilityTest'} else 'layout.')+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    assert run.host.sha(ROOT/'IndependentNamedFieldOracle.java')=='7fefc742055add410ebcb49991a8f30fb5a71e29d3d9c2908a053b8f17109a7d'
    run.step=environmental_step
    run.main()
