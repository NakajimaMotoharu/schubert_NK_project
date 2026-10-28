"""Existing whole Query5/Evidence7 through injected fake Process and memory JSON only."""
import re
import scoped_prometheus_host as run

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
COMPILE = run.host.W/'pg13596-lgs-remaining-two-branches-v1'
COMPILE_SHA = '1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12'
COUNTS = {'BrokerJournalQueryTest':5,'BrokerJournalEvidenceTest':7}
SESSION = 'PG13692-BROKER-JOURNAL-CURRENT-WHOLE12'
BASE = run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform'
TESTS = {name:BASE/(name+'.java') for name in COUNTS}
PINS = {'BrokerJournalQueryTest':'935ce8afed0d16ad9b8617c647ceb921eb0d28edc9438cf7e2ac5f58eaa9f745','BrokerJournalEvidenceTest':'73ec7a8bca1a6540dec83520b7072b56fd7c988e55d9d1a86afb67b0a9125a02'}
OWNERS = {'BrokerJournalQueryTest':'WBS-P004-04','BrokerJournalEvidenceTest':'WBS-P017-10'}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13692-broker-journal-whole-twelve-pt-v1'
    run.OUT = run.host.BASE/'PG13692-broker-journal-whole-twelve-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/BrokerJournalCurrentTwelveJunitLauncher.java'
    run.NEW_TEST = TESTS['BrokerJournalQueryTest']
    run.TEST_SOURCE_OVERRIDES = {'BrokerJournalEvidenceTest':TESTS['BrokerJournalEvidenceTest']}
    run.EXTRA_TEST_SOURCES = ()
    run.FIXTURES = {}
    run.COUNTS = COUNTS
    run.SESSION_ID = SESSION
    for name,path in TESTS.items():
        text = path.read_text()
        assert run.host.sha(path) == PINS[name]
        assert text.count('@Test') == COUNTS[name] and len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == COUNTS[name]
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','@TempDir','DriverManager','getConnection(', 'java.nio.file.','ProcessBuilder','Runtime.getRuntime','setAccessible','LinuxDirectoryCalls','LinuxInodeSecurity','getDeclared','TemporaryInfrastructureException','WebStartupException','NativeReader.forTarget(','new InspectorUnitProbe.NativeReader()'])
    query = TESTS['BrokerJournalQueryTest'].read_text()
    evidence = TESTS['BrokerJournalEvidenceTest'].read_text()
    assert 'class Child extends Process' in query and 'new InspectorUnitProbe.NativeReader(\n        command ->' in query
    assert '.inspect(' not in evidence and '.inspectStopped(' not in evidence and '@org.junit.jupiter.api.parallel.Isolated' in evidence
    helper = run.HELPER.read_text()
    selected = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',helper,re.S)
    assert len(selected) == 1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0]) == ['dev.codex.schubert.nk.batch.platform.'+name for name in COUNTS]
    assert re.findall(r'(?:getTests(?:Found|Started|Succeeded)Count\(\)|results.size\(\))\s*==\s*(\d+)',helper) == ['12']*4
    assert 'Existing whole twelve memory-only broker journal tests' in helper
    assert run.SLOT.name.upper() == run.OUT.name.upper()
    run.main()
