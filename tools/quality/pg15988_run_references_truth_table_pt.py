"""New independent 16-row primitive value fixture; no held Test adapted or business operation."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE = run.host.W / 'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA = '1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME = 'dev/codex/schubert/nk/batch/repository/RunReferences'
ROWS = [dict(module='batch', name=NAME, sha256='dacc345b826e86682036df2e94f8e5300cb75435f4cdcd1de6ece4165eac5884', suffixes=[''])]
MAIN_UNITS = {NAME: ROWS[0]}
CLOSURES = {NAME: [NAME]}
METADATA = set()
EXECUTED = {NAME}
UNEXECUTED = set()
ROOT = data.ROOT / 'tools/quality/architecture'
TEST = ROOT / 'RunReferencesTruthTableTest.java'
TEST_SHA = '57eb6860f5767a5e8c2967899f4cce13437e5c1a05fb19f4cbc313adcd628b57'
TESTS = {'RunReferencesTruthTableTest': TEST}
COUNTS = {'RunReferencesTruthTableTest': 3}
FIXTURES = {}
SESSION = 'PG15988-RUN-REFERENCES-LITERAL16-THREE'
REPORTER = ROOT / 'SharedSelectedJunitReporterV1.java'

def source_path(row):
    return 'src/schubert-nk-' + row['module'] + '/src/main/java/' + row['name'] + '.java'

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg15988-run-references-truth-table-three-pt-v1'
    run.OUT = data.BASE / 'PG15988-run-references-truth-table-three-pt-v1'
    run.HELPER = ROOT / 'RunReferencesTruthTableJunitLauncher.java'
    run.NEW_TEST = TEST
    run.TEST_ROOT = ROOT
    run.TEST_SOURCE_OVERRIDES = {}
    run.EXTRA_TEST_SOURCES = (REPORTER,)
    run.FIXTURES = FIXTURES
    run.COUNTS = COUNTS
    run.SESSION_ID = SESSION
    proof = data.read_checked(data.BASE / 'PG13728-shared-reporter-selftest-post-v1/manifest.json', '32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit'] == proof['productTestsExecuted'] == 0 and proof['toolChecksIndependentlyConfirmed'] == 12
    assert run.host.sha(REPORTER) == proof['toolSourceHashes'][str(REPORTER)] == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(TEST) == TEST_SHA and run.host.sha(run.HELPER) == '18e823db9d3a1ceea2c87d32a667dbaa0a0e43ac6064e0b51a0e37004381258d'
    text = TEST.read_text()
    assert text.count('@Test') == len(re.findall(r'@Test\s+void\s+flags[0-9]{3}[A-Za-z0-9_]+\s*\(', text)) == 3
    assert len(re.findall(r'new Vector\(', text)) == 16
    assert not any(term in text for term in ['ProcessBuilder', 'DriverManager', 'Files.', 'Linux', 'getenv(', 'java.sql', 'ManagementFactory', 'TemporaryInfrastructureException', 'WebStartupException', 'FingerprintKeyRing', 'ResponseSnapshotCodec', 'RunReferenceRepository', 'ExpiryAuditRepository', 'Cleanup', '@TempDir'])
    normal = data.read_checked(COMPILE / 'manifest.safe.json', COMPILE_SHA)
    path = source_path(ROWS[0])
    assert normal['source'] == SOURCE and normal['begin']['inputHashes'][path] == run.host.sha(data.ROOT / path) == run.host.sha(COMPILE / 'snapshot' / path) == ROWS[0]['sha256']
    previous = data.read_checked(data.BASE / 'PG15978-current2091-expiry-joint-registry-v1/manifest.json', '6cc07d3fb25ccebaf5a406c85f401b49f83d127cb0811283ee0cd19d9de02862')
    assert NAME in previous['fullSourceUnits'] and previous['fullSourceUnits'][NAME]['four100'] is False and 'dev.codex.schubert.nk.batch.repository.RunReferencesTruthTableTest' not in previous['suiteNames']
    run.step = environmental_step
    run.main()
