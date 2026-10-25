"""Close17 Bootstrap metadata only, preserving all formal/safety/cost distinctions."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_BOOTSTRAP17_SOURCE_V1',close.BASE/'PG9514-bootstrap17-metrics-v1',
      close.BASE/'PG9516-bootstrap17-public-delta-v1','c9bda14c007c6d89d364e021e23d08f1e0c7eca4',dict(
        groupStartEstimatePp=dict(low=.5,base=2,high=5),groupCapPp=10,
        quotaBefore=dict(usedPercent=1,remainingPercent=99,resetsAt=1793513544),quotaAfter=dict(usedPercent=1,remainingPercent=99,resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T06:33:04Z',quotaAfterObservedAtUTC='2026-10-25T06:35:12Z',sameQuotaWindow=True,observedSharedPp=0,
        attemptResult='17_BOOTSTRAP_SHARED_CHECKPOINT_SOURCE_PRIMARY_RELATED_RESPONSIBILITIES_REGISTERED_REMAIN62',
        originalPlanEngineeringDelta=dict(item='EXACT_BOOTSTRAP17_SOURCE_PRIMARY_RESPONSIBILITIES',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[],ykt=[]),
        sourceReauthentication=dict(old885CanonicalRelatedRuntimeArtifactFieldsPreserved=True,oldSourceResultsTransferred=False,currentNormalSnapshotHashesExact=True),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1,producerRetries=0,primaryMembershipPreflight=17,targetCompile=0,targetRuntimeInvocation=0,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=17,sourceRows=902,javaPaths=1789,registered=1727,registeredMain=965,totalMain=965,
          registeredTest=762,totalTest=824,unregisteredTest=62,remainingMultiOwner=44,remainingNoMainCp=18,
          verifiedSourceClosure=23,independentTestClassDeclarations=58,independentMainClassDeclarations=53,independentUniqueMainSourceFiles=25,
          catalogNegatives=9,mapperNegatives=8,neighbourInvariance=17,snapshotNegatives=6,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1929_G13Bootstrap17_主関連責任結果.md'],
        tokenMeasurementIds=['3f2e8832b3b776338d666e9bcae62cb80b642784defd07292019d612c7d67bc8'],
        nextCommand='9516 publicdelta/save-push; fresh current-window remaining>10 then remaining62 source responsibilities or independent ordinary PGPT'),[
        ('PG9506-bootstrap17-source-metadata-v1/manifest.json','149b4cd28bab67a5d02b1e1aa7eb7dee3b7313320b87cc1e68c631ba9f5c3a64'),
        ('PG9508-bootstrap17-source-post-v1/manifest.json','4ea772b5dee1158fb6290b8bdeb422379651edd67ff4377c589bdef39e922445'),
        ('PG9510-bootstrap17-source-join-v1/manifest.json','7f314d491c7ff05eabf7464cd3f42efb313cfbb5e8c499b5c49b316f77f3c650'),
        ('PG9512-bootstrap17-snapshot-post-v1/manifest.json','550662efea7b79d548d233022130e91846c903fcb8afedba3d96c596ce36c41c')])
