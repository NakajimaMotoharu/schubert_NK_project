"""New fixed-oracle six-case pure value PT; original31 never reexecuted or unioned."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'ProtocolCarrierBoundaryTest':6}
SESSION='PG14868-PROTOCOL-CARRIER-BOUNDARY6'
ROOT=data.ROOT/'tools/quality/architecture'
TESTS={'ProtocolCarrierBoundaryTest':ROOT/'ProtocolCarrierBoundaryTest.java'}
FIXTURES={}
REPORTER=ROOT/'SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14868-protocol-carrier-boundary-six-pt-v1';run.OUT=data.BASE/'PG14868-protocol-carrier-boundary-six-pt-v1'
    run.HELPER=ROOT/'ProtocolCarrierBoundaryJunitLauncher.java';run.NEW_TEST=TESTS['ProtocolCarrierBoundaryTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.NEW_TEST)=='bd1da8b0168836610a5d7a28ec4b3af127dfca86d15c0a7bbabb98282f841003' and run.host.sha(run.HELPER)=='5132d00764b008cd80c085c803d7af44b10ea0dda11c645187ca7d69fbd090bd'
    text=run.NEW_TEST.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==6
    assert not any(term in text for term in ['ProcessBuilder','DriverManager','Files.','Linux','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
    assert '"dev.codex.schubert.nk.protocol.layout.ProtocolCarrierBoundaryTest", 6' in run.HELPER.read_text()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    for relative,pin in [('FieldValue','6f50d333720aaedf58b714be1f84c298297ae80398e8b8f7afb0ec7341d98041'),('FieldValueSet','2c292124a30ee4ed275ad2d43818b46c73c8f5648edd60914992da786e6f555b')]:
        path='src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/'+relative+'.java'
        assert normal['begin']['inputHashes'][path]==run.host.sha(data.ROOT/path)==pin
    run.step=environmental_step;run.main()
