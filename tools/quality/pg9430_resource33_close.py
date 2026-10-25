"""Close source/resource responsibility33 without executing production resources or tests."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_RESOURCE33_SOURCE_OWNERS_V1',close.BASE/'PG9430-resource33-metrics-v1',
      close.BASE/'PG9432-resource33-public-delta-v1','580154e6908cd193f8fffec316bf8900e50ecf4b',dict(
        groupStartEstimatePp=dict(low=.5,base=2,high=5),groupCapPp=10,
        quotaBefore=dict(usedPercent=66,remainingPercent=34,resetsAt=1793382075),quotaAfter=dict(usedPercent=66,remainingPercent=34,resetsAt=1793382075),
        quotaBeforeObservedAtUTC='2026-10-25T05:20:43Z',quotaAfterObservedAtUTC='2026-10-25T05:29:41Z',sameQuotaWindow=True,observedSharedPp=0,
        attemptResult='33_EXACT_RESOURCE_SQL_UNIT_JS_BUILD_SOURCE_RESPONSIBILITIES_REGISTERED_NOT_RUNTIME_PT; REMAIN223',
        originalPlanEngineeringDelta=dict(item='EXACT_RESOURCE33_PRIMARY_SOURCE_RESPONSIBILITIES',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[],ykt=[],sharedJdbcOrFixture18NotAssigned=True,primaryWitnessNotExhaustiveDependencies=True),
        sourceReauthentication=dict(old708CanonicalRelatedAndRuntimePreserved=True,oldSourceResultsTransferred=False,currentNormalSnapshotHashesExact=True,
          original941ResourcesAndBudgetsUnchanged=True),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1,producerRetries=0,targetCompile=0,targetRuntimeInvocation=0,
          independentTestClassDeclarations=42,uniqueSourceFiles=33,uniqueArtifactWitnessFiles=54,sourceSelectionVectors=5,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=33,sourceRows=741,javaPaths=1789,registered=1566,registeredMain=965,totalMain=965,
          registeredTest=601,totalTest=824,unregisteredTest=223,uniqueArtifactWitnessFiles=54,independentTestClassDeclarations=42,
          catalogNegatives=9,mapperNegatives=10,neighbourInvariance=33,snapshotNegatives=6,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1915_G13Resource33_製造artifact担当対応結果.md'],
        tokenMeasurementIds=['002c9850cec97b4a8a6f847438e9a83efad08e7c9d023f9409f3044881f7a6e3'],
        nextCommand='9432 public scan/save-push; remaining223 composite/fixture source responsibilities and independent PG/PT'),[
        ('PG9422-resource33-source-metadata-v1/manifest.json','376d762a7f0806073fe2cc57692eca7842fb3323243e92b5fea3ac947081ab78'),
        ('PG9424-resource33-source-post-v1/manifest.json','73b3eee45b6f17c32a2da075e1e8cfa5f91fdf9cd1747c1c59147d4c6ecec8a9'),
        ('PG9426-resource33-source-join-v1/manifest.json','91f349d3158c28d4b6da2bfddf9c2ca1b9469de764ebb2d87cb4c7d137f21690'),
        ('PG9428-resource33-snapshot-post-v1/manifest.json','49741c75ccceab1f2c7e672b8760e5b4c9adaae24361ba7bd28226d8f1db1749')])
