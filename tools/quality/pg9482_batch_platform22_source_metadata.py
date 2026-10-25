"""Batch platform22 source metadata only; never instantiate targets or touch any service."""
from pathlib import Path
import explicit_primary_source_metadata as metadata

PREFIX='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/'
TABLE={
 'platform/ArtemisUnitSnapshotTest.java':'WBS-P004-04',
 'platform/BrokerJournalQueryTest.java':'WBS-P004-04',
 'platform/CaddyAdmissionFenceTest.java':'WBS-P017-06',
 'platform/CgroupPrimitiveOwnerTest.java':'WBS-P018-04',
 'platform/CleanupUnitCycleTest.java':'WBS-P017-06',
 'platform/EnumValueCatalogCompatibilityTest.java':'WBS-P018-04',
 'platform/ExpiryReceiptFixture.java':'WBS-P017-06',
 'platform/ExpiryRequestBoundaryTest.java':'WBS-P017-07',
 'platform/ExpiryWorkerRequestTest.java':'WBS-P017-07',
 'platform/FailedProfileBoundaryTest.java':'WBS-P017-06',
 'platform/InspectorHeldStateContractTest.java':'WBS-P004-04',
 'platform/InspectorUnitCycleTest.java':'WBS-P017-06',
 'platform/InspectorUnitProbeFixture.java':'WBS-P004-04',
 'platform/MorningNoPriorBrokerTest.java':'WBS-P017-10',
 'platform/MorningServiceReadinessNativeTest.java':'WBS-P018-07',
 'platform/MorningStopEvidenceTest.java':'WBS-P018-03',
 'platform/RootGenerationCounterexampleTest.java':'WBS-P018-03',
 'platform/RootGenerationTruthTableTest.java':'WBS-P018-03',
 'platform/ServiceIntentReadyRetirementTest.java':'WBS-P017-06',
 'platform/StoppedBackupFixture.java':'WBS-P017-06',
 'platform/UnsupportedRootIdentityTest.java':'WBS-P018-03',
 'platform/UnsupportedServiceMarkerTest.java':'WBS-P017-06',}
PRIMARY={PREFIX+path:owner for path,owner in TABLE.items()}

if __name__=='__main__':
    assert len(PRIMARY)==22
    metadata.run(Path(__file__),metadata.BASE/'PG9482-batch-platform22-source-metadata-v1',
      metadata.ROOT.parent/'pgpt-runs/PG379/pg9482-batch-platform22-source-metadata-v1',PRIMARY,
      'PG9474-batch-data19-source-join-v1/manifest.json','916f308c85f4b0465f2ef54bfe64b2bbb1529ecf57235a521fe3a67c9422e32c',False)
