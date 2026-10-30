"""Original whole eight-case byte codec, public synthetic golden, own trace only; no actual backup."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'BackupManifestCodecTest':8}
SESSION='PG14886-ORIGINAL-BACKUP-MANIFEST-CODEC8'
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file'
TESTS={'BackupManifestCodecTest':ROOT/'BackupManifestCodecTest.java'}
FIXTURES={'src/schubert-nk-batch/src/test/resources/backup/manifest-golden.json':'733939f4daa4dcb642e6b9a4433c92daf3d42e8ac73a15b0aee914b58571289e'}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
EXTRA=ROOT.parent/'backup/BackupManifestFixture.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14886-backup-manifest-codec-eight-pt-v1';run.OUT=data.BASE/'PG14886-backup-manifest-codec-eight-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalBackupManifestCodecJunitLauncher.java';run.NEW_TEST=TESTS['BackupManifestCodecTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,EXTRA);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    for path,pin in [(run.NEW_TEST,'c474a1eea57ea0a3974fcb577c3d068154d634cd41580d27343954a1b18d3692'),(EXTRA,'dc52d8ad7f4cc73b2947257e458bb8e36f10221789218812c44010c72951e976')]:
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==pin
    text=run.NEW_TEST.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==8
    for line in ['Files.createDirectories(traces);','Files.write(traces.resolve("PT-BAT-186-manifest.json"), encoded);']:
        assert text.count(line)==1;text=text.replace(line,'')
    assert 'Path traces = Path.of("target", "backup-manifest-traces");' in text and 'Files.' not in text
    assert not any(term in text+EXTRA.read_text() for term in ['ProcessBuilder','DriverManager','Linux','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
    assert '"dev.codex.schubert.nk.batch.file.BackupManifestCodecTest", 8' in run.HELPER.read_text()
    run.step=environmental_step;run.main()
