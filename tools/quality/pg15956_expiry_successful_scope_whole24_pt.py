"""Original 24 success-predicate/TWR contracts, no actual JDBC/owner/native operations."""
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
MAIN_UNITS = {r['name']: r for r in ROWS}
CLOSURES = {r['name']: [r['name'] + s for s in r['suffixes']] for r in ROWS}
METADATA = {ROOT + 'ExpiryAuditRepository' + s for s in ('$JdbcAcquire', '$JdbcRead', '$JdbcRelease')}
EXECUTED = {ROOT + 'ExpiryAuditRepository', ROOT + 'ExpiryAuditRepository$Snapshot', ROOT + 'BatchRepositoryException'}
UNEXECUTED = {ROOT + 'ExpiryAuditRepository$Stage', ROOT + 'ExpiryAuditRepository$Prior'}
TEST = run.host.ROOT / 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/ExpirySuccessfulScopeTest.java'
TEST_SHA = 'b863f5fbdb657ab110e7c7a63a550b2bae770281b638f5a873c2e07a441c1429'
TESTS = {'ExpirySuccessfulScopeTest': TEST}
COUNTS = {'ExpirySuccessfulScopeTest': 24}
FIXTURES = {}
SESSION = 'PG15956-EXPIRY-SUCCESSFUL-SCOPE-WHOLE24'
REPORTER = run.host.ROOT / 'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

def source_path(row):
    return 'src/schubert-nk-' + row['module'] + '/src/main/java/' + row['name'] + '.java'

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg15956-expiry-successful-scope-whole24-pt-v1'
    run.OUT = run.host.BASE / 'PG15956-expiry-successful-scope-whole24-pt-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/ExpirySuccessfulScopeTwentyFourJunitLauncher.java'
    run.NEW_TEST = TEST
    run.TEST_ROOT = TEST.parent
    run.TEST_SOURCE_OVERRIDES = {}
    run.EXTRA_TEST_SOURCES = (REPORTER,)
    run.FIXTURES = FIXTURES
    run.COUNTS = COUNTS
    run.SESSION_ID = SESSION
    reporter = data.read_checked(data.BASE / 'PG13728-shared-reporter-selftest-post-v1/manifest.json', '32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert reporter['actualExit'] == reporter['productTestsExecuted'] == 0 and reporter['toolChecksIndependentlyConfirmed'] == 12
    assert run.host.sha(REPORTER) == reporter['toolSourceHashes'][str(REPORTER)] == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER) == 'c4722416f641db65ec193098d37781360703160b44b3bc4b92af79d329a7a34b'
    normal = data.read_checked(COMPILE / 'manifest.safe.json', COMPILE_SHA)
    current = data.read_checked(data.BASE / 'PG15908-current2064-observation-values-registry-v1/manifest.json', 'a2df9a72bc19eca2b725aaff0d5bee234c8da7cdb50e3ec3ce9cf0d5823b3c53')
    relative = str(TEST.relative_to(data.ROOT))
    text = TEST.read_text()
    assert run.host.sha(TEST) == normal['begin']['inputHashes'][relative] == run.host.sha(COMPILE / 'snapshot' / relative) == TEST_SHA
    methods = re.findall(r'(?m)^  void (exp4956[0-9]{3}[A-Za-z0-9_]+)\(', text)
    assert text.count('@Test') == len(methods) == 24 and {m[7:10] for m in methods} == {str(i).zfill(3) for i in range(1, 25)}
    assert 'dev.codex.schubert.nk.batch.repository.ExpirySuccessfulScopeTest' not in current['suiteNames']
    assert not any(v in text for v in ['@BeforeAll', '@BeforeEach', '@TempDir', 'ProcessBuilder', 'DriverManager', 'System.getenv(', 'getConnection(', 'TemporaryInfrastructureException', 'WebStartupException', 'Class.forName(', 'HttpClient', 'LinuxDirectoryCalls', 'FingerprintKeyRing', 'ResponseSnapshotCodec', 'new ExpiryAuditRepository('])
    assert all(v in text for v in ['new ExpiryAuditRepository.Snapshot(', 'ExpiryAuditRepository.verifySuccessfulAudit(', 'ExpiryAuditRepository.usingJdbc(', 'try (JdbcClose owned = release::close)'])
    assert len(METADATA) == 3 and len(EXECUTED) == 3 and len(UNEXECUTED) == 2
    for row in ROWS:
        path = source_path(row)
        name = row['name']
        assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][path] == run.host.sha(data.ROOT / path) == run.host.sha(COMPILE / 'snapshot' / path) == row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:
            assert {p[:-6] for p in jar.namelist() if p == name + '.class' or p.startswith(name + '$') and p.endswith('.class')} == set(CLOSURES[name])
    run.step = environmental_step
    run.main()
