"""New independent public data fixture, not a held-suite extraction or a crypto operation."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE = run.host.W / 'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA = '1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX = 'dev/codex/schubert/nk/api/idempotency/'
ROWS = [
    dict(module='api', name=PREFIX + 'CanonicalField', sha256='427b37bf360f201bd1509e336aa435f2a1db77c9f782b842aa2bf16fdcc28e3a', suffixes=['']),
    dict(module='api', name=PREFIX + 'ResponseSnapshotIdentity', sha256='66e9e45738d02de02e8c0d336e997c2e2878f96e1620d84ae532c663ebd3418c', suffixes=[''])]
MAIN_UNITS = {r['name']: r for r in ROWS}
CLOSURES = {r['name']: [r['name']] for r in ROWS}
METADATA = set()
EXECUTED = set(MAIN_UNITS)
UNEXECUTED = set()
ROOT = data.ROOT / 'tools/quality/architecture'
TEST = ROOT / 'PublicCanonicalAadValueTest.java'
TEST_SHA = '9ba9b2009e7623821dc0a9d6bad223ed24b27d4005a761039dc2d551e03ec2d1'
TESTS = {'PublicCanonicalAadValueTest': TEST}
COUNTS = {'PublicCanonicalAadValueTest': 8}
FIXTURES = {}
SESSION = 'PG16082-PUBLIC-CANONICAL-AAD-EIGHT'
REPORTER = ROOT / 'SharedSelectedJunitReporterV1.java'

def source_path(row):
    return 'src/schubert-nk-' + row['module'] + '/src/main/java/' + row['name'] + '.java'

if __name__ == '__main__':
    run.SOURCE, run.COMPILE, run.COMPILE_SHA = SOURCE, COMPILE, COMPILE_SHA
    run.SLOT = run.host.W / 'pg16082-public-canonical-aad-eight-pt-v1'
    run.OUT = data.BASE / 'PG16082-public-canonical-aad-eight-pt-v1'
    run.HELPER = ROOT / 'PublicCanonicalAadValueJunitLauncher.java'
    run.NEW_TEST, run.TEST_ROOT = TEST, ROOT
    run.TEST_SOURCE_OVERRIDES, run.FIXTURES, run.COUNTS = {}, {}, COUNTS
    run.EXTRA_TEST_SOURCES, run.SESSION_ID = (REPORTER,), SESSION
    proof = data.read_checked(data.BASE / 'PG13728-shared-reporter-selftest-post-v1/manifest.json', '32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit'] == proof['productTestsExecuted'] == 0 and proof['toolChecksIndependentlyConfirmed'] == 12
    assert run.host.sha(REPORTER) == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(TEST) == TEST_SHA and run.host.sha(run.HELPER) == '3e1e90e527ec9db8546d586723eef3b92a22c0ea2c8d0371106fe9a2a5a4c0d6'
    text = TEST.read_text()
    assert text.count('@Test') == len(re.findall(r'@Test\s+void\s+public[0-9]{3}[A-Za-z0-9_]+\s*\(', text)) == 8
    assert not any(term in text for term in ['ProcessBuilder', 'DriverManager', 'Files.', 'Linux', 'getenv(', 'java.sql', 'ManagementFactory', 'TemporaryInfrastructureException', 'WebStartupException', 'FingerprintKeyRing', 'ResponseSnapshotCodec', 'javax.crypto', 'MessageDigest', '@TempDir'])
    normal = data.read_checked(COMPILE / 'manifest.safe.json', COMPILE_SHA)
    previous = data.read_checked(data.BASE / 'PG16048-current2125-backup-request-registry-v1/manifest.json', '1481270818c601b5881b4f6e9fe55a9d4ac18e17e8a3698bf683161affdb71a9')
    assert normal['source'] == previous['source'] == SOURCE
    assert 'dev.codex.schubert.nk.api.idempotency.PublicCanonicalAadValueTest' not in previous['suiteNames']
    for row in ROWS:
        path = source_path(row)
        assert normal['begin']['inputHashes'][path] == run.host.sha(data.ROOT / path) == run.host.sha(COMPILE / 'snapshot' / path) == row['sha256']
        assert row['name'] in previous['fullSourceUnits'] and not previous['fullSourceUnits'][row['name']]['four100']
        with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
            assert {p[:-6] for p in jar.namelist() if p == row['name'] + '.class' or p.startswith(row['name'] + '$') and p.endswith('.class')} == {row['name']}
    run.step = environmental_step
    run.main()
