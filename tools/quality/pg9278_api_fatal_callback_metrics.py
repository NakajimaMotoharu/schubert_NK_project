"""Existing-method current qualification, no new ID/code, no normal or static replay."""
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9278-api-fatal-callback-metrics-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
GROUP='P01805_API_FATAL_CALLBACK_QUALIFICATION_V1'

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proof=bind([
      (BASE/'PG9274-api-fatal-callback-measure-v1/manifest.json','4862a4949538a46497b3f2cabbb53e98e7a95922d65b3f873c1dcaf8b0ead008'),
      (BASE/'PG9276-api-fatal-callback-trace-v2/manifest.json','05bb33c3c4a35cd04945ffa0baf18c07166f6a97a3a7488b8d8cc96c4007906e')],SOURCE)
    quota=json.loads((BASE/'PG9270-api-fatal-callback-start-v1/quota-end.safe.json').read_bytes())
    assert quota['primary']['usedPercent']==61 and quota['primary']['resetsAt']==1793382075
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert inventory['currentIncrementalHostOwnership']['source']==SOURCE
    assert inventory['currentIncrementalHostOwnership']['sourceRows']==255
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(
      primaryWbs='WBS-P018-05',wbsLeafIds=['WBS-P018-05'],source=SOURCE,sourceBefore=SOURCE,
      workCategory='SELECTED_TEST',groupStartEstimatePp=dict(low=.25,base=.5,high=1),groupCapPp=1,
      quotaBefore=dict(usedPercent=61,remainingPercent=39,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=61,remainingPercent=39,resetsAt=1793382075),
      quotaAfterObservedAtUTC=quota['observedAtUTC'],sameQuotaWindow=True,observedSharedPp=0,
      original90Preservation=dict(originalBaselineUsed=0,originalBaselineReset=1793306748,
        capturedLowerBoundPp=86,unknownIntervalPp=2,cumulativeExactPp=None,cap=90,rebased=False,newLargeGroupsSuppressed=True),
      attemptResult='EXISTING2_CURRENT_FATAL_CALLBACK_F0_E0_S0; OWNER_BOUND_SANITIZED; INNER_UNEXECUTED_WHOLE_LIFE_NOT100_HOLD',
      technicalMeasurementDelta=dict(newTestIds=0,newMain=0,necessaryRegressionTests=2,currentTests=2,currentSuites=1,
        newlyQualifiedExistingClass=0,physicalMain=1843,sourceOwners=255,
        wholeSourceUnitCounters=dict(LINE=dict(covered=27,missed=41),METHOD=dict(covered=9,missed=10),
          CLASS=dict(covered=1,missed=1),BRANCH=dict(covered=4,missed=10)),
        requiredWholeClassFour100=False,programPtComplete=False,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='CURRENT_SOURCE_OWNER_BOUND_FATAL_CALLBACK_QUALIFICATION',
        newImplementation=False,wholeProgramAccepted=False),
      additionalDiscoveries=dict(bugs=['BUG-1745'],ykt=['YKT-1496'],toolScopeClosed=True),productRework=dict(productTestsRerunForConfirmation=0),
      sourceReauthentication=dict(all1843SameBytes=True,previous254SameSourceOwnersPlusOneCandidate=True,normalReplay=False,
        staticReplay=False,architectureReplay=False,oldCoverageTransferred=False),
      toolConstructionAndEnvironmentRework=dict(jsSyntaxBeforeAnyTool=1,oldCounterexampleShapeInvalid=1,newV2PositiveAndSingleCostFieldValidated=True,productTestsReplayed=0,exclusivePp=None),
      relatedWbs='WBS-P018-06',componentAdditionalBudgetPp=0,sourceProofs=proof,
      sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1887_APIFatalCallback_当source限定資格結果.md'],
      tokenMeasurementIds=['e89abe5d4dbc76b0b36410040979a9411fdc33a1fa6d5f199c185e0b1167ad08'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,pgptAllComplete=False,stopReason=None,
      nextCommand='9280 public delta/commit-push; permitted current pure-readiness qualification or short quality within original90'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=identifier,invocation=invocation,
          newTestIds=0,newMain=0,programPtComplete=False,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,currentExistingTests=2,newTestIds=0)))

if __name__=='__main__':main()
