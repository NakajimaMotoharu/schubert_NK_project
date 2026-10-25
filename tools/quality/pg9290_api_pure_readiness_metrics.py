"""Existing-method current qualification, no new ID/code, no normal or static replay."""
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9290-api-pure-readiness-metrics-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
GROUP='P01805_API_PURE_READINESS_QUALIFICATION_V1'

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proof=bind([
      (BASE/'PG9286-api-pure-readiness-measure-v1/manifest.json','722dfd2319f371d57c92717f8dd240e46ace92eb2bf0079d68bc48a75438375c'),
      (BASE/'PG9288-api-pure-readiness-trace-v1/manifest.json','6a721ba74684d07681c61ba56593796363063f6e6eaa313cf62749dc94a2f7a6')],SOURCE)
    quota=json.loads((BASE/'PG9282-api-readiness-start-v1/quota-end.safe.json').read_bytes())
    assert quota['primary']['usedPercent']==61 and quota['primary']['resetsAt']==1793382075
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert inventory['currentIncrementalHostOwnership']['source']==SOURCE
    assert inventory['currentIncrementalHostOwnership']['sourceRows']==256
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(
      primaryWbs='WBS-P018-05',wbsLeafIds=['WBS-P018-05'],source=SOURCE,sourceBefore=SOURCE,
      workCategory='SELECTED_TEST',groupStartEstimatePp=dict(low=.25,base=.5,high=1),groupCapPp=1,
      quotaBefore=dict(usedPercent=61,remainingPercent=39,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=61,remainingPercent=39,resetsAt=1793382075),
      quotaAfterObservedAtUTC=quota['observedAtUTC'],sameQuotaWindow=True,observedSharedPp=0,
      original90Preservation=dict(originalBaselineUsed=0,originalBaselineReset=1793306748,
        capturedLowerBoundPp=86,unknownIntervalPp=2,cumulativeExactPp=None,cap=90,rebased=False,newLargeGroupsSuppressed=True),
      attemptResult='EXISTING3_CURRENT_PURE_READINESS_F0_E0_S0; TRUTH_ORDER_NULL_FAILURE; WHOLE_MAIN_NOT100_HOLD',
      technicalMeasurementDelta=dict(newTestIds=0,newMain=0,necessaryRegressionTests=3,currentTests=3,currentSuites=1,
        newlyQualifiedExistingClass=0,physicalMain=1843,sourceOwners=256,
        wholeSourceUnitCounters=dict(LINE=dict(covered=8,missed=168),METHOD=dict(covered=4,missed=30),
          CLASS=dict(covered=1,missed=0),BRANCH=dict(covered=10,missed=8)),
        requiredWholeClassFour100=False,programPtComplete=False,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='CURRENT_SOURCE_PURE_READINESS_TRUTH_ORDER_QUALIFICATION',
        newImplementation=False,wholeProgramAccepted=False),
      additionalDiscoveries=dict(bugs=[],ykt=[]),productRework=dict(productTestsRerunForConfirmation=0),
      sourceReauthentication=dict(all1843SameBytes=True,previous255SameSourceOwnersPlusOneCandidate=True,normalReplay=False,
        staticReplay=False,architectureReplay=False,oldCoverageTransferred=False),
      toolConstructionAndEnvironmentRework=dict(docPatchContextRejectedBeforeWrite=1,costCounterexamplePositiveAndSingleFieldValidated=True,productTestsReplayed=0,exclusivePp=None),
      relatedWbs='WBS-P018-06',componentAdditionalBudgetPp=0,sourceProofs=proof,
      sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1889_APIReadinessPure_当source限定資格結果.md'],
      tokenMeasurementIds=['2b354bb54e54c0dbc66c017ec0c1ffe9d42fcc6a2a93c3ca505014b5a4e97192'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,pgptAllComplete=False,stopReason=None,
      nextCommand='9292 public delta/commit-push; permitted bounded quality or missing ordinary qualification within original90'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=identifier,invocation=invocation,
          newTestIds=0,newMain=0,programPtComplete=False,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,currentExistingTests=3,newTestIds=0)))

if __name__=='__main__':main()
