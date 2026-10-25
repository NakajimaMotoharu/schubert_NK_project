"""Independent Batch22 literal table; service/Root authority is never inferred from metadata."""
from pathlib import Path
import explicit_primary_source_post as post
from pg9472_batch_data19_source_post import other_module

if __name__=='__main__':
    post.run(Path(__file__),post.BASE/'PG9484-batch-platform22-source-post-v1','PG9482-batch-platform22-source-metadata-v1',
      '5b1ae75f2003e104021422da9c16ab93d944434b68cc600bf1a897f407787318','2e972e8ebcc75958eb1240f4b742befde945601dc6fb8942b407281c77422c18',
      'evidence/01_PT/018_NK-OPS-001/1924_G13BatchPlatform22_主関連責任仕様.md','b8f848af5ba8ceaed57c5c6e731ad8bf585223cd6c86e72f0ec264550186014d',
      'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/',('platform/',),22,
      {'InspectorUnitProbe':'WBS-P004-04','InspectorUnitSnapshot':'WBS-P004-04','BackupUnitStartClient':'WBS-P017-06',
       'MorningBackupUnitCycle':'WBS-P017-06','MorningBrokerUnitCycle':'WBS-P017-10','CleanupWorkerRequest':'WBS-P017-07',
       'CleanupFailedBackupRequest':'WBS-P017-06','RootStartupContext':'WBS-P018-03','MorningGateEvidence':'WBS-P018-03',
       'MorningServiceReadiness':'WBS-P018-07','FixedUnitCgroupNamespace':'WBS-P018-04','ApplicationUnit':'WBS-P018-04'},
      source_path_mutator=other_module,source_mutator_vectors=1)
