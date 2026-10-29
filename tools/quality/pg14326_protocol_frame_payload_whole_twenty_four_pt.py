"""Five original whole codec24 suites plus three exact public TSV fixtures, no broker or live auth operations."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'MessageCodecTest':7,'PayloadCodecTest':8,'PayloadGoldenVectorTest':3,'ScenarioRecordEncodingTest':3,'AuthenticationErrorProfileTest':3}
SESSION='PG14326-ORIGINAL-PROTOCOL-FRAME-PAYLOAD24'
ROOT=run.host.ROOT/'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/codec'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={'MessageCodecTest':'65e12cc4b54b26c0730e868925a88bc0f335061113d3b77cb90f4a9e195f23ca','PayloadCodecTest':'becfdcb277f693d7f8f70a06e1b5a32361d84856314a66f2116625d80b264970','PayloadGoldenVectorTest':'d9828b15fcf0655bdb0ffa2028c6812e1600866c9e230d3d649a9d075a6604ad','ScenarioRecordEncodingTest':'53352d9758286a925435d60aba66ad2637610d1cd4cfd01d286d7a4bef764a15','AuthenticationErrorProfileTest':'41ebd3cd62dc2c154a9a6aa89bb7152f5a6e52e6f62a2fcaf673a60be27bd93a'}
FIXTURES={'src/schubert-nk-protocol/src/test/resources/protocol/payload-golden-ui234-236.tsv':'49bb76ec610216042f8e53ed548f4d5e52707a8bbf930a9fc6c93300dfa24839','src/schubert-nk-protocol/src/test/resources/protocol/fields-ui234-236.tsv':'b07bd90705a4761ebcc97b859bd495dadaf26501fcee3b60c4edd72474a4811b','src/schubert-nk-protocol/src/test/resources/protocol/layouts-ui233.tsv':'c4f290595f5cabf19c11877e2dea95627b4d42490116431bac3bfde58950d711'}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14326-protocol-frame-payload-whole-twenty-four-pt-v1'
    run.OUT=run.host.BASE/'PG14326-protocol-frame-payload-whole-twenty-four-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalProtocolFramePayloadJunitLauncher.java'
    run.NEW_TEST=TESTS['MessageCodecTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"dev.codex.schubert.nk.protocol.codec.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step
    run.main()
