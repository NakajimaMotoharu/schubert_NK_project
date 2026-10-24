"""Pure API stop-budget18, necessary qualification and CLI/count tool repair; original90 preserved."""
import hashlib
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9176-api-stop-budget-metrics-v1'
GROUP='P01805_API_STOP_BUDGET_V1'
SOURCE='ecfcbf9f6ab81f77301833eda3fba464c72eb4b5'

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row['eventType']=='GROUP_END' for row in events)
    proof=bind([
      (BASE/'PG9172-api-stop-budget-post-v1/manifest.json','cf2f8da6e5bf93466eb2e96ad47aaf3ffb70998d5310461e8d2332e4f10d284c'),
      (BASE/'PG9174-api-stop-budget-trace-v2/manifest.json','ebdbb14650b1dca164daf224cd21e503deef005a21946c2876dcfcc82c4c7932')],SOURCE)
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert digest(inventory['artifacts'])=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert digest(inventory['currentPhysicalCandidate'])=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    assert inventory['currentIncrementalHostOwnership']['source']==SOURCE and inventory['currentIncrementalHostOwnership']['sourceRows']==248
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(
      primaryWbs='WBS-P018-05',wbsLeafIds=['WBS-P018-05'],source=SOURCE,
      sourceBefore='cb91bc2ec0ef5a36652369aff5c86fa037801cca',workCategory='IMPLEMENTATION',
      groupStartEstimatePp=dict(low=3,base=5,high=9),groupCapPp=10,
      quotaBefore=dict(usedPercent=57,remainingPercent=43,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=57,remainingPercent=43,resetsAt=1793382075),
      quotaAfterObservedAtUTC='2026-10-24T23:37:08+00:00',sameQuotaWindow=True,observedSharedPp=0,roundedZeroNotExclusiveZero=True,
      original90Preservation=dict(originalBaselineUsed=0,originalBaselineReset=1793306748,cap=90,
        capturedLowerBoundPp=82,unknownIntervalPp=2,cumulativeExactPp=None,
        basis='PMO/hourly-monitor/budget-preservation-80-20261025-0826.json; fresh57 unchanged same-window endpoint',
        newLargeGroupsSuppressed=True,nextStagesShortNecessaryOrPreservationOnly=True,rebased=False),
      attemptResult='CURRENT18_F0_E0_S0; WHOLE_ONE_MAIN_FOUR100; CS_SB0; RAW_PMD2_INDIVIDUAL_PRIVATE_LOCK; ACTUAL_CALLER_UNSUPPLIED_HOLD',
      technicalMeasurementDelta=dict(newTestIds=18,necessaryRegressionTests=0,currentSourceSelectedTests=18,newMain=1,
        physicalMain=1843,sourceOwners=248,scopedCoverage=dict(LINE=24,METHOD=5,CLASS=1,BRANCH=12,missed=0),
        rawPmd=2,reviewedPmd=2,unclassified=0,checkstyleFindings=0,spotbugsFindings=0,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='API_FIRST_STOP_MONOTONIC_BUDGET_NONRENEWING',componentOnly=True,actualCallerConnected=False),
      additionalDiscoveries=dict(bugs=['BUG-1739'],ykt=['YKT-1490'],limitedScopeClosed=True),
      productExecutions=dict(normalSources=1,selectedSources=1,totalSelectedExecutions=18,incrementalTestIdsOnly=18,oldSuccessConfirmationReplays=0),
      toolRepair=dict(rawPmdCount2AndCliExit4Separated=True,originalUnqualifiedFilesImmutable=True,
        originalTraceFailedBeforeChild=True,currentTraceMetadataNegatives=17,productTestsRerun=0),
      canonicalOwnership=dict(old246MappingsUnchanged=True,newTwoExactPaths='WBS-P018-05',logical941AndHistorical943Unchanged=True,historicalCostReassignment=False),
      relatedWbs='WBS-P018-09',componentAdditionalBudgetPp=0,
      sourceProofs=proof,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1871_APIStopBudget_実行結果・残依存.md'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,
      tokenMeasurementIds=['81dbf1dd49c1b7710b873c81fa68177c1c1061a31a417549e651a569887ba926'],
      pgptAllComplete=False,stopReason=None,nextCommand='9178 public delta/commit-push; short necessary lifetime first-stop remaining supply PG/PT, actual Main/native HOLD'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,
          logical941AndHistorical943Unchanged=True,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,sourceRows=248)))

if __name__=='__main__':main()
