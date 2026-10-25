"""New10 selected-method success, whole-Life incomplete; original90 and exact unclassified rows kept."""
import hashlib
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9204-api-main-observation-metrics-v1'
GROUP='P01805_API_MAIN_OBSERVATION_WIRING_V1'
SOURCE='9f7a3215621dca09184ea24d0ba824b3a002b329'

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row['eventType']=='GROUP_END' for row in events)
    proof=bind([
      (BASE/'PG9200-api-main-observation-measure-v1/manifest.json','a38ab05005ceed0609a20589c476e72b17c37a82a51fef3ceecc132ba680dfea'),
      (BASE/'PG9202-api-main-observation-trace-v1/manifest.json','646a8d8e05a439b85c56b80f323529a8366f2adbd897ed8b2849a0fd731c696d')],SOURCE)
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert digest(inventory['artifacts'])=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert digest(inventory['currentPhysicalCandidate'])=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    assert inventory['currentIncrementalHostOwnership']['source']==SOURCE and inventory['currentIncrementalHostOwnership']['sourceRows']==251
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(
      primaryWbs='WBS-P018-05',wbsLeafIds=['WBS-P018-05'],source=SOURCE,
      sourceBefore='6c271f74da3e09cbcf52e6c2abf5dd27fe93acd5',workCategory='IMPLEMENTATION',
      groupStartEstimatePp=dict(low=1,base=2,high=3),groupCapPp=3,
      quotaBefore=dict(usedPercent=58,remainingPercent=42,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=59,remainingPercent=41,resetsAt=1793382075),
      quotaAfterObservedAtUTC='2026-10-25T00:56:14+00:00',sameQuotaWindow=True,observedSharedPp=1,
      original90Preservation=dict(originalBaselineUsed=0,originalBaselineReset=1793306748,cap=90,
        capturedLowerBoundPp=84,previousCapturedLowerBound=83,sameWindowEndpoint58To59Pp=1,
        unknownIntervalPp=2,cumulativeExactPp=None,newLargeGroupsSuppressed=True,rebased=False),
      attemptResult='NEW8_F0_E0_S0; WHOLE_MAIN_12of176_4of34_1of1_0of18_NOT100; CS_SB0_RAW_PMD2_CONTEXT_REVIEW2; ACTUAL_HOLD',
      technicalMeasurementDelta=dict(newTestIds=8,necessaryRegressionTests=0,currentSourceSelectedTests=8,newMain=0,
        changedSourceUnits=1,changedPhysicalClasses=1,physicalMain=1843,sourceOwners=251,
        wholeSourceUnitCounters=dict(LINE=dict(covered=12,missed=164),METHOD=dict(covered=4,missed=30),
          CLASS=dict(covered=1,missed=0),BRANCH=dict(covered=0,missed=18)),
        requiredWholeClassFour100=False,programPtComplete=False,rawPmd=2,reviewedPmd=2,unclassifiedPmd=0,
        checkstyleFindings=0,spotbugsFindings=0,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='MAIN_HELD_ASSEMBLY_EXISTING_LIFE_REMAINING_SUPPLY',componentOnly=True,mainFactoryWired=True,wholeProgramAccepted=False),
      additionalDiscoveries=dict(bugs=[],ykt=[]),
      productRework=dict(normalSources=1,normalFailures=0,selectedSources=1,totalSelectedExecutions=8),
      toolConstructionAndEnvironmentRework=dict(jsPatchSyntaxBeforeChild=1,childNotStarted=True,productTestsRerun=0,exclusivePp=None),
      relatedWbs='WBS-P018-09',componentAdditionalBudgetPp=0,
      sourceProofs=proof,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1875_APIMainObservation_限定実行結果・残依存.md'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,
      tokenMeasurementIds=['e7732992fc8b2f92496d18406e058c3f9c780e9f75ba9f3a8306e237ffbe5ec1'],
      pgptAllComplete=False,stopReason=None,
      nextCommand='9206 public delta/commit-push; bounded positive fake-port factory producer/cache/SDK supply; actual operations HOLD'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,
          logical941AndHistorical943Unchanged=True,programPtComplete=False,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,sourceRows=251,programPtComplete=False)))

if __name__=='__main__':main()
