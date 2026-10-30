"""Current pure login policy whole15; synthetic values/state only, no credentials or actual authentication."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'LoginUsernameTest':3,'PasswordPolicyTest':3,'LoginAttemptStateTest':5,'LoginAttemptSequenceTest':4}
SESSION='PG15368-CURRENT-PURE-LOGIN15'
ROOT=data.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={"LoginUsernameTest":"1fdb742c0aab4c1be6ce90ca68e2f357c7030a7d5a916df34f9f91a61bfccf00","PasswordPolicyTest":"fe466645fdf4739e44df74b3197c1b55631a5b2b0c423d526f005468ac87fc55","LoginAttemptStateTest":"8de7da1fea134d4f1973ac003287dccee971dad697859f6014f0a32743930391","LoginAttemptSequenceTest":"92d8a79ea0e8089bea9822fd77560998184f0e032bf7f94c5317e43454d3975f"}
MAIN_PINS={"LoginUsername":"970b0b15993f72f0881cdf64b00839cb1fdf4f601a6c4b0827e2adc0bb4e0359","PasswordPolicy":"6d8ffe5b35fc04f4056999d5a4a4a73ce6c3103a62b4b2cd87fbcfbeb1c8e608","LoginAttemptState":"393f52726e83c3ea52fe34c7385c0da413d49306a476894255602fe82880c352","LoginAttemptKind":"493c8b03e7791a044be87f4fadeb1c7c7c95588aba1174cb38baa0b5a3b56f7b"}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15368-pure-login-policy-fifteen-pt-v1';run.OUT=data.BASE/'PG15368-pure-login-policy-fifteen-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalPureLoginPolicyJunitLauncher.java';run.NEW_TEST=TESTS['LoginUsernameTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='LoginUsernameTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG15352-current1777-inputs-outbox-registry-v1/manifest.json','e160176d7283e59615bfa7690c3d8856a7dd79babd89012a9e974df2face2c67')
    assert not {'dev.codex.schubert.nk.api.security.'+name for name in COUNTS}&set(registry['suiteNames'])
    prefix='dev/codex/schubert/nk/api/security/'
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for name,pin in MAIN_PINS.items():
            target=prefix+name;main='src/schubert-nk-api/src/main/java/'+target+'.java'
            assert target not in registry['fullSourceUnits']
            assert normal['begin']['inputHashes'][main]==run.host.sha(data.ROOT/main)==run.host.sha(COMPILE/'snapshot'/main)==pin
            assert {p[:-6] for p in jar.namelist() if p==target+'.class' or p.startswith(target+'$') and p.endswith('.class')}=={target}
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert len(re.findall(r'@Test\b',text))==COUNTS[name]
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','FileSystems.','getFileStore(','Linux','getenv(','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','HttpClient','Clock.system','TemporaryInfrastructureException','getSuppressed(','@BeforeAll','@BeforeEach','@TempDir','getConnection(','DataSource','PreparedStatement','.production('])
        assert not re.search(r'\.\s*(?:gc|setVerbose|dumpHeap)\s*\(',text)
        assert not re.search(r'(?<![A-Za-z0-9_])Files\s*\.',text)
        assert '"dev.codex.schubert.nk.api.security.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
        assert 'new ApiProcessMain(' not in text and '.run(' not in text and '.main(' not in text
    run.step=environmental_step;run.main()
