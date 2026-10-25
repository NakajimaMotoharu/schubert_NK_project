"""Close7 shared fixture responsibilities only; SQL/child/production tests remain unexecuted."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_SHARED_FIXTURE7_SOURCE_V1',close.BASE/'PG9550-shared-fixture7-metrics-v1',
      close.BASE/'PG9552-shared-fixture7-public-delta-v1','e94801bf34204312cd587841a57265996905c748',dict(
        groupStartEstimatePp=dict(low=.5,base=3,high=7),groupCapPp=10,
        quotaBefore=dict(usedPercent=2,remainingPercent=98,resetsAt=1793513544),quotaAfter=dict(usedPercent=2,remainingPercent=98,resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T06:50:14Z',quotaAfterObservedAtUTC='2026-10-25T06:55:02Z',sameQuotaWindow=True,observedSharedPp=0,
        attemptResult='7_SHARED_FIXTURE_DDL_OR_UNIQUE_COMMON_MAIN_RESPONSIBILITIES_REGISTERED_REMAIN8',
        originalPlanEngineeringDelta=dict(item='EXACT_SHARED_FIXTURE7_EXPLICIT_RESOURCE_COMMON_CONTRACT_RESPONSIBILITIES',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[],ykt=[]),
        sourceReauthentication=dict(old949CanonicalRelatedRuntimeArtifactFieldsPreserved=True,oldSourceResultsTransferred=False,currentNormalSnapshotHashesExact=True),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1,producerRetries=0,editHunkOrderRefusedBeforeWrite=1,targetCompile=0,targetRuntimeInvocation=0,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=7,sourceRows=956,javaPaths=1789,registered=1781,registeredMain=965,totalMain=965,
          registeredTest=816,totalTest=824,unregisteredTest=8,remainingMultiOwner=2,remainingNoMainCpUnregistered=6,
          verifiedFixtureSources=7,primaryArtifactWitnessFiles=30,sqlArtifacts=29,uniqueCommonMainContracts=1,ownedRetentionDirectConsumers=6,
          independentlyParsedTestClassFiles=1910,catalogNegatives=11,mapperNegatives=8,neighbourInvariance=7,snapshotNegatives=6,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1935_G13SharedFixture7_資源・共通Main責任結果.md'],
        tokenMeasurementIds=['9ebcaea8f7a22ca46f12474c00e781985ea89e09d5580d118e23bbd1561873f8'],
        nextCommand='9552 publicdelta/save-push; fresh current-window remaining>10 then remaining8 method/TestID responsibilities or independent ordinary PGPT'),[
        ('PG9542-shared-fixture7-source-metadata-v1/manifest.json','5e231aad063060ee16adb8eb4bf6e281df3a6ac3e8eca6d0b20de9ead46ea513'),
        ('PG9544-shared-fixture7-source-post-v1/manifest.json','b3fe5741799dfa2d46af261279baf5753bb07f77ba1e60bfa8c7bb3aa66da643'),
        ('PG9546-shared-fixture7-source-join-v1/manifest.json','4d82743eb894ccd448a2ef88b40f566bc0fb08a8ee4b5128a925e49c08b7dd61'),
        ('PG9548-shared-fixture7-snapshot-post-v1/manifest.json','8ac9d20345e3fb9f8e448a282d3959626b4fac7c4fc5d015871ae122e0e464b0')])
