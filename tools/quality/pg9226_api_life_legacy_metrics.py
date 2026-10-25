"""Read-only two-row diagnosis, not implementation, PT PASS or full static acceptance."""
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9226-api-life-legacy-metrics-v1'
SOURCE='3641d0f49e6b33fe64de718703f134406dfddb30'

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    proof=bind([(BASE/'PG9224-api-life-legacy-contract-v1/manifest.json',
      '74c11ab1997d4dc48bd4ef46dd92940825697bb1a8c2dbc257f4a73f08dedc67')],SOURCE)
    verify(invocation)
    identifier=metrics.append('P01805_API_LIFE_LEGACY_CONTRACT_V1','GROUP_END',dict(
      primaryWbs='WBS-P018-05',wbsLeafIds=['WBS-P018-05'],source=SOURCE,workCategory='CONTRACT_AUDIT',
      groupStartEstimatePp=dict(low=.25,base=.5,high=1),groupCapPp=1,
      quotaBefore=dict(usedPercent=59,remainingPercent=41,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=59,remainingPercent=41,resetsAt=1793382075),sameQuotaWindow=True,observedSharedPp=0,
      attemptResult='TWO_RAW_ROWS_CLASSIFIED_AS_APPLICABLE_REMEDIATION_REQUIRED; UNRESOLVED2; NEW_PT0',
      technicalMeasurementDelta=dict(newTestIds=0,newMain=0,examinedStaticRows=2,applicableUnresolved=2,
        productTestsExecuted=0,coverage=None,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='LIFE_LEGACY_STATIC_CAUSE_AND_MINIMAL_FIX_CONTRACT',diagnosisOnly=True),
      additionalDiscoveries=dict(webSameCatchCandidate=1,scopeExpansionNotStarted=True),
      productRework=dict(productTestsRerun=0),sourceReauthentication=dict(currentSourceHashOnly=True,oldPtTransferred=False),
      toolConstructionAndEnvironmentRework=dict(unregisteredCategoryRejectedBeforeAppend=1,exclusivePp=None),
      relatedWbs='WBS-P018-09',componentAdditionalBudgetPp=0,sourceProofs=proof,
      sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1879_APILifeLegacy_個別判定結果・残是正.md'],
      original90Preservation=dict(originalBaselineUsed=0,originalBaselineReset=1793306748,
        capturedLowerBoundPp=84,unknownIntervalPp=2,cumulativeExactPp=None,cap=90,rebased=False,newLargeGroupsSuppressed=True),
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,pgptAllComplete=False,stopReason=None,
      nextCommand='9228 public delta/commit-push; bounded internal Life atomic-state/explicit shutdown-return remedy if fresh original90 permits'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=identifier,invocation=invocation,
          programPtComplete=False,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,applicableUnresolved=2)))

if __name__=='__main__':main()
