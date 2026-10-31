"""Original JDBC proxy3 plus required prior24: one current-source joint27, no real backend."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE = run.host.W / 'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA = '1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
ROOT = 'dev/codex/schubert/nk/batch/repository/'
ROWS = [dict(module='batch', name=ROOT + 'ExpiryAuditRepository', sha256='8d04ab28261de2e41ccc24790d732922f02c823aad5c0f374d6040e99cbe9a7e', suffixes=['', '$JdbcAcquire', '$JdbcRead', '$JdbcRelease', '$Prior', '$Snapshot', '$Stage']), dict(module='batch', name=ROOT + 'BatchRepositoryException', sha256='134bcdaecf9f02adc74d5cb728782c41f19497b0c0c37ee2cd4a70b0155179b6', suffixes=[''])]
ROWS += [dict(module='batch', name=ROOT + 'RunReferenceRepository', sha256='f9ef20bb9fcdd35983e5c18bbd4cff7b52f80553828af2dfa399954ee9bf55e0', suffixes=['']), dict(module='batch', name=ROOT + 'JdbcResourceFailures', sha256='f4cff9bb43cacfde5be699fd61d4e25526523d5ef5e478aa88dcbb8bdde6928a', suffixes=['']), dict(module='batch', name=ROOT + 'RunReferences', sha256='dacc345b826e86682036df2e94f8e5300cb75435f4cdcd1de6ece4165eac5884', suffixes=[''])]
MAIN_UNITS = {r['name']: r for r in ROWS}
CLOSURES = {r['name']: [r['name'] + s for s in r['suffixes']] for r in ROWS}
METADATA = {ROOT + 'ExpiryAuditRepository' + s for s in ('$JdbcAcquire', '$JdbcRead', '$JdbcRelease')}
EXECUTED = {ROOT + 'ExpiryAuditRepository', ROOT + 'ExpiryAuditRepository$Snapshot', ROOT + 'BatchRepositoryException'}
EXECUTED |= {ROOT + 'RunReferenceRepository', ROOT + 'JdbcResourceFailures', ROOT + 'RunReferences'}
UNEXECUTED = {ROOT + 'ExpiryAuditRepository$Stage', ROOT + 'ExpiryAuditRepository$Prior'}
TEST = run.host.ROOT / 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/ExpirySuccessfulScopeTest.java'
TEST_SHA = 'b863f5fbdb657ab110e7c7a63a550b2bae770281b638f5a873c2e07a441c1429'
NEW_TEST = TEST.parent / 'ExpiryAuditResourceFailureTest.java'
NEW_TEST_SHA = 'b5f68a2bbf6a1af7a28bf6ee1f884087a88b4cc6fefa530172bac9ae62bacd48'
MATRIX = TEST.parent / 'JdbcResourceCases.java'
MATRIX_SHA = '641d71157a20f609beb2b8639e8098497c6c714d5f2122540cd5264dfb717c97'
TESTS = {'ExpirySuccessfulScopeTest': TEST, 'ExpiryAuditResourceFailureTest': NEW_TEST}
COUNTS = {'ExpirySuccessfulScopeTest': 24, 'ExpiryAuditResourceFailureTest': 3}
FIXTURES = {}
SESSION = 'PG15972-EXPIRY-JDBC-JOINT27'
REPORTER = run.host.ROOT / 'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

def source_path(row):
    return 'src/schubert-nk-' + row['module'] + '/src/main/java/' + row['name'] + '.java'

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg15972-expiry-jdbc-joint27-pt-v1'
    run.OUT = run.host.BASE / 'PG15972-expiry-jdbc-joint27-pt-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/ExpiryJdbcJointTwentySevenJunitLauncher.java'
    run.NEW_TEST = TEST
    run.TEST_ROOT = TEST.parent
    run.TEST_SOURCE_OVERRIDES = {}
    run.EXTRA_TEST_SOURCES = (REPORTER, NEW_TEST, MATRIX)
    run.FIXTURES = FIXTURES
    run.COUNTS = COUNTS
    run.SESSION_ID = SESSION
    reporter = data.read_checked(data.BASE / 'PG13728-shared-reporter-selftest-post-v1/manifest.json', '32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert reporter['actualExit'] == reporter['productTestsExecuted'] == 0 and reporter['toolChecksIndependentlyConfirmed'] == 12
    assert run.host.sha(REPORTER) == reporter['toolSourceHashes'][str(REPORTER)] == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER) == 'b66a279ea860eb5523919f95f768ae72d853a264cc680efd569aab21f76f9ea6'
    normal = data.read_checked(COMPILE / 'manifest.safe.json', COMPILE_SHA)
    current = data.read_checked(data.BASE / 'PG15962-current2088-expiry-scope-registry-v1/manifest.json', 'fe4e0cd55f6677b6797dea4644781ec91ee99a3c2c9597ed8712917f55c7393f')
    relative = str(TEST.relative_to(data.ROOT))
    text = TEST.read_text()
    assert run.host.sha(TEST) == normal['begin']['inputHashes'][relative] == run.host.sha(COMPILE / 'snapshot' / relative) == TEST_SHA
    methods = re.findall(r'(?m)^  void (exp4956[0-9]{3}[A-Za-z0-9_]+)\(', text)
    assert text.count('@Test') == len(methods) == 24 and {m[7:10] for m in methods} == {str(i).zfill(3) for i in range(1, 25)}
    assert 'dev.codex.schubert.nk.batch.repository.ExpirySuccessfulScopeTest' in current['suiteNames']
    assert 'dev.codex.schubert.nk.batch.repository.ExpiryAuditResourceFailureTest' not in current['suiteNames']
    for path, pin in [(NEW_TEST, NEW_TEST_SHA), (MATRIX, MATRIX_SHA)]:
        rel = str(path.relative_to(data.ROOT))
        assert run.host.sha(path) == normal['begin']['inputHashes'][rel] == run.host.sha(COMPILE / 'snapshot' / rel) == pin
        assert not any(t in path.read_text() for t in ['@BeforeAll', '@TempDir', 'BatchDatabaseFixture', 'DriverManager', 'LinuxDirectoryCalls', 'TemporaryInfrastructureException', 'WebStartupException', 'FingerprintKeyRing', 'ResponseSnapshotCodec'])
    assert NEW_TEST.read_text().count('@Test') == 3 and 'assertEquals(68, samples.size())' in MATRIX.read_text()
    assert not any(v in text for v in ['@BeforeAll', '@BeforeEach', '@TempDir', 'ProcessBuilder', 'DriverManager', 'System.getenv(', 'getConnection(', 'TemporaryInfrastructureException', 'WebStartupException', 'Class.forName(', 'HttpClient', 'LinuxDirectoryCalls', 'FingerprintKeyRing', 'ResponseSnapshotCodec', 'new ExpiryAuditRepository('])
    assert all(v in text for v in ['new ExpiryAuditRepository.Snapshot(', 'ExpiryAuditRepository.verifySuccessfulAudit(', 'ExpiryAuditRepository.usingJdbc(', 'try (JdbcClose owned = release::close)'])
    assert len(METADATA) == 3 and len(EXECUTED) == 6 and len(UNEXECUTED) == 2
    for row in ROWS:
        path = source_path(row)
        name = row['name']
        assert (name in current['fullSourceUnits']) == (name in {ROOT + 'ExpiryAuditRepository', ROOT + 'BatchRepositoryException'})
        assert normal['begin']['inputHashes'][path] == run.host.sha(data.ROOT / path) == run.host.sha(COMPILE / 'snapshot' / path) == row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:
            assert {p[:-6] for p in jar.namelist() if p == name + '.class' or p.startswith(name + '$') and p.endswith('.class')} == set(CLOSURES[name])
    run.step = environmental_step
    run.main()
