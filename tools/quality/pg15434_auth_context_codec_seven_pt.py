"""Whole original AuthContextCodec seven; only public synthetic keys and own JCA/thread state."""
import hashlib
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'AuthContextCodecTest':7}
SESSION='PG15434-AUTH-CONTEXT-CODEC-CURRENT-WHOLE7'
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={'AuthContextCodecTest':'10b4b75bc16afe0038e05e7c14abd516e1335f51929a25a674319d7afcdda26d'}
FIXTURES={}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15434-auth-context-codec-seven-pt-v1'
    run.OUT=run.host.BASE/'PG15434-auth-context-codec-seven-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/AuthContextCodecCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['AuthContextCodecTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    text=TESTS['AuthContextCodecTest'].read_text();assert run.host.sha(TESTS['AuthContextCodecTest'])==PINS['AuthContextCodecTest']
    assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==7
    assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv('])
    assert all(v in text for v in ['independentEnvelope(', 'independentAad(', 'Cipher.getInstance("AES/GCM/NoPadding")', 'new byte[32]', 'Arrays.fill(bytes, (byte) 42)', 'assertNull(failure.getCause())'])
    assert 'finally {' in text and 'assertArrayEquals(original, Security.getProviders());' in text
    assert '"dev.codex.schubert.nk.api.security.AuthContextCodecTest", 7' in run.HELPER.read_text()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15424-current1803-context-hash-registry-v1/manifest.json','8b2967c3e42ea8126d3b4c13805f9d6433e12ec8584349d2802379b699541f9f')
    mains={"AuthContextCodec":"6cbdc8b0bc006e036ac3e127685d06c19bbb3c1e05d854cb52c8620d6a6065d6","AuthContextIdentity":"b9dbed4233756c481cdb747d96f6de8843e9d910a4c18f51c30454d16130d7dd","EncryptedAuthContext":"d503847e6b1b1a3853033cbe82eb53678b529d616f36d1dfc0a354b3635954b7","AuthContextCryptoException":"a54b29289de7d08e01d6cbc814e9a815ae2162de559e02eebdb6e677a850066f"}
    for short,pin in mains.items():
        name='dev/codex/schubert/nk/api/security/'+short;main='src/schubert-nk-api/src/main/java/'+name+'.java'
        assert name not in current['fullSourceUnits']
        assert normal['begin']['inputHashes'][main]==run.host.sha(run.host.ROOT/main)==run.host.sha(COMPILE/'snapshot'/main)==pin
    assert 'dev.codex.schubert.nk.api.security.AuthContextCodecTest' not in current['suiteNames']
    path=str(TESTS['AuthContextCodecTest'].relative_to(run.host.ROOT))
    assert normal['begin']['inputHashes'][path]==run.host.sha(COMPILE/'snapshot'/path)==PINS['AuthContextCodecTest']
    assert run.host.sha(run.HELPER)=='f6491da4aaefc7b374bcda53deaa2dc2076d400efe59c8e155806eb556058537'
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for short in mains:
            name='dev/codex/schubert/nk/api/security/'+short
            expected={name,name+'$Reason'} if short=='AuthContextCryptoException' else {name}
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}==expected
    run.step=environmental_step;run.main()
