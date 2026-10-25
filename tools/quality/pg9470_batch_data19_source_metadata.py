"""Frozen19 batch source primaries; metadata only, never database, broker or target execution."""
from pathlib import Path
import explicit_primary_source_metadata as metadata

PREFIX='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/'
TABLE={
 'backup/BackupManifestFixture.java':'WBS-P017-05','backup/BackupManifestValuesTest.java':'WBS-P017-05',
 'repository/BackupStepFixture.java':'WBS-P017-05','repository/BackupTerminalObservationTest.java':'WBS-P017-01',
 'repository/BatchStepValuesTest.java':'WBS-P017-02','repository/CleanupStepFixture.java':'WBS-P017-07',
 'repository/CleanupStepValuesTest.java':'WBS-P017-07','repository/EnumValueCatalogCompatibilityTest.java':'WBS-P017-02',
 'repository/ExpiryAuditResourceFailureTest.java':'WBS-P017-11','repository/ExpirySuccessfulScopeTest.java':'WBS-P017-11',
 'repository/MorningDatabaseAccessContractTest.java':'WBS-P017-01','repository/MorningExpiryObservationInvariantTest.java':'WBS-P017-01',
 'repository/MorningExpirySessionTest.java':'WBS-P017-01','repository/MorningSuccessfulBackupProjectionTest.java':'WBS-P017-01',
 'repository/WebReceiptCleanupTest.java':'WBS-P017-07','file/CurrentObservationValueTest.java':'WBS-P018-03',
 'mq/ArtemisManagementEncoderBoundaryTest.java':'WBS-P017-10','mq/ArtemisParentDeadlineTest.java':'WBS-P017-10',
 'mq/ArtemisUnknownBoundaryTest.java':'WBS-P017-10'}
PRIMARY={PREFIX+path:owner for path,owner in TABLE.items()}

if __name__=='__main__':
    assert len(PRIMARY)==19
    metadata.run(Path(__file__),metadata.BASE/'PG9470-batch-data19-source-metadata-v2',
      metadata.ROOT.parent/'pgpt-runs/PG379/pg9470-batch-data19-source-metadata-v2',PRIMARY,
      'PG9462-web-screen22-source-join-v1/manifest.json','7ea77aaaa24b59d395ea34e6e1e0af822ec5d43354c6ec1e4748f0c0b9084bdc',False)
