"""Close42 API/Web metadata only, retaining unresolved20 and all runtime/formal holds."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_API_WEB42_SOURCE_V1',close.BASE/'PG9526-api-web42-metrics-v1',
      close.BASE/'PG9528-api-web42-public-delta-v1','fa5ce0726555c716efdcc840e75eec80f4a2c722',dict(
        groupStartEstimatePp=dict(low=.5,base=3,high=8),groupCapPp=10,
        quotaBefore=dict(usedPercent=1,remainingPercent=99,resetsAt=1793513544),quotaAfter=dict(usedPercent=1,remainingPercent=99,resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T06:36:23Z',quotaAfterObservedAtUTC='2026-10-25T06:39:14Z',sameQuotaWindow=True,observedSharedPp=0,
        attemptResult='42_API_WEB_SOURCE_PRIMARY_RELATED_RESPONSIBILITIES_REGISTERED_REMAIN20_UNCERTAINTY_RETAINED',
        originalPlanEngineeringDelta=dict(item='EXACT_API_WEB42_SOURCE_PRIMARY_RESPONSIBILITIES',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[],ykt=[]),
        sourceReauthentication=dict(old902CanonicalRelatedRuntimeArtifactFieldsPreserved=True,oldSourceResultsTransferred=False,currentNormalSnapshotHashesExact=True),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1,producerRetries=0,primaryMembershipPreflight=42,targetCompile=0,targetRuntimeInvocation=0,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=42,sourceRows=944,javaPaths=1789,registered=1769,registeredMain=965,totalMain=965,
          registeredTest=804,totalTest=824,unregisteredTest=20,remainingMultiOwner=2,remainingNoMainCp=18,
          verifiedSourceClosure=67,independentTestClassDeclarations=130,independentMainClassDeclarations=277,independentUniqueMainSourceFiles=238,
          catalogNegatives=9,mapperNegatives=8,neighbourInvariance=42,snapshotNegatives=6,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1931_G13ApiWeb42_主関連責任結果.md'],
        tokenMeasurementIds=['75331eb9803402298480892cf071aec4b2c40c550fbff98f402375e1dd4fa3e6'],
        nextCommand='9528 publicdelta/save-push; fresh current-window remaining>10 then remaining20 ownership roots or independent ordinary PGPT'),[
        ('PG9518-api-web42-source-metadata-v1/manifest.json','61ef8d45de754b88b2f9dfe9fb2f81ef14f539eba830910a605dd81f85d8b295'),
        ('PG9520-api-web42-source-post-v1/manifest.json','4f8bc5b38d2aaac3af21860bf789753f35138de39a32ae72b96c140e5852c6a9'),
        ('PG9522-api-web42-source-join-v1/manifest.json','4f85bf805c3e32dbe668e6374bf6a70cb6fa6c0d93edd1ef4ea99bc30925f927'),
        ('PG9524-api-web42-snapshot-post-v1/manifest.json','b65797c0e553fab5c22951eb22668e86e5d590da001ade574a20dd980875ad94')])
