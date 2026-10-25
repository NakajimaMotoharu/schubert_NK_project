"""Bootstrap module and one batch checkpoint fixture17; metadata only, never credential/runtime IO."""
from pathlib import Path
import explicit_primary_source_metadata as metadata

PRIMARY={
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/BackupCredentialLoaderTest.java':'WBS-P018-01',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/BackupRequestCredentialLoaderTest.java':'WBS-P018-01',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/BootstrapCredentialLoaderTest.java':'WBS-P018-01',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/EnumValueCatalogCompatibilityTest.java':'WBS-P018-01',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/InspectorDatabaseCredentialLoaderTest.java':'WBS-P018-01',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/MaintenanceOwnerCredentialReaderTest.java':'WBS-P018-01',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/PublicApiCredentialFixture.java':'WBS-P018-01',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/ServiceNativeReleaseTest.java':'WBS-P018-04',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/ServiceOwnedReleaseTest.java':'WBS-P018-04',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/ServiceResourceRetentionTest.java':'WBS-P018-04',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/maintenance/ServiceDatabaseAdmissionTest.java':'WBS-P019-01',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/ChildBrokerTest.java':'WBS-P018-03',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/ChildCaddyTest.java':'WBS-P018-03',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/ChildMaintenanceInspectorTest.java':'WBS-P018-03',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/NativeCoverageExportTest.java':'WBS-P018-08',
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/TerminalNativeCoverageProfileTest.java':'WBS-P018-08',
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/bootstrap/RootEntryCheckpointFixture.java':'WBS-P018-08',}

if __name__=='__main__':
    assert len(PRIMARY)==17
    metadata.run(Path(__file__),metadata.BASE/'PG9506-bootstrap17-source-metadata-v1',
      metadata.ROOT.parent/'pgpt-runs/PG379/pg9506-bootstrap17-source-metadata-v1',PRIMARY,
      'PG9498-batch-file37-source-join-v1/manifest.json','96770fbedea32222e1492af2b158cfa9055622a31d15486c4ac7b4033723a1a4',False)
