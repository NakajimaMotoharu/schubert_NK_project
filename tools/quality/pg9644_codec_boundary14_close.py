"""Save actual static codec oracle relations; no dynamic PASS or family completion credit."""
from pathlib import Path
import trace_group_close as close

if __name__ == '__main__':
    close.run(Path(__file__), 'G13_CODEC_BOUNDARY14_ORACLE_REVIEW_V1', close.BASE / 'PG9644-codec-boundary14-metrics-v1',
      close.BASE / 'PG9646-codec-boundary14-public-delta-v1', '1f2f819ac385e98dce042577590a6dc85c00d28c', dict(
        groupStartEstimatePp=dict(low=.5, base=3, high=8), groupCapPp=10,
        quotaBefore=dict(usedPercent=7, remainingPercent=93, resetsAt=1793513544),
        quotaAfter=dict(usedPercent=7, remainingPercent=93, resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T09:53:05Z', quotaAfterObservedAtUTC='2026-10-25T09:57:46Z',
        sameQuotaWindow=True, observedSharedPp=0,
        attemptResult='14_METHODS_13_EXISTING_FAMILIES_19_RELATIONS_STATIC_SCENARIO_GOLDEN4800_NO_PRODUCT_EXECUTION',
        originalPlanEngineeringDelta=dict(item='CURRENT_CODEC_BOUNDARY_METHOD_ORACLE_TRACE', wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[], ykt=[], unprovedScopeExplicit=True),
        sourceReauthentication=dict(currentNormalSnapshotHashesExact=True, oldDynamicResultsTransferred=False,
            referenceAdditionalBudgetPp=0, filePrimaryOwnersReassigned=False),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1, targetCompile=0, targetRuntimeInvocation=0,
            nonOracleProseTypoCorrectedByAppendix=True, exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=0, sourceRows=956, javaPaths=1789,
            registered=1781, unregisteredTest=8, staticMethodOracleRelations=14, existingDistinctTestIdFamilies=13,
            methodTestIdRelations=19, currentMainSourceFiles=11, scenarioGoldenFields=10, scenarioGoldenBytes=4800,
            testBuilderAssignments=6, productTestsExecuted=0, newTestIds=0, newMain=0, coverage=None, formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1962_G13CodecBoundary14_静的対応結果・残条件.md'],
        tokenMeasurementIds=['935fba4d00494de02a89efe7c72ea0c0d7ee1ff2c738b9525a3d095a40ebcf7b'],
        nextCommand='9646 save/push; next payload/typed existing independent oracle or necessary ordinary PGPT'), [
        ('PG9642-codec-boundary14-oracle-trace-v1/manifest.json', 'aea6d62dea46ccd1d80e6116aba2cf65df58ee278855def4107bccca701fbed3')])
