"""Save static semantic relations, then continue to newly specified ordinary pagination PT."""
from pathlib import Path
import trace_group_close as close

if __name__ == '__main__':
    close.run(Path(__file__), 'G13_SEMANTIC8_ORACLE_REVIEW_V1', close.BASE / 'PG9656-semantic8-metrics-v1',
      close.BASE / 'PG9658-semantic8-public-delta-v1', 'ffb682550887e26f1870ecc355c449843d2237cd', dict(
        groupStartEstimatePp=dict(low=.5, base=3, high=8), groupCapPp=10,
        quotaBefore=dict(usedPercent=7, remainingPercent=93, resetsAt=1793513544),
        quotaAfter=dict(usedPercent=7, remainingPercent=93, resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T10:05:00Z', quotaAfterObservedAtUTC='2026-10-25T10:11:28Z',
        sameQuotaWindow=True, observedSharedPp=0,
        attemptResult='8_SEMANTIC_METHODS_1_EXISTING_FAMILY_8_RELATIONS_NEXT_DEDICATED_ORDINARY_PAGE_BOUNDARIES',
        originalPlanEngineeringDelta=dict(item='CURRENT_BUSINESS_SEMANTIC_METHOD_ORACLE_TRACE', wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[], ykt=[], dedicatedPaginationVectorsPlanned=True),
        sourceReauthentication=dict(currentNormalSnapshotHashesExact=True, oldDynamicResultsTransferred=False,
            referenceAdditionalBudgetPp=0, filePrimaryOwnersReassigned=False),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1, targetCompile=0, targetRuntimeInvocation=0, exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=0, sourceRows=956, javaPaths=1789,
            registered=1781, unregisteredTest=8, staticMethodOracleRelations=8, existingDistinctTestIdFamilies=1,
            methodTestIdRelations=8, currentMainSourceFiles=3, cumulativeSeriesUniqueReviewedMethods=95,
            ordinaryTestDeclarationDenominator=5622, seriesUnreviewedDeclarations=5527,
            namedConstructorVsValidatorAttributionUnproved=True, productTestsExecuted=0, newTestIds=0, newMain=0,
            coverage=None, formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1968_G13Semantic8_静的対応結果・次通常PT.md'],
        tokenMeasurementIds=['c14cae839d6c885eb212014832fbfbb3150f8ec99bd24814da5e9cfd2fb3f12f'],
        nextCommand='9658 save/push; freeze new ordinary page2/max-page/arithmetic PT with independent literal expectations'), [
        ('PG9654-semantic8-oracle-trace-v1/manifest.json', '2de49df9d1d03e38039994868dae5e105d4abc1d6ffe89014569657ecd136376')])
