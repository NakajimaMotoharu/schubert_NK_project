"""Original Backup public-codec whole nine in one JVM; no owner/permission/I/O is acquired."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE = run.host.W / 'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA = '1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME = 'dev/codex/schubert/nk/batch/platform/BackupWorkerRequest'
ROWS = [dict(module='batch', name=NAME, sha256='32197ff409b28d61df222cc42ce71740bcfc44b8d3dc066660dca41040fe4c4b', suffixes=['', '$Verification'])]
MAIN_UNITS = {r['name']: r for r in ROWS}
CLOSURES = {NAME: [NAME + s for s in ROWS[0]['suffixes']]}
METADATA = set()
UNEXECUTED = set()
EXECUTED = set(CLOSURES[NAME])
TEST_ROOT = data.ROOT / 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform'
TESTS = {'BackupWorkerRequestTest': TEST_ROOT / 'BackupWorkerRequestTest.java'}
TEST_HASHES = {'BackupWorkerRequestTest': '674c4ec473789c1db6026308e93b6922e4eae59c895b91c8e68c215c06fa39f1'}
COUNTS = {'BackupWorkerRequestTest': 9}
FIXTURES = {}
SESSION = 'PG16042-BACKUP-PUBLIC-REQUEST-WHOLE9'
REPORTER = data.ROOT / 'tools/quality/architecture/SharedSelectedJunitReporterV1.java'


def source_path(row):
    return 'src/schubert-nk-' + row['module'] + '/src/main/java/' + row['name'] + '.java'


if __name__ == '__main__':
    run.SOURCE, run.COMPILE, run.COMPILE_SHA = SOURCE, COMPILE, COMPILE_SHA
    run.SLOT = run.host.W / 'pg16042-backup-public-request-whole9-pt-v1'
    run.OUT = data.BASE / 'PG16042-backup-public-request-whole9-pt-v1'
    run.HELPER = data.ROOT / 'tools/quality/architecture/BackupPublicRequestWholeNineJunitLauncher.java'
    run.NEW_TEST, run.TEST_ROOT = TESTS['BackupWorkerRequestTest'], TEST_ROOT
    run.TEST_SOURCE_OVERRIDES, run.FIXTURES, run.COUNTS = {}, {}, COUNTS
    run.EXTRA_TEST_SOURCES, run.SESSION_ID = (REPORTER,), SESSION
    assert data.sha(REPORTER.read_bytes()) == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert data.sha(run.HELPER.read_bytes()) == '37c5a7e84357ebc852086dc7ded41d8ff202ed0706dfa066766c7ef2b651feb4'
    normal = data.read_checked(COMPILE / 'manifest.safe.json', COMPILE_SHA)
    current = data.read_checked(data.BASE / 'PG16032-current2116-failed-profile-registry-v1/manifest.json', 'a8a019d0f660dba06a1d5b137ae2d0af77b6b2a9e5d1cbf9501054b768ab372a')
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
