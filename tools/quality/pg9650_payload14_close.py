"""Save static payload links and pure fixture reauthentication, never old dynamic results."""
from pathlib import Path
import trace_group_close as close

if __name__ == '__main__':
    close.run(Path(__file__), 'G13_PAYLOAD14_ORACLE_REVIEW_V1', close.BASE / 'PG9650-payload14-metrics-v1',
      close.BASE / 'PG9652-payload14-public-delta-v1', '2a139d5effc7d3c894372bad02270fc8b7a93d32', dict(
        groupStartEstimatePp=dict(low=.5, base=3, high=8), groupCapPp=10,
        quotaBefore=dict(usedPercent=7, remainingPercent=93, resetsAt=1793513544),
        quotaAfter=dict(usedPercent=7, remainingPercent=93, resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T09:58:54Z', quotaAfterObservedAtUTC='2026-10-25T10:02:38Z',
        sameQuotaWindow=True, observedSharedPp=0,
        attemptResult='14_PAYLOAD_METHODS_11_EXISTING_FAMILIES_15_RELATIONS_PRIOR_PURE_GOLDEN_BYTES_SAME_NO_PRODUCT_PT',
        originalPlanEngineeringDelta=dict(item='CURRENT_PAYLOAD_METHOD_ORACLE_TRACE', wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[], ykt=[]),
        sourceReauthentication=dict(currentNormalSnapshotHashesExact=True, oldDynamicResultsTransferred=False,
            reusedPureGoldenProofOnly=True, referenceAdditionalBudgetPp=0, filePrimaryOwnersReassigned=False),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1, commonMetadataBinderAdded=True,
            targetCompile=0, targetRuntimeInvocation=0, exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=0, sourceRows=956, javaPaths=1789,
            registered=1781, unregisteredTest=8, staticMethodOracleRelations=14, existingDistinctTestIdFamilies=11,
            methodTestIdRelations=15, currentMainSourceFiles=7, reusedPureGoldenDigests=287,
            cumulativeSeriesUniqueReviewedMethods=87, ordinaryTestDeclarationDenominator=5622,
            seriesUnreviewedDeclarations=5535, productTestsExecuted=0, newTestIds=0, newMain=0, coverage=None, formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1965_G13Payload14_静的対応結果・純粋根拠再利用.md'],
        tokenMeasurementIds=['e762bbf6b9597260bee135fe4bcefffa1f88af52544d89c6912ecfdaeee2eceb'],
        nextCommand='9652 save/push; next semantic/typed independent oracle or necessary permitted PGPT'), [
        ('PG9648-payload14-oracle-trace-v1/manifest.json', '397f5b4d515fc3b3f9601950439ce9804d2fd443ecf97e315f1a4e4d1139f2e7')])
