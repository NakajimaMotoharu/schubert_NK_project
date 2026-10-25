"""Exact API32/Web10 source responsibility metadata, not business/runtime test execution."""
from pathlib import Path
import explicit_primary_source_metadata as metadata

PRIMARY={
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/UserApplicationFixture.java':'WBS-P010-02',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/log/LogVectors.java':'WBS-P018-09',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/media/MediaReplayFixture.java':'WBS-P009-01',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/media/MediaRequestFixture.java':'WBS-P001-03',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/media/MediaStageFixture.java':'WBS-P009-01',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/QuestionProviderFailureGraph329Test.java':'WBS-P012-03',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/QuestionQueryRepositoryTest.java':'WBS-P014-01',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/QuestionSubmissionBoundaryRemainderTest.java':'WBS-P011-02',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/scenario/ScenarioMessageGuardTest.java':'WBS-P006-01',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/scenario/ScenarioReplayFixture.java':'WBS-P008-01',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/scenario/ScenarioRequestFixture.java':'WBS-P001-03',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiAdmittedConfigurationTest.java':'WBS-P018-05',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementBindTest.java':'WBS-P018-05',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementDefaultBindTest.java':'WBS-P018-05',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementStopTest.java':'WBS-P018-05',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/file/ApiBrokerContextsCredentialTest.java':'WBS-P005-03',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/file/InspectorOwnerContractTest.java':'WBS-P004-04',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/file/MediaAssetFixture.java':'WBS-P003-04',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/AuthenticationInboxCleanupTest.java':'WBS-P004-02',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InboxCleanupNonAuthenticationTest.java':'WBS-P004-02',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InboxDeletionBoundaryTest.java':'WBS-P004-04',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InboxInspectionBoundaryTest.java':'WBS-P004-04',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InboxInspectionProgressTest.java':'WBS-P004-04',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InspectorFailureGraph329Test.java':'WBS-P004-04',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/QuestionQueryInboxCleanupTest.java':'WBS-P004-02',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/ResultBoundResponseSnapshotCodecTest.java':'WBS-P006-01',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/config/ArtemisFileJournalTest.java':'WBS-P005-03',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AuthenticationJdbcBoundary329Test.java':'WBS-P007-01',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/EnumValueCatalogCompatibilityTest.java':'WBS-P005-04',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/ExceptionValueContractTest.java':'WBS-P007-03',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/storage/ApiPreparationOwnerTest.java':'WBS-P018-05',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/storage/RealScenarioFileFixture.java':'WBS-P008-03',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/JmsSecondary330Test.java':'WBS-P006-04',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/LocalAuditGraph331Test.java':'WBS-P006-03',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/RequestProjectionFailureGraph329Test.java':'WBS-P006-03',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebApiLogReplayIntegrationTest.java':'WBS-P006-05',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebAuditSinkContractTest.java':'WBS-P006-03',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebOwnedAttachment329Test.java':'WBS-P006-04',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/ExceptionValueContractTest.java':'WBS-P005-02',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/ReplyIsolationPrimaryContractTest.java':'WBS-P005-02',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/WebBusinessWireClientsTest.java':'WBS-P005-02',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/WebFactoryNativeRetentionTest.java':'WBS-P005-02',}

if __name__=='__main__':
    assert len(PRIMARY)==42
    metadata.run(Path(__file__),metadata.BASE/'PG9518-api-web42-source-metadata-v1',
      metadata.ROOT.parent/'pgpt-runs/PG379/pg9518-api-web42-source-metadata-v1',PRIMARY,
      'PG9510-bootstrap17-source-join-v1/manifest.json','7f314d491c7ff05eabf7464cd3f42efb313cfbb5e8c499b5c49b316f77f3c650',False)
