"""BUG1749: module-qualified literal25 table, distinct new-only static output."""
from pathlib import Path
import explicit_primary_source_metadata as metadata

TABLE=[
 ('api','api/application/log/LogApplicationFixture','WBS-P006-01'),
 ('api','api/dispatch/ApiReadinessFailureGraph330Test','WBS-P018-05'),
 ('api','api/idempotency/JdbcScenarioSnapshotReplacementTest','WBS-P006-01'),
 ('api','api/idempotency/SnapshotScratchOwnershipTest','WBS-P006-01'),
 ('api','api/messaging/inbound/ParentGraph334Test','WBS-P005-03'),
 ('api','api/messaging/outbound/OutboxFailureOwnershipTest','WBS-P006-02'),
 ('api','api/messaging/outbound/OutboxSecondary330Test','WBS-P006-02'),
 ('batch','batch/mq/AcceptorObjectBoundaryTest','WBS-P017-10'),
 ('batch','batch/mq/ArtemisDetailedValuesTest','WBS-P017-10'),
 ('batch','batch/platform/ServiceDeadlineArgumentTest','WBS-P018-03'),
 ('bootstrap','api/maintenance/SchemaHistoryAdmissionTest','WBS-P019-01'),
 ('bootstrap','bootstrap/FixedNativeCoverageRemovalDuringShutdownProbe','WBS-P018-08'),
 ('bootstrap','bootstrap/SystemdBinderAbiTest','WBS-P018-03'),
 ('web','web/bootstrap/WebReadinessFailureGraph330Test','WBS-P018-06'),
 ('web','web/logging/JdbcWebSessionStoreTest','WBS-P015-01'),
 ('web','web/messaging/BrokerGraph334Test','WBS-P005-02'),
 ('web','web/messaging/ReplyCleanup333Test','WBS-P005-02'),
 ('web','web/messaging/ReplyCommittedTerminalAdmissionContractTest','WBS-P005-02'),
 ('web','web/messaging/ReplyConsumerGraph332Test','WBS-P005-02'),
 ('web','web/messaging/ReplyFatalIsolationContractTest','WBS-P005-02'),
 ('web','web/messaging/ReplyRollbackSignalContractTest','WBS-P005-02'),
 ('web','web/messaging/ReplyRollbackUnconfirmedContractTest','WBS-P005-02'),
 ('web','web/receipt/ReceiptFailureGraph329Test','WBS-P011-04'),
 ('web','web/receipt/ReceiptReferenceFaultTest','WBS-P011-04'),
 ('web','web/session/SessionRollbackAttachment329Test','WBS-P015-01')]
PRIMARY={'src/schubert-nk-'+module+'/src/test/java/dev/codex/schubert/nk/'+name+'.java':owner for module,name,owner in TABLE}

if __name__=='__main__':
    assert len(TABLE)==len(PRIMARY)==25
    metadata.run(Path(__file__),metadata.BASE/'PG9410-reflective25-source-metadata-v2',metadata.ROOT.parent/'pgpt-runs/PG379/pg9410-reflective25-source-metadata-v2',
      PRIMARY,'PG9402-protocol-composite-join-v1/manifest.json','6bc494ba796f9752639739ea1d6cdb811f160637dd82cd1fc0866b2943e9e985',True)
