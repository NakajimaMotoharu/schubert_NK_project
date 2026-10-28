"""Existing whole six Login exchanges through only injected memory senders, never a broker."""
import re
import scoped_prometheus_host as run

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
COMPILE = run.host.W/'pg13596-lgs-remaining-two-branches-v1'
COMPILE_SHA = '1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12'
COUNTS = {'MqLoginClientTest': 6}
SESSION = 'PG13676-MQ-LOGIN-CURRENT-WHOLE6'
TESTS = {'MqLoginClientTest':run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/security/MqLoginClientTest.java'}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13676-mq-login-whole-six-pt-v1'
    run.OUT = run.host.BASE/'PG13676-mq-login-whole-six-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/MqLoginCurrentSixJunitLauncher.java'
    run.NEW_TEST = TESTS['MqLoginClientTest']
    run.TEST_SOURCE_OVERRIDES = {}
    run.EXTRA_TEST_SOURCES = ()
    run.FIXTURES = {}
    run.COUNTS = COUNTS
    run.SESSION_ID = SESSION
    text = run.NEW_TEST.read_text()
    assert run.host.sha(run.NEW_TEST) == '6b4e9b5d633652ae0e6aa7e2e141b5ea88bb333906f04d7d06728f0c9f649598'
    assert text.count('@Test') == 6 and len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == 6
    assert not any(value in text for value in ['@BeforeAll','@BeforeEach','@TempDir','DriverManager','getConnection(', 'java.nio.file.','ProcessBuilder','Runtime.getRuntime','setAccessible','Artemis','LinuxDirectoryCalls','LinuxInodeSecurity','getDeclared','TemporaryInfrastructureException','WebStartupException'])
    assert 'new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12)' in text
    assert 'CountDownLatch' in text and 'result.get(10, TimeUnit.SECONDS)' in text
    selected = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected) == 1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0]) == ['dev.codex.schubert.nk.web.security.MqLoginClientTest']
    assert run.SLOT.name.upper() == run.OUT.name.upper()
    assert re.findall(r'(?:getTests(?:Found|Started|Succeeded)Count\(\)|results.size\(\))\s*==\s*(\d+)',run.HELPER.read_text()) == ['6']*4
    assert 'Existing whole six memory-only MqLoginClientTest' in run.HELPER.read_text()
    run.main()
