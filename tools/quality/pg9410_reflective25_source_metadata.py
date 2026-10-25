"""1912 literal source responsibility25 only; actual reflection/native/DB remain unexecuted."""
from pathlib import Path
import explicit_primary_source_metadata as metadata

PRIMARY={
 'LogApplicationFixture':'WBS-P006-01','ApiReadinessFailureGraph330Test':'WBS-P018-05','JdbcScenarioSnapshotReplacementTest':'WBS-P006-01',
 'SnapshotScratchOwnershipTest':'WBS-P006-01','ParentGraph334Test':'WBS-P005-03','OutboxFailureOwnershipTest':'WBS-P006-02','OutboxSecondary330Test':'WBS-P006-02',
 'AcceptorObjectBoundaryTest':'WBS-P017-10','ArtemisDetailedValuesTest':'WBS-P017-10','ServiceDeadlineArgumentTest':'WBS-P018-03',
 'SchemaHistoryAdmissionTest':'WBS-P019-01','FixedNativeCoverageRemovalDuringShutdownProbe':'WBS-P018-08','SystemdBinderAbiTest':'WBS-P018-03',
 'WebReadinessFailureGraph330Test':'WBS-P018-06','JdbcWebSessionStoreTest':'WBS-P015-01','BrokerGraph334Test':'WBS-P005-02',
 'ReplyCleanup333Test':'WBS-P005-02','ReplyCommittedTerminalAdmissionContractTest':'WBS-P005-02','ReplyConsumerGraph332Test':'WBS-P005-02',
 'ReplyFatalIsolationContractTest':'WBS-P005-02','ReplyRollbackSignalContractTest':'WBS-P005-02','ReplyRollbackUnconfirmedContractTest':'WBS-P005-02',
 'ReceiptFailureGraph329Test':'WBS-P011-04','ReceiptReferenceFaultTest':'WBS-P011-04','SessionRollbackAttachment329Test':'WBS-P015-01'}

if __name__=='__main__':
    metadata.run(Path(__file__),metadata.BASE/'PG9410-reflective25-source-metadata-v1',metadata.ROOT.parent/'pgpt-runs/PG379/pg9410-reflective25-source-metadata-v1',
      PRIMARY,'PG9402-protocol-composite-join-v1/manifest.json','6bc494ba796f9752639739ea1d6cdb811f160637dd82cd1fc0866b2943e9e985',True)
