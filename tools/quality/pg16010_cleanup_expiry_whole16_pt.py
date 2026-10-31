"""Original three public-codec suites in one JVM; no owner/permission/I/O is acquired."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE = run.host.W / 'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA = '1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME = 'dev/codex/schubert/nk/batch/platform/CleanupWorkerRequest'
ROWS = [dict(module='batch', name=NAME, sha256='996bede981606bfde5c711d030a4cb9f32de06e05fcbad8c064990966060e24f', suffixes=['', '$Expiry', '$Expiry$PriorExpiry'])]
MAIN_UNITS = {r['name']: r for r in ROWS}
CLOSURES = {NAME: [NAME + s for s in ROWS[0]['suffixes']]}
METADATA = set()
UNEXECUTED = set()
EXECUTED = set(CLOSURES[NAME])
TEST_ROOT = data.ROOT / 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform'
TESTS = {name: TEST_ROOT / (name + '.java') for name in ('ExpiryWorkerRequestTest', 'ExpiryRequestBoundaryTest', 'CleanupWorkerRequestTest')}
TEST_HASHES = {'ExpiryWorkerRequestTest': 'ecc28374a929bf41206d1c25e473d719c726f90ade712c9e56d619c553a36847', 'ExpiryRequestBoundaryTest': 'cb037659b32f272f31e60f58e9822f1dd5d41a8080ca633207f220d72dce528b', 'CleanupWorkerRequestTest': 'fd76996c84c1a75a7eb68ac5fb24e758e58c5fcfb69a1679cb0aa46efc6e5493'}
COUNTS = dict(ExpiryWorkerRequestTest=7, ExpiryRequestBoundaryTest=2, CleanupWorkerRequestTest=7)
FIXTURES = {}
SESSION = 'PG16010-CLEANUP-EXPIRY-WHOLE16'
REPORTER = data.ROOT / 'tools/quality/architecture/SharedSelectedJunitReporterV1.java'


def source_path(row):
    return 'src/schubert-nk-' + row['module'] + '/src/main/java/' + row['name'] + '.java'


if __name__ == '__main__':
    run.SOURCE, run.COMPILE, run.COMPILE_SHA = SOURCE, COMPILE, COMPILE_SHA
    run.SLOT = run.host.W / 'pg16010-cleanup-expiry-whole16-pt-v1'
    run.OUT = data.BASE / 'PG16010-cleanup-expiry-whole16-pt-v1'
    run.HELPER = data.ROOT / 'tools/quality/architecture/CleanupExpiryWholeSixteenJunitLauncher.java'
    run.NEW_TEST, run.TEST_ROOT = TESTS['ExpiryWorkerRequestTest'], TEST_ROOT
    run.TEST_SOURCE_OVERRIDES, run.FIXTURES, run.COUNTS = {}, {}, COUNTS
    run.EXTRA_TEST_SOURCES, run.SESSION_ID = (REPORTER,), SESSION
    assert data.sha(REPORTER.read_bytes()) == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert data.sha(run.HELPER.read_bytes()) == '7e1ac7af75050c0bdba40eed937ade678c222fb33e314f88b5fdadf6882ab5dd'
    normal = data.read_checked(COMPILE / 'manifest.safe.json', COMPILE_SHA)
    current = data.read_checked(data.BASE / 'PG15994-current2094-reference-value-registry-v1/manifest.json', '7eaf3d75b2eadf3ab0d38f642333aefff3bb56fd81acd5b31d16d55d02d58a17')
    assert normal['source'] == SOURCE and NAME not in current['fullSourceUnits']
    for name, file in TESTS.items():
        relative = str(file.relative_to(data.ROOT))
        text = file.read_text()
        assert data.sha(file.read_bytes()) == normal['begin']['inputHashes'][relative] == data.sha((COMPILE / 'snapshot' / relative).read_bytes()) == TEST_HASHES[name]
        assert text.count('@Test') == len(re.findall(r'(?m)^  void [A-Za-z0-9_]+\(', text)) == COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.platform.' + name not in current['suiteNames']
        assert not any(s in text for s in ('@BeforeAll', '@BeforeEach', '@TempDir', 'ProcessBuilder', 'DriverManager', 'getConnection(', 'System.getenv(', 'LinuxDirectoryCalls', 'TemporaryInfrastructureException', 'WebStartupException', 'FingerprintKeyRing', 'ResponseSnapshotCodec', 'Class.forName(', 'HttpClient'))
    path = source_path(ROWS[0])
    assert normal['begin']['inputHashes'][path] == data.sha((data.ROOT / path).read_bytes()) == ROWS[0]['sha256']
    with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
        assert {p[:-6] for p in jar.namelist() if p == NAME + '.class' or p.startswith(NAME + '$') and p.endswith('.class')} == EXECUTED
    run.step = environmental_step
    run.main()
