"""Exact37 batch file source primaries; static metadata, not FD/Root/permit execution."""
from pathlib import Path
import explicit_primary_source_metadata as metadata

PREFIX='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/'
TABLE={
 'file/BackupArtifactFixture.java':'WBS-P017-05',
 'file/BackupPublicationFixture.java':'WBS-P017-04',
 'file/BackupRequestReadBoundaryTest.java':'WBS-P017-03',
 'file/BackupRetentionBoundaryTest.java':'WBS-P017-05',
 'file/BackupRetentionRejectionTest.java':'WBS-P017-05',
 'file/BackupStartIntentCollisionTest.java':'WBS-P017-06',
 'file/ExpiryOwnerTest.java':'WBS-P017-08',
 'file/ExpiryResultContractTest.java':'WBS-P017-08',
 'file/ExternalEntryRejectionTest.java':'WBS-P018-03',
 'file/MainTerminationPortTest.java':'WBS-P017-12',
 'file/MaintenanceRetirementRecordsTest.java':'WBS-P004-03',
 'file/MaintenanceRunRetirementTest.java':'WBS-P004-03',
 'file/MorningBackupMetadataTest.java':'WBS-P017-03',
 'file/MorningBackupObservedCompletionTest.java':'WBS-P017-12',
 'file/MorningCleanupCompletionTest.java':'WBS-P017-07',
 'file/MorningCompletedMainTest.java':'WBS-P017-12',
 'file/MorningCompletionRetirementTest.java':'WBS-P017-12',
 'file/MorningGateEvidenceBrokerTest.java':'WBS-P018-03',
 'file/MorningOriginalCompletionTest.java':'WBS-P017-02',
 'file/MorningStartupLaunchOwnerAdmissionTest.java':'WBS-P017-12',
 'file/ObservationValueRedactionTest.java':'WBS-P018-03',
 'file/PostgresObservationRowsTest.java':'WBS-P018-03',
 'file/RetainedExpiryAuditTest.java':'WBS-P017-08',
 'file/RetentionWireBoundaryTest.java':'WBS-P017-05',
 'file/RootElfDigestPortTest.java':'WBS-P018-03',
 'file/RootEntryRejectionTest.java':'WBS-P018-03',
 'file/RootFailedStartPairRecoveryTest.java':'WBS-P017-12',
 'file/RootPendingWaitTest.java':'WBS-P017-12',
 'file/RootRecoveryNativeAuthorityTest.java':'WBS-P017-12',
 'file/RootServiceEnvironmentTest.java':'WBS-P018-03',
 'file/RootServiceProofTest.java':'WBS-P018-03',
 'file/StartupAdmissionViewOwnerTest.java':'WBS-P018-03',
 'file/StartupLaunchBoundaryTest.java':'WBS-P018-03',
 'file/StoppedBackupCompletionTest.java':'WBS-P017-12',
 'file/TransferCleanupFailureTest.java':'WBS-P017-09',
 'file/TransferIoBoundaryTest.java':'WBS-P017-09',
 'file/UnsupportedBackupVerificationTest.java':'WBS-P017-03',}
PRIMARY={PREFIX+path:owner for path,owner in TABLE.items()}

if __name__=='__main__':
    assert len(PRIMARY)==37
    metadata.run(Path(__file__),metadata.BASE/'PG9494-batch-file37-source-metadata-v1',
      metadata.ROOT.parent/'pgpt-runs/PG379/pg9494-batch-file37-source-metadata-v1',PRIMARY,
      'PG9486-batch-platform22-source-join-v1/manifest.json','960c0986edd66ef7626d8d752497bf3a49700ed3e68019db1d3ac31b708ff405',False)
