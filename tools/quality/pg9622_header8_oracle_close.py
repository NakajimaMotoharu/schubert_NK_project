"""Save eight static non-token oracle links without borrowing old PT/coverage or family completion."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_HEADER8_ORACLE_REVIEW_V1',close.BASE/'PG9622-header8-oracle-metrics-v1',
      close.BASE/'PG9624-header8-oracle-public-delta-v1','2bf3c9502c863e3a4088fda68dcd90a0690d7154',dict(
        groupStartEstimatePp=dict(low=.5,base=2,high=6),groupCapPp=10,
        quotaBefore=dict(usedPercent=6,remainingPercent=94,resetsAt=1793513544),quotaAfter=dict(usedPercent=6,remainingPercent=94,resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T09:11:08Z',quotaAfterObservedAtUTC='2026-10-25T09:22:25Z',sameQuotaWindow=True,observedSharedPp=0,
        attemptResult='8_NON_TOKEN_METHODS_TO_6_EXISTING_TESTID_FAMILIES_9_RELATIONS_STATIC_GOLDEN17_FIELDS_NO_PRODUCT_EXECUTION',
        originalPlanEngineeringDelta=dict(item='CURRENT_NON_TOKEN_METHOD_TESTID_ORACLE_TRACE',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[],ykt=[]),sourceReauthentication=dict(currentNormalSnapshotHashesExact=True,oldDynamicResultsTransferred=False,
          canonicalDesign='origin/main@8b91944df5820535e23ba2469740f1c0aa94c447',referenceAdditionalBudgetPp=0,filePrimaryOwnersReassigned=False),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1,independentPostAttempts=1,targetCompile=0,targetRuntimeInvocation=0,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=0,sourceRows=956,javaPaths=1789,registered=1781,unregisteredTest=8,
          staticMethodOracleRelations=8,existingDistinctTestIdFamilies=6,methodTestIdRelations=9,canonicalUiFields=17,testBuilderAssignments=13,
          currentMainClassProofs=6,literalArithmeticVectors=3,metadataCounterexamples=10,wholeQseOrLayoutsQualified=False,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1954_G13Header8_意味対応結果・残条件.md'],
        tokenMeasurementIds=['eb730d417098ba9208def5951ba3726d24f3170f03032a7403386c8d58b50c1e'],
        nextCommand='9624 publicdelta/save-push; next existing explicit method/oracle or other permitted PGPT'),[
        ('PG9618-header8-oracle-trace-v1/manifest.json','31cd0d1ea0ae26cd364fae679de4093304d305bc69e001c1254c8af31b175317'),
        ('PG9620-header8-oracle-post-v1/manifest.json','d157c26bb144f4de03759abeef42131f19e49142e1926d6a452620a7b8d5708d')])
