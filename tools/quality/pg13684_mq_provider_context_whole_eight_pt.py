"""Two existing whole Login probe/provider tests, only injected memory wire and Spring objects."""
import re
import scoped_prometheus_host as run

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
COMPILE = run.host.W/'pg13596-lgs-remaining-two-branches-v1'
COMPILE_SHA = '1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12'
COUNTS = {'MqLoginContextProbeTest':3,'MqAuthenticationProviderTest':5}
SESSION = 'PG13684-MQ-PROVIDER-CONTEXT-CURRENT-WHOLE8'
BASE = run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/security'
TESTS = {name:BASE/(name+'.java') for name in COUNTS}
PINS = {'MqLoginContextProbeTest':'94bd2c4d5bcc12870074f5907c03a7e21ef7b5a213cad94170a20e480d20434b','MqAuthenticationProviderTest':'1102d1cdb41889da6e3476227970c3d01e2523be8603e6a9db83ad1cdc7adcad'}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13684-mq-provider-context-whole-eight-pt-v1'
    run.OUT = run.host.BASE/'PG13684-mq-provider-context-whole-eight-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/MqProviderCurrentEightJunitLauncher.java'
    run.NEW_TEST = TESTS['MqLoginContextProbeTest']
    run.TEST_SOURCE_OVERRIDES = {'MqAuthenticationProviderTest':TESTS['MqAuthenticationProviderTest']}
    run.EXTRA_TEST_SOURCES = (BASE/'MqLoginClientTest.java',)
    run.FIXTURES = {}
    run.COUNTS = COUNTS
    run.SESSION_ID = SESSION
    for name,path in TESTS.items():
        text = path.read_text()
        assert run.host.sha(path) == PINS[name]
        assert text.count('@Test') == COUNTS[name] and len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == COUNTS[name]
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','@TempDir','DriverManager','getConnection(', 'java.nio.file.','ProcessBuilder','Runtime.getRuntime','setAccessible','Artemis','LinuxDirectoryCalls','LinuxInodeSecurity','getDeclared','TemporaryInfrastructureException','WebStartupException'])
    assert run.host.sha(BASE/'MqLoginClientTest.java') == '6b4e9b5d633652ae0e6aa7e2e141b5ea88bb333906f04d7d06728f0c9f649598'
    helper = run.HELPER.read_text()
    selected = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',helper,re.S)
    assert len(selected) == 1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0]) == ['dev.codex.schubert.nk.web.security.'+name for name in COUNTS]
    assert re.findall(r'(?:getTests(?:Found|Started|Succeeded)Count\(\)|results.size\(\))\s*==\s*(\d+)',helper) == ['8']*4
    assert 'Existing whole eight memory-only Login probe/provider tests' in helper
    assert run.SLOT.name.upper() == run.OUT.name.upper()
    run.main()
