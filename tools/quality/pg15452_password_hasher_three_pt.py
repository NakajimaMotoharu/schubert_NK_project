"""Original PasswordHasher3, public synthetic passwords and standard JCA PBKDF2 only."""
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'PasswordHasherTest':3}
SESSION='PG15452-PASSWORD-HASHER-CURRENT-WHOLE3'
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={'PasswordHasherTest':'a44c27a8e9b3869fd01ef90dae2a28bfebc0f5f78b4bd0d417b12eb3b319daae'}
FIXTURES={}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15452-password-hasher-three-pt-v1'
    run.OUT=run.host.BASE/'PG15452-password-hasher-three-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/PasswordHasherCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['PasswordHasherTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    text=TESTS['PasswordHasherTest'].read_text();assert run.host.sha(TESTS['PasswordHasherTest'])==PINS['PasswordHasherTest']
    assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==3
    assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv('])
    assert all(v in text for v in ['independentHash(', 'PBEKeySpec(value.toCharArray(), salt, 310_000, 256)', 'SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")', 'spec.clearPassword()', 'assertArrayEquals(new char[input.length], input)'])
    assert '"dev.codex.schubert.nk.api.security.PasswordHasherTest", 3' in run.HELPER.read_text()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15442-current1810-auth-context-codec-registry-v1/manifest.json','e94941427a78ea47d0b82eabbcffd19400909efb16b939c3216a30cc6aed897c')
    name='dev/codex/schubert/nk/api/security/PasswordHasher';main='src/schubert-nk-api/src/main/java/'+name+'.java'
    assert name not in current['fullSourceUnits'] and 'dev.codex.schubert.nk.api.security.PasswordHasherTest' not in current['suiteNames']
    assert normal['begin']['inputHashes'][main]==run.host.sha(run.host.ROOT/main)==run.host.sha(COMPILE/'snapshot'/main)=='af26da6781015b67cf36a6e35497c334dd1eadf05e00da38f1e2c43460d91baf'
    path=str(TESTS['PasswordHasherTest'].relative_to(run.host.ROOT))
    assert normal['begin']['inputHashes'][path]==run.host.sha(COMPILE/'snapshot'/path)==PINS['PasswordHasherTest']
    assert run.host.sha(run.HELPER)=='c2e37cc5e68468ace257a0f738528ffdb3c0f50a30e3115c52d1d811b781ba3d'
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}=={name}
    crypto=[p for p,h in normal['begin']['inputHashes'].items() if p==main];assert crypto==[main]
    run.step=environmental_step;run.main()
