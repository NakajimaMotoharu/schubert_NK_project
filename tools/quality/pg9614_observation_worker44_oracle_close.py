"""Save44 static oracle relations separately from old44 dynamic PT and all formal acceptance."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_OBSERVATION_WORKER44_ORACLE_REVIEW_V1',close.BASE/'PG9614-observation-worker44-oracle-metrics-v1',
      close.BASE/'PG9616-observation-worker44-oracle-public-delta-v1','35d37b18b3b51f8ed6cb6715d218baa71dfd9d5c',dict(
        groupStartEstimatePp=dict(low=.5,base=3,high=8),groupCapPp=10,
        quotaBefore=dict(usedPercent=5,remainingPercent=95,resetsAt=1793513544),quotaAfter=dict(usedPercent=5,remainingPercent=95,resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T08:52:17Z',quotaAfterObservedAtUTC='2026-10-25T09:02:43Z',sameQuotaWindow=True,observedSharedPp=0,
        attemptResult='44_EXISTING_METHOD_SPEC_ORACLE_STATIC_SEMANTIC_RELATIONS_RECORDED_NOT_DYNAMIC_PT_859_CANDIDATE_SUBSET',
        originalPlanEngineeringDelta=dict(item='INITIAL_CURRENT_METHOD_TESTID_INDEPENDENT_ORACLE_TRACE_REVIEW',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[],ykt=[]),sourceReauthentication=dict(currentNormalSnapshotHashesExact=True,oldDynamicResultsTransferred=False,
          artifactOwner='WBS-P018-09',referenceAdditionalBudgetPp=0,filePrimaryOwnersReassigned=False),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1,independentPostAttempts=1,targetCompile=0,targetRuntimeInvocation=0,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=0,sourceRows=956,javaPaths=1789,registered=1781,unregisteredTest=8,
          staticMethodOracleRelations=44,parentSemanticReviewOnly=True,independentPostReferencesBytesBoundariesOnly=True,
          uniqueExistingSpecRowCandidateUniverse=859,reviewIsSubsetNotAdditive=True,metadataCounterexamples=10,literalArithmeticVectors=1,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1951_G13ObservationWorker44_意味対応結果・残条件.md'],
        tokenMeasurementIds=['5850701dc9b84a0f461cb8892c48088fff095bfa4c7b87e7b01ce79147a8a51e'],
        nextCommand='9616 publicdelta/save-push; non-token method existing explicit oracle references or other permitted PGPT'),[
        ('PG9610-observation-worker44-oracle-trace-v1/manifest.json','e2d953b07c08be7c455724b1b1d001fd0e45ef8819a2525a15eb6c6002f6e286'),
        ('PG9612-observation-worker44-oracle-post-v1/manifest.json','d3931ca36d55abaf7e3dd493699edfd0e0cf85d9996546ed3f277b0c78fe99c4')])
