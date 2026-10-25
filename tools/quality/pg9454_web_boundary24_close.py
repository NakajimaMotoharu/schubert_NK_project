"""Close Web boundary24 source trace, not authentication/session/runtime PT acceptance."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_WEB_BOUNDARY24_SOURCE_V1',close.BASE/'PG9454-web-boundary24-metrics-v1',
      close.BASE/'PG9456-web-boundary24-public-delta-v1','692dc1e076886ea63a265be73d7df384762d2746',dict(
        groupStartEstimatePp=dict(low=.5,base=2,high=6),groupCapPp=10,
        quotaBefore=dict(usedPercent=67,remainingPercent=33,resetsAt=1793382075),quotaAfter=dict(usedPercent=67,remainingPercent=33,resetsAt=1793382075),
        quotaBeforeObservedAtUTC='2026-10-25T05:54:10Z',quotaAfterObservedAtUTC='2026-10-25T06:00:44Z',sameQuotaWindow=True,observedSharedPp=0,
        attemptResult='24_EXACT_WEB_BOUNDARY_SESSION_SECURITY_RUNTIME_SOURCE_PRIMARY_RELATED_SCOPES_REGISTERED_NOT_PT; REMAIN179',
        originalPlanEngineeringDelta=dict(item='EXACT_WEB_BOUNDARY24_PRIMARY_SOURCE_RESPONSIBILITIES',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[],ykt=[],sessionPackageNotAutomaticSingleOwner=True),
        sourceReauthentication=dict(old761CanonicalRelatedRuntimeArtifactFieldsPreserved=True,oldSourceResultsTransferred=False,currentNormalSnapshotHashesExact=True),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1,producerRetries=0,targetCompile=0,targetRuntimeInvocation=0,sourceSelectionVectors=5,
          explicitWebModuleMutationVectors=2,diagnosticNamespaceSplitFailure=1,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=24,sourceRows=785,javaPaths=1789,registered=1610,registeredMain=965,totalMain=965,
          registeredTest=645,totalTest=824,unregisteredTest=179,remainingMultiOwner=161,remainingNoMainCp=18,
          verifiedSourceClosure=30,independentTestClassDeclarations=127,independentMainClassDeclarations=122,independentUniqueMainSourceFiles=104,
          catalogNegatives=9,mapperNegatives=8,neighbourInvariance=24,snapshotNegatives=6,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1919_G13WebBoundary24_主関連責任結果.md'],
        tokenMeasurementIds=['1562435752a8a69947b141e5bdbeffd860c52845a486c0cc73709ececb248bda'],
        nextCommand='9456 public scan/save-push; remaining179 business composite/shared fixture source responsibilities then independent PG/PT'),[
        ('PG9446-web-boundary24-source-metadata-v1/manifest.json','5b5a5f49cf35b72e83c90e0a339c9bd6598688ad543bfae52628c2cbd440892d'),
        ('PG9448-web-boundary24-source-post-v1/manifest.json','4668707b55bbc9eb99e307f3f99583c3736785e2614f7ef3c1b4f3bd4ca2d914'),
        ('PG9450-web-boundary24-source-join-v1/manifest.json','170288a0dc7c8b2ebecd8bd42c397bdfdc274f30057c8c2c7dc850063afe5818'),
        ('PG9452-web-boundary24-snapshot-post-v1/manifest.json','d793c435675add6a46295f1126b2a465b28b9965e77e5e3a18948ee1194db814')])
