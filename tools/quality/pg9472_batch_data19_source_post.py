"""Independent literal Batch19 primary/related table, with explicit foreign-module rejection."""
from pathlib import Path
import explicit_primary_source_post as post

def other_module(path):
    prefix='src/schubert-nk-batch/src/test/java/'
    if not path.startswith(prefix):raise ValueError('explicit batch module required')
    return 'src/schubert-nk-api/src/test/java/'+path[len(prefix):]

if __name__=='__main__':
    assert other_module('src/schubert-nk-batch/src/test/java/p/Foo.java')=='src/schubert-nk-api/src/test/java/p/Foo.java'
    post.run(Path(__file__),post.BASE/'PG9472-batch-data19-source-post-v1','PG9470-batch-data19-source-metadata-v2',
      '03280b63db32bcc34f068ae109bff7c770bb08c63f44e16edce1020a16c2fb0f','dd8893883f5ed11d8a8fbde11b58a98c257780331d51efb73372dd08a239ff7c',
      'evidence/01_PT/018_NK-OPS-001/1922_G13BatchData19_主関連責任仕様.md','e7ca235a875820a387f2809a836e22c8ef79036e314db1145fed0e3ad23cd34d',
      'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/',('backup/','repository/','file/','mq/'),19,
      {'BackupManifest':'WBS-P017-05','BackupVersions':'WBS-P017-05','BackupStepRepository':'WBS-P017-06',
       'MorningDatabaseSession':'WBS-P017-01','BatchStep':'WBS-P017-02','CleanupStepRepository':'WBS-P017-07',
       'CleanupStepChunk':'WBS-P017-07','ExpiryAuditRepository':'WBS-P017-11','StartupPermitRecords':'WBS-P018-03',
       'ArtemisManagementReadinessClient':'WBS-P017-10'},source_path_mutator=other_module,source_mutator_vectors=1)
