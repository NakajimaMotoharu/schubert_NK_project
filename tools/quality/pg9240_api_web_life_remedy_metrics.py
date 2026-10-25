"""New10 selected-method success, whole-Life incomplete; original90 and exact unclassified rows kept."""
import hashlib
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9240-api-web-life-remedy-metrics-v1'
GROUP='P01805_API_WEB_LIFE_STATIC_REMEDY_V1'
SOURCE='600b966bab415690bf09d24ba07268a097b19d18'

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row['eventType']=='GROUP_END' for row in events)
    proof=bind([
      (BASE/'PG9236-api-web-life-remedy-measure-v1/manifest.json','a1e56672716122f40a25ef77764daec7e594195e5689de48ee9dabed01248b99'),
      (BASE/'PG9238-api-web-life-remedy-trace-v1/manifest.json','f026b8e6aec316d2408089cafe71910970943c4a8b3ec493c3528541bf0f530c')],SOURCE)
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert digest(inventory['artifacts'])=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert digest(inventory['currentPhysicalCandidate'])=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    assert inventory['currentIncrementalHostOwnership']['source']==SOURCE and inventory['currentIncrementalHostOwnership']['sourceRows']==254
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(
      primaryWbs='WBS-P018-05',wbsLeafIds=['WBS-P018-05'],source=SOURCE,
      sourceBefore='3641d0f49e6b33fe64de718703f134406dfddb30',workCategory='IMPLEMENTATION',
      groupStartEstimatePp=dict(low=.5,base=1,high=2),groupCapPp=2,
      quotaBefore=dict(usedPercent=59,remainingPercent=41,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=60,remainingPercent=40,resetsAt=1793382075),
      quotaAfterObservedAtUTC='2026-10-25T01:17:00+00:00',sameQuotaWindow=True,observedSharedPp=1,
      original90Preservation=dict(originalBaselineUsed=0,originalBaselineReset=1793306748,cap=90,
        capturedLowerBoundPp=85,previousCapturedLowerBound=84,sameWindowEndpoint59To60Pp=1,
        unknownIntervalPp=2,cumulativeExactPp=None,newLargeGroupsSuppressed=True,rebased=False),
      attemptResult='NEW3_PLUS_IMPACT11_F0_E0_S0; TARGETED_STATIC_REMEDY_CONFIRMED; RAW_PMD18_PENDING; WHOLE_PROGRAM_NOT100_HOLD',
      technicalMeasurementDelta=dict(newTestIds=3,necessaryRegressionTests=11,currentSourceSelectedTests=14,currentSuites=3,newMain=0,
        changedSourceUnits=2,changedPhysicalClasses=2,physicalMain=1843,sourceOwners=254,
        wholeSourceUnitCounters=dict(LINE=dict(covered=66,missed=59),METHOD=dict(covered=16,missed=13),
          CLASS=dict(covered=2,missed=1),BRANCH=dict(covered=14,missed=14)),
        requiredWholeClassFour100=False,programPtComplete=False,rawPmd=18,unclassifiedPmd=18,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='API_ATOMIC_RELEASE_AND_API_WEB_TERMINAL_CLOSE_CONTROL_FLOW',componentOnly=True,wholeProgramAccepted=False),
      additionalDiscoveries=dict(bugs=['BUG-1742'],ykt=['YKT-1493'],staticTargetsRemedied=3,
        yktOpenAdditionalWebInterruptedEmpty=1,remainingWebPrivateSynchronized=2),
      productRework=dict(normalSources=1,normalFailures=0,selectedSources=1,totalSelectedExecutions=14),
      technicalEstimateCorrection=dict(sourceUnitClasses=3,changedPhysicalClasses=2,anonymousInnerUnchanged=True,newScope=False),
      toolConstructionAndEnvironmentRework=dict(productTestsRerunForConfirmation=0,exclusivePp=None),
      relatedWbs='WBS-P018-09',componentAdditionalBudgetPp=0,
      sourceProofs=proof,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1881_APIWebLifeStatic_限定是正結果・残指摘.md'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,
      tokenMeasurementIds=['6ad8e7064cc44bdfd0f735d326d63f98be20a185d85d63749e893b8268750454'],
      pgptAllComplete=False,stopReason=None,
      nextCommand='9242 public delta/commit-push; bounded Web private lock/interrupted interval representation within original90; actual operations HOLD'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,
          logical941AndHistorical943Unchanged=True,programPtComplete=False,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,sourceRows=254,programPtComplete=False)))

if __name__=='__main__':main()
