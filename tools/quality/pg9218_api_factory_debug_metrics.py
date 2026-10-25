"""New10 selected-method success, whole-Life incomplete; original90 and exact unclassified rows kept."""
import hashlib
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9218-api-factory-debug-metrics-v1'
GROUP='P01805_API_FACTORY_DEBUG_FAKE_SUPPLY_V1'
SOURCE='3641d0f49e6b33fe64de718703f134406dfddb30'

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row['eventType']=='GROUP_END' for row in events)
    proof=bind([
      (BASE/'PG9214-api-factory-debug-measure-v2/manifest.json','f506719d825662d5e88b233a68c859a3ae69da983334df83166143980e4ed237'),
      (BASE/'PG9216-api-factory-debug-trace-v1/manifest.json','4fa9a883c89bdef6165bbcf14628b4637736de1a4a5244741f25f7f5b338a77b')],SOURCE)
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert digest(inventory['artifacts'])=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert digest(inventory['currentPhysicalCandidate'])=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    assert inventory['currentIncrementalHostOwnership']['source']==SOURCE and inventory['currentIncrementalHostOwnership']['sourceRows']==252
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(
      primaryWbs='WBS-P018-05',wbsLeafIds=['WBS-P018-05'],source=SOURCE,
      sourceBefore='9f7a3215621dca09184ea24d0ba824b3a002b329',workCategory='IMPLEMENTATION',
      groupStartEstimatePp=dict(low=.5,base=1,high=2),groupCapPp=2,
      quotaBefore=dict(usedPercent=59,remainingPercent=41,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=59,remainingPercent=41,resetsAt=1793382075),
      quotaAfterObservedAtUTC='2026-10-25T01:04:17+00:00',sameQuotaWindow=True,observedSharedPp=0,
      original90Preservation=dict(originalBaselineUsed=0,originalBaselineReset=1793306748,cap=90,
        capturedLowerBoundPp=84,previousCapturedLowerBound=84,sameWindowEndpoint59To59Pp=0,
        unknownIntervalPp=2,cumulativeExactPp=None,newLargeGroupsSuppressed=True,rebased=False),
      attemptResult='NEW1_F0_E0_S0; FACTORY_DEBUG_FAKE_SUPPLY_RELEASE; MAIN_ALL1843_BYTES_UNCHANGED; WHOLE_MAIN_NOT100; ACTUAL_HOLD',
      technicalMeasurementDelta=dict(newTestIds=1,necessaryRegressionTests=0,currentSourceSelectedTests=1,newMain=0,
        changedSourceUnits=0,changedPhysicalClasses=0,physicalMain=1843,sourceOwners=252,
        wholeSourceUnitCounters=dict(LINE=dict(covered=14,missed=162),METHOD=dict(covered=6,missed=28),
          CLASS=dict(covered=1,missed=0),BRANCH=dict(covered=0,missed=18)),
        requiredWholeClassFour100=False,programPtComplete=False,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='MAIN_FACTORY_POSITIVE_DEBUG_FAKE_SUPPLY_AND_LIFE_RELEASE',componentOnly=True,wholeProgramAccepted=False),
      additionalDiscoveries=dict(bugs=['BUG-1741'],ykt=['YKT-1492'],toolScopeClosed=True),
      productRework=dict(normalSources=1,normalFailures=0,selectedSources=1,totalSelectedExecutions=1),
      toolConstructionAndEnvironmentRework=dict(oldSessionReaderRejected=1,newV2ReaderQualified=True,wrongOldSessionNegative=1,
        guessedLegacyHelperDiagnostic=1,productTestsRerun=0,exclusivePp=None),
      relatedWbs='WBS-P018-09',componentAdditionalBudgetPp=0,
      sourceProofs=proof,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1877_APIFactoryDebug_限定実行結果・残依存.md'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,
      tokenMeasurementIds=['3c5c375308f1af02fc96c25a464da24eb0fec768f71377e93cff7cd3ca241583'],
      pgptAllComplete=False,stopReason=None,
      nextCommand='9220 public delta/commit-push; bounded Life legacy2 individual contract review within original90; actual operations HOLD'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,
          logical941AndHistorical943Unchanged=True,programPtComplete=False,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,sourceRows=252,programPtComplete=False)))

if __name__=='__main__':main()
