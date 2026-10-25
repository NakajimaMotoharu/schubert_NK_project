"""Existing-method current qualification, no new ID/code, no normal or static replay."""
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9266-api-ordinary-guard-metrics-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
GROUP='P01805_API_ORDINARY_GUARD_QUALIFICATION_V1'

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proof=bind([
      (BASE/'PG9262-api-ordinary-guard-measure-v1/manifest.json','d10a3d37c2c05bb431cf1ca988b8af02dba11400a2d1de9d127fa57ca972d095'),
      (BASE/'PG9264-api-ordinary-guard-trace-v1/manifest.json','6c467096ff0550e3e09f3f13bf694e2e845ca117613d9d53a4a94bb0004e1894')],SOURCE)
    quota=json.loads((BASE/'PG9258-api-ordinary-guard-start-v1/quota-end.safe.json').read_bytes())
    assert quota['primary']['usedPercent']==60 and quota['primary']['resetsAt']==1793382075
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert inventory['currentIncrementalHostOwnership']['source']==SOURCE
    assert inventory['currentIncrementalHostOwnership']['sourceRows']==254
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(
      primaryWbs='WBS-P018-05',wbsLeafIds=['WBS-P018-05'],source=SOURCE,sourceBefore=SOURCE,
      workCategory='SELECTED_TEST',groupStartEstimatePp=dict(low=.25,base=.5,high=1),groupCapPp=1,
      quotaBefore=dict(usedPercent=60,remainingPercent=40,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=60,remainingPercent=40,resetsAt=1793382075),
      quotaAfterObservedAtUTC=quota['observedAtUTC'],sameQuotaWindow=True,observedSharedPp=0,
      original90Preservation=dict(originalBaselineUsed=0,originalBaselineReset=1793306748,
        capturedLowerBoundPp=85,unknownIntervalPp=2,cumulativeExactPp=None,cap=90,rebased=False,newLargeGroupsSuppressed=True),
      attemptResult='EXISTING2_CURRENT_EXEC_F0_E0_S0; EXISTING_INNER_ALL_MISSED0; WHOLE_LIFE_NOT100_HOLD',
      technicalMeasurementDelta=dict(newTestIds=0,newMain=0,necessaryRegressionTests=2,currentTests=2,currentSuites=1,
        newlyQualifiedExistingClass=1,physicalMain=1843,sourceOwners=254,
        wholeSourceUnitCounters=dict(LINE=dict(covered=51,missed=17),METHOD=dict(covered=15,missed=4),
          CLASS=dict(covered=2,missed=0),BRANCH=dict(covered=10,missed=4)),
        requiredWholeClassFour100=False,programPtComplete=False,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='CURRENT_SOURCE_PURE_GUARD_HEALTH_QUALIFICATION',
        newImplementation=False,wholeProgramAccepted=False),
      additionalDiscoveries=dict(bugs=[],ykt=[]),productRework=dict(productTestsRerunForConfirmation=0),
      sourceReauthentication=dict(all1843SameBytes=True,all254SameSourceOwners=True,normalReplay=False,
        staticReplay=False,architectureReplay=False,oldCoverageTransferred=False),
      toolConstructionAndEnvironmentRework=dict(exclusivePp=None),
      relatedWbs='WBS-P018-06',componentAdditionalBudgetPp=0,sourceProofs=proof,
      sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1885_APIOrdinaryGuard_当source限定資格結果.md'],
      tokenMeasurementIds=['903bff45226d7ef63578129bb22825a3aaf8fcacd66776bf7797d22bd12d767f'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,pgptAllComplete=False,stopReason=None,
      nextCommand='9268 public delta/commit-push; permitted missing current committed-fatal callback pure qualification or short quality within original90'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=identifier,invocation=invocation,
          newTestIds=0,newMain=0,programPtComplete=False,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,currentExistingTests=2,newTestIds=0)))

if __name__=='__main__':main()
