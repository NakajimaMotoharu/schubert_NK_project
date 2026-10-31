"""Whole original Acceptor JSON object2; injected readers and unused session only."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/batch/'
MAIN_PINS={"mq/ArtemisAcceptorReadinessClient":"32bdcede64efafb409107c400bab7b0ec74953b6c4fb5a1e8a018429a5c49ab8","mq/ArtemisManagementReadinessException":"6b3e87f566e3901e1674a14d3dcad7d3cc60bbcb938ed505ddf6553d3bf6346d"}
CLOSURES={"mq/ArtemisAcceptorReadinessClient":["mq/ArtemisAcceptorReadinessClient","mq/ArtemisAcceptorReadinessClient$Reader"],"mq/ArtemisManagementReadinessException":["mq/ArtemisManagementReadinessException"]}
ROOT=run.host.ROOT/'src/schubert-nk-batch/src/test/java'/PREFIX
TESTS={'AcceptorObjectBoundaryTest':ROOT/'mq/AcceptorObjectBoundaryTest.java'}
COUNTS={'AcceptorObjectBoundaryTest':2}
PINS={'AcceptorObjectBoundaryTest':'0b69334562a3d1e8d0ef7c1dc0729b40384689d4e71918e79c939eaf988713c5'}
FIXTURES={}
SUPPORT_PINS={}
SESSION='PG15788-ACCEPTOR-JSON-WHOLE2'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15788-acceptor-json-two-pt-v1';run.OUT=run.host.BASE/'PG15788-acceptor-json-two-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/AcceptorJsonTwoJunitLauncher.java'
    run.NEW_TEST=TESTS['AcceptorObjectBoundaryTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={};run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='e0c5e02f97d11845a6a70aa1ab2ab4f916e189297404c50cde98aeb4e6734baa'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15778-current2026-artemis-values-registry-v1/manifest.json','dfc4ce5dd3bcb7f674aeadf10e0c23324343814dfebf64ba6f6dd2febca43776')
    path=run.NEW_TEST;text=path.read_text();relative=str(path.relative_to(run.host.ROOT))
    assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==PINS[path.stem]
    assert text.count('@Test')==len(re.findall(r'(?m)^  void [A-Za-z0-9_]+\(',text))==2
    assert not any(v in text for v in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','getConnection(','TemporaryInfrastructureException','WebStartupException','Class.forName(','HttpClient','createConnection(','createContext(','withParentDeadline(','new ArtemisStartupObservation('])
    assert 'data-only reader must never use borrowed session' in text and 'throw new AssertionError' in text
    assert 'dev.codex.schubert.nk.batch.mq.AcceptorObjectBoundaryTest' not in current['suiteNames']
    with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
        for short,pin in MAIN_PINS.items():
            name=PREFIX+short;relative='src/schubert-nk-batch/src/main/java/'+name+'.java'
            assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][relative]==run.host.sha(run.host.ROOT/relative)==run.host.sha(COMPILE/'snapshot'/relative)==pin
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}=={PREFIX+p for p in CLOSURES[short]}
    run.step=environmental_step;run.main()
