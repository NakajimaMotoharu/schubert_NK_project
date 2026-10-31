"""Original failure-profile two public-codec suites in one JVM; no owner/permission/I/O is acquired."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE = run.host.W / 'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA = '1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME = 'dev/codex/schubert/nk/batch/platform/CleanupFailedBackupRequest'
PROFILE = 'dev/codex/schubert/nk/batch/platform/CleanupProfile'
ROWS = [dict(module='batch', name=NAME, sha256='37079ddb280f2d105ee147969e3f915e2a8f5adf61aba51325ba25775db68ec0', suffixes=['', '$Row']), dict(module='batch', name=PROFILE, sha256='9fbbeb80a1be4f6a2183376d4b1f979020e48e02baee163a11406656c9c5e2b9', suffixes=[''])]
MAIN_UNITS = {r['name']: r for r in ROWS}
CLOSURES = {r['name']: [r['name'] + suffix for suffix in r['suffixes']] for r in ROWS}
METADATA = set()
UNEXECUTED = set()
EXECUTED = {name for group in CLOSURES.values() for name in group}
TEST_ROOT = data.ROOT / 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform'
TESTS = {name: TEST_ROOT / (name + '.java') for name in ('CleanupFailedBackupRequestTest', 'FailedProfileBoundaryTest')}
TEST_HASHES = {'CleanupFailedBackupRequestTest': 'cbae23933dc9cc7e2ff72edb59a42b259ffb35c4f13adbf9a28ee7efdc610f49', 'FailedProfileBoundaryTest': '17bf7c33e7d6ac9eee8a9892469c07b3b43d47de0e91ec81dcb9eb4311693a64'}
COUNTS = dict(CleanupFailedBackupRequestTest=4, FailedProfileBoundaryTest=2)
FIXTURES = {}
SESSION = 'PG16026-FAILED-PROFILE-WHOLE6'
REPORTER = data.ROOT / 'tools/quality/architecture/SharedSelectedJunitReporterV1.java'


def source_path(row):
    return 'src/schubert-nk-' + row['module'] + '/src/main/java/' + row['name'] + '.java'


if __name__ == '__main__':
    run.SOURCE, run.COMPILE, run.COMPILE_SHA = SOURCE, COMPILE, COMPILE_SHA
    run.SLOT = run.host.W / 'pg16026-failed-profile-whole6-pt-v1'
    run.OUT = data.BASE / 'PG16026-failed-profile-whole6-pt-v1'
    run.HELPER = data.ROOT / 'tools/quality/architecture/FailedProfileWholeSixJunitLauncher.java'
    run.NEW_TEST, run.TEST_ROOT = TESTS['CleanupFailedBackupRequestTest'], TEST_ROOT
    run.TEST_SOURCE_OVERRIDES, run.FIXTURES, run.COUNTS = {}, {}, COUNTS
    run.EXTRA_TEST_SOURCES, run.SESSION_ID = (REPORTER,), SESSION
    assert data.sha(REPORTER.read_bytes()) == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert data.sha(run.HELPER.read_bytes()) == 'd52d2a73d7cfb258831578be25b16390ead877343f4196b2a7bd16c08cbc6c2f'
    normal = data.read_checked(COMPILE / 'manifest.safe.json', COMPILE_SHA)
    current = data.read_checked(data.BASE / 'PG16016-current2110-cleanup-expiry-registry-v1/manifest.json', '08f7203d2b16473ec80ff3e17cd80d371890bfdbb14b0e4f8ff7fcce52a4ff25')
    assert normal['source'] == SOURCE and all(name not in current['fullSourceUnits'] for name in MAIN_UNITS)
    for name, file in TESTS.items():
        relative = str(file.relative_to(data.ROOT))
        text = file.read_text()
        assert data.sha(file.read_bytes()) == normal['begin']['inputHashes'][relative] == data.sha((COMPILE / 'snapshot' / relative).read_bytes()) == TEST_HASHES[name]
        assert text.count('@Test') == len(re.findall(r'(?m)^  void [A-Za-z0-9_]+\(', text)) == COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.platform.' + name not in current['suiteNames']
        assert not any(s in text for s in ('@BeforeAll', '@BeforeEach', '@TempDir', 'ProcessBuilder', 'DriverManager', 'getConnection(', 'System.getenv(', 'LinuxDirectoryCalls', 'TemporaryInfrastructureException', 'WebStartupException', 'FingerprintKeyRing', 'ResponseSnapshotCodec', 'Class.forName(', 'HttpClient'))
    for row in ROWS:
        path, name = source_path(row), row['name']
        assert normal['begin']['inputHashes'][path] == data.sha((data.ROOT / path).read_bytes()) == row['sha256']
        with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
            assert {p[:-6] for p in jar.namelist() if p == name + '.class' or p.startswith(name + '$') and p.endswith('.class')} == set(CLOSURES[name])
    run.step = environmental_step
    run.main()
