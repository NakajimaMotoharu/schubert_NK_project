"""New10 selected-method success, whole-Life incomplete; original90 and exact unclassified rows kept."""
import hashlib
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9190-api-lifetime-budget-metrics-v1'
GROUP='P01805_API_LIFETIME_STOP_BUDGET_V1'
SOURCE='6c271f74da3e09cbcf52e6c2abf5dd27fe93acd5'

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row['eventType']=='GROUP_END' for row in events)
    proof=bind([
      (BASE/'PG9186-api-lifetime-budget-measure-v1/manifest.json','d852e44b73825938e8cc6460707475ea75b4831cd7d22d8ba960848a3d0683c5'),
      (BASE/'PG9188-api-lifetime-budget-trace-v1/manifest.json','40935dee125b947b1e53b7b313b0d3f2accf3f1add25be384d842e0e0a4cb75a')],SOURCE)
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert digest(inventory['artifacts'])=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert digest(inventory['currentPhysicalCandidate'])=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    assert inventory['currentIncrementalHostOwnership']['source']==SOURCE and inventory['currentIncrementalHostOwnership']['sourceRows']==250
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(
      primaryWbs='WBS-P018-05',wbsLeafIds=['WBS-P018-05'],source=SOURCE,
      sourceBefore='ecfcbf9f6ab81f77301833eda3fba464c72eb4b5',workCategory='IMPLEMENTATION',
      groupStartEstimatePp=dict(low=0.5,base=2,high=3),groupCapPp=3,
      quotaBefore=dict(usedPercent=57,remainingPercent=43,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=58,remainingPercent=42,resetsAt=1793382075),
      quotaAfterObservedAtUTC='2026-10-25T00:03:04+00:00',sameQuotaWindow=True,observedSharedPp=1,
      original90Preservation=dict(originalBaselineUsed=0,originalBaselineReset=1793306748,cap=90,
        capturedLowerBoundPp=83,previousCapturedLowerBound=82,sameWindowEndpoint57To58Pp=1,
        unknownIntervalPp=2,cumulativeExactPp=None,newLargeGroupsSuppressed=True,rebased=False),
      attemptResult='NEW10_F0_E0_S0; WHOLE_LIFE_TWO_CLASS_35of67_9of19_1of2_8of14_NOT100; CS_SB0_RAW_PMD9_REVIEW7_PENDING2; ACTUAL_HOLD',
      technicalMeasurementDelta=dict(newTestIds=10,necessaryRegressionTests=0,currentSourceSelectedTests=10,newMain=0,
        changedSourceUnits=1,changedPhysicalClasses=2,physicalMain=1843,sourceOwners=250,
        wholeSourceUnitCounters=dict(LINE=dict(covered=35,missed=32),METHOD=dict(covered=9,missed=10),
          CLASS=dict(covered=1,missed=1),BRANCH=dict(covered=8,missed=6)),
        requiredWholeClassFour100=False,programPtComplete=False,rawPmd=9,reviewedPmd=7,unclassifiedPmd=2,
        checkstyleFindings=0,spotbugsFindings=0,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='LIFETIME_FIRST_STOP_REMAINING_SUPPLY',componentOnly=True,mainFactoryWired=False,wholeProgramAccepted=False),
      additionalDiscoveries=dict(bugs=['BUG-1740'],ykt=['YKT-1491'],fixtureScopeClosed=True),
      productRework=dict(normalSources=2,normalFailures=1,selectedSources=1,totalSelectedExecutions=10,
        original10BeforeCompilerFix='UNRUN',mainSourceUnchangedByFix=True,changedFixtureOnly='lifeBudget005'),
      technicalEstimateCorrection=dict(predictedPhysicalClassChanges=1,actualPhysicalClassChanges=2,
        cause='Same source unit anonymous inner debug lines only; javap instruction text unchanged',newScope=False,budgetEstimateChanged=False),
      toolConstructionAndEnvironmentRework=dict(unusedImportPreflight=1,incompletePythonPathDiagnostic=1,childNotStarted=True,productTestsRerun=0,exclusivePp=None),
      relatedWbs='WBS-P018-09',componentAdditionalBudgetPp=0,
      sourceProofs=proof,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1873_APILifetimeBudget_限定実行結果・残依存.md'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,
      tokenMeasurementIds=['41d76e68ea4bccdc77cb956c931b0e4986fa688ba78870f216722d3d95b82e89'],
      pgptAllComplete=False,stopReason=None,
      nextCommand='9192 public delta/commit-push; bounded short Main factory existing-remaining/assembly supply or legacy2 contract review; actual operations HOLD'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,
          logical941AndHistorical943Unchanged=True,programPtComplete=False,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,sourceRows=250,programPtComplete=False)))

if __name__=='__main__':main()
