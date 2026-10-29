"""Whole original ContextHash suite, child-local JCA registry/thread state only."""
import hashlib
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='0061d178cda80c2ce3926290619c64db125dbcfc'
COMPILE=run.host.W/'pg13832-snapshot-program-six-compile-v1'
COMPILE_SHA='8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
COUNTS={'ContextHashTest':3}
SESSION='PG14092-CONTEXT-HASH-CURRENT-WHOLE3'
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={'ContextHashTest':'eafd2eb1a16ac85b8d8eb40f1d75cdcf49c0c894c9d08c883d546b233e62b353'}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14092-context-hash-whole-three-pt-v1'
    run.OUT=run.host.BASE/'PG14092-context-hash-whole-three-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ContextHashCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['ContextHashTest'];run.TEST_SOURCE_OVERRIDES={}
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
    run.main()
