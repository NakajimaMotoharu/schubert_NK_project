"""Whole original pure profile4; public literal claim hashes only, no tool authority or actual artifacts."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'BackupProfileTest':4}
SESSION='PG14892-ORIGINAL-BACKUP-PROFILE4'
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/backup'
TESTS={'BackupProfileTest':ROOT/'BackupProfileTest.java'}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14892-backup-profile-four-pt-v1';run.OUT=data.BASE/'PG14892-backup-profile-four-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalBackupProfileJunitLauncher.java';run.NEW_TEST=TESTS['BackupProfileTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);p=run.NEW_TEST;relative=str(p.relative_to(data.ROOT))
    assert normal['begin']['inputHashes'][relative]==run.host.sha(p)==run.host.sha(COMPILE/'snapshot'/relative)=='4a963ac811d3f30f957310ae72755277cbc000f53a26af0da65e1cc822a20fdc'
    source='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/backup/BackupProfile.java';assert normal['begin']['inputHashes'][source]==run.host.sha(data.ROOT/source)=='4b9b04b202f3cafb60dfd69f420ea5e8e688ecf9db9d795998e55929e21ccdd6'
    text=p.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==4
    assert not any(term in text for term in ['ProcessBuilder','DriverManager','Files.','Linux','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
    assert '"dev.codex.schubert.nk.batch.backup.BackupProfileTest", 4' in run.HELPER.read_text()
    run.step=environmental_step;run.main()
