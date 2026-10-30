"""Whole original ContextHash suite, child-local JCA registry/thread state only."""
import hashlib
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'ContextHashTest':3}
SESSION='PG15418-CONTEXT-HASH-CURRENT-WHOLE3'
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={'ContextHashTest':'eafd2eb1a16ac85b8d8eb40f1d75cdcf49c0c894c9d08c883d546b233e62b353'}
FIXTURES={}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15418-context-hash-three-pt-v1'
    run.OUT=run.host.BASE/'PG15418-context-hash-three-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ContextHashCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['ContextHashTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    text=TESTS['ContextHashTest'].read_text();assert run.host.sha(TESTS['ContextHashTest'])==PINS['ContextHashTest']
    assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==3
    assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv('])
    for value,expected in [('a','ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb'),('b','a0fab1377f49a759b57f63318262ebe89fabfc990e8e93ceac2984561482b9d4')]:
        assert hashlib.sha256((value*64).encode('ascii')).hexdigest()==expected and expected in text
    assert 'finally {' in text and 'assertArrayEquals(original, Security.getProviders());' in text
    assert '"dev.codex.schubert.nk.api.security.ContextHashTest", 3' in run.HELPER.read_text()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15408-current1800-exact12-owner-registry-v3/manifest.json','75c239f0250f38bb7ed4f6d9cf812eaaf8dd6766f38e93d917f81be0ae287640')
    name='dev/codex/schubert/nk/api/security/ContextHash';main='src/schubert-nk-api/src/main/java/'+name+'.java'
    assert name not in current['fullSourceUnits'] and 'dev.codex.schubert.nk.api.security.ContextHashTest' not in current['suiteNames']
    assert normal['begin']['inputHashes'][main]==run.host.sha(run.host.ROOT/main)==run.host.sha(COMPILE/'snapshot'/main)=='9b0714ec9dc88f3f15e11341d71d873250fee8436ebad03b3fb1079060392581'
    path=str(TESTS['ContextHashTest'].relative_to(run.host.ROOT))
    assert normal['begin']['inputHashes'][path]==run.host.sha(COMPILE/'snapshot'/path)==PINS['ContextHashTest']
    assert run.host.sha(run.HELPER)=='aa25e79c7e05fc281f6eb9709b596c8d07158d56553ed4efdd718e3358d496aa'
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+') and p.endswith('.class')}=={name}
    run.step=environmental_step;run.main()
