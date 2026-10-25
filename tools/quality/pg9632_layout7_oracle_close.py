"""Save static Layout7 links and explicit tool rework, with no product PT credit."""
from pathlib import Path
import trace_group_close as close

if __name__ == '__main__':
    close.run(Path(__file__), 'G13_LAYOUT_CATALOG7_ORACLE_REVIEW_V1', close.BASE / 'PG9632-layout7-oracle-metrics-v1',
      close.BASE / 'PG9634-layout7-oracle-public-delta-v1', '515178611958f4643d4f5f466436bcac36a6ee4d', dict(
        groupStartEstimatePp=dict(low=.5, base=3, high=8), groupCapPp=10,
        quotaBefore=dict(usedPercent=6, remainingPercent=94, resetsAt=1793513544),
        quotaAfter=dict(usedPercent=7, remainingPercent=93, resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T09:31:14Z', quotaAfterObservedAtUTC='2026-10-25T09:46:51Z',
        sameQuotaWindow=True, observedSharedPp=1,
        attemptResult='7_METHODS_6_EXISTING_FAMILIES_11_RELATIONS_STATIC_64_LAYOUTS_389_FIELDS_NO_PRODUCT_PT',
        originalPlanEngineeringDelta=dict(item='CURRENT_LAYOUT_METHOD_TESTID_ORACLE_TRACE', wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=['BUG-1753'], ykt=['YKT-1504']),
        sourceReauthentication=dict(currentNormalSnapshotHashesExact=True, oldDynamicResultsTransferred=False,
            reusedPureFixtureProofOnly=True, referenceAdditionalBudgetPp=0, filePrimaryOwnersReassigned=False),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=2, independentPostAttempts=2,
            scanPreflightConstructionFailures=2, targetCompile=0, targetRuntimeInvocation=0, exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=0, sourceRows=956, javaPaths=1789,
            registered=1781, unregisteredTest=8, staticMethodOracleRelations=7, existingDistinctTestIdFamilies=6,
            methodTestIdRelations=11, currentRegistryLiteralTuples=64, currentFieldLiteralRows=389,
            relationCounterexamples=2, previousMatricesRecounted=2, productTestsExecuted=0,
            newTestIds=0, newMain=0, coverage=None, formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1957_G13LayoutCatalog7_意味対応結果・工具是正.md'],
        tokenMeasurementIds=['b76b3af010fff9c157866abd10b82ea38f88c5ce18ae979d3960ec1d65c6367e'],
        nextCommand='9634 publicdelta/save-push; next necessary ordinary PT or permitted independent PGPT'), [
        ('PG9628-layout7-oracle-trace-v2/manifest.json', 'd494ae30c275cca595f8df366176ddb05276f64d37d47289683b6e95e56ff2db'),
        ('PG9630-layout7-oracle-post-v1/manifest.json', '981969b50240efaa0f2b7378362c7b80c490ed2aa0e747c8eff21573312a665f')])
