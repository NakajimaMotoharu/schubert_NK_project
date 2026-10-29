"""Four original file/time/topology20 suites: pure values and supplied memory streams only."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"MediaDescriptorValidatorTest":7,"LargeResultRecordCodecTest":7,"JstWireTimestampTest":4,"BrokerTopologyTest":2}
SESSION='PG14364-ORIGINAL-PROTOCOL-FILE-TIME-TOPOLOGY20'
ROOT=run.host.ROOT/'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/file'
TESTS={n:(ROOT.parent/('time' if n=='JstWireTimestampTest' else 'transport') if n in {'JstWireTimestampTest','BrokerTopologyTest'} else ROOT)/(n+'.java') for n in COUNTS}
PINS={"MediaDescriptorValidatorTest":"97faf48280d3d1e6fdf24cae984fae531f718545274c4567f9ca4c26b163ab34","LargeResultRecordCodecTest":"fd37c828db9db48c3bb81eb6b4c1382bf314143c967d8eea0afb6d2869ed92ef","JstWireTimestampTest":"588bc19f5035c5b1d9e80979fc5376274a7ebace6df91d8f68fa1eec1e6f8c61","BrokerTopologyTest":"96e98d5d674681c90c863b7150c9fcfdb17c69e89d63f9462569daa004ab2630"}
FIXTURES={}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14364-protocol-file-time-topology-whole-twenty-pt-v1'
    run.OUT=run.host.BASE/'PG14364-protocol-file-time-topology-whole-twenty-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalProtocolFileTimeTopologyJunitLauncher.java'
    run.NEW_TEST=TESTS['MediaDescriptorValidatorTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='MediaDescriptorValidatorTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"dev.codex.schubert.nk.protocol.'+('time.' if name=='JstWireTimestampTest' else 'transport.' if name=='BrokerTopologyTest' else 'file.')+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step
    run.main()
