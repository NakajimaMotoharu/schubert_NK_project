"""Save one actual necessary regression and honest whole-class misses; no native/formal inflation."""
import json
from pathlib import Path
import pg998_metrics as metrics
import pg6990_recovery_public_scan as scan
from source_evidence_binding import bind
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
GROUP='WEB_CLOSE_HANDOFF_QUALIFICATION_V1'
OUT=BASE/'PG9584-web-close-handoff-metrics-v1'

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    rows=[json.loads(line) for line in metrics.EVENTS.read_bytes().splitlines()]
    starts=[r for r in rows if r['groupId']==GROUP and r['eventType']=='GROUP_START']
    assert len(starts)==1 and not any(r['groupId']==GROUP and r.get('groupBoundary')=='END' for r in rows)
    start=starts[0];assert start['groupStartEstimatePp']==dict(low=.5,base=2,high=6) and start['groupCapPp']==10
    pins=[(BASE/'PG9580-web-close-handoff-host-v1/manifest.json','d3de468ea11251f37122b32239d7166bd8b239952b8ba112737380ab2e013991'),
      (BASE/'PG9582-web-close-handoff-post-v1/manifest.json','30069fd06e3096a15ff173986e667092e862de89f2e3160903202f73f961a65c')]
    proofs=bind(pins,SOURCE);post=json.loads(pins[-1][0].read_bytes())
    assert post['actualTests']==1 and post['newTestIds']==0 and not post['requiredWholeClassFour100']
    verify(invocation)
    event=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-P018-06',source=SOURCE,sourceBefore=SOURCE,workCategory='SELECTED_TEST',
      groupStartEstimatePp=start['groupStartEstimatePp'],groupCapPp=10,quotaBefore=start['quotaBefore'],
      quotaAfter=dict(usedPercent=4,remainingPercent=96,resetsAt=1793513544),quotaBeforeObservedAtUTC='2026-10-25T08:15:42Z',
      quotaAfterObservedAtUTC='2026-10-25T08:18:51Z',sameQuotaWindow=True,observedSharedPp=0,actualAllocatedPp=None,
      tokenTotals=None,effortCompletionRate=None,attemptResult='NECESSARY_CHANGED_CLOSE_TO_WAITING_UNINSTALLED_OWNER_1_PT_PASS_POST_VERIFIED_WHOLE_FOUR100_FALSE',
      technicalMeasurementDelta=dict(productTestsExecuted=1,suites=1,newTestIds=0,newMain=0,necessaryRegression=1,
        wholeSourceUnitCounters=post['wholeSourceUnitCounters'],requiredWholeClassFour100=False,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='CHANGED_PRIVATE_LOCK_OWNER_COMPLETION_HANDOFF_REGRESSION',programPtComplete=False),
      additionalDiscoveries=dict(bugs=[],ykt=[]),sourceReauthentication=dict(currentNormalSnapshotAndAllInputHashesEqual=True,oldProductPtTransferred=False),
      toolConstructionAndEnvironmentRework=dict(hostAttempts=1,postAttempts=1,selectedMethodCount=1,invalidCategoryRejectedBeforeStart=1,exclusivePp=None),
      sourceProofs=proofs,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1943_WebCloseHandoff_当source限定回帰結果.md'],
      tokenMeasurementIds=['b4dfa3639844dc07f7ae5fecfd5aad4c525af7da7aa9f0f38ff050186c8b711a'],
      stopPolicy='FRESH_APPLICABLE_WINDOW_REMAINING_LE10_OR_UNAVAILABLE',oldCumulativeStopPolicyApplied=False,
      pgptAllComplete=False,stopReason=None,nextCommand='9586 publicdelta/save-push; next permitted independent PGPT, actual hooks/Root/native/refusal-unidentified HOLD unchanged'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=event,invocation=invocation,actualTests=1,newTestIds=0,
          wholeSourceUnitCounters=post['wholeSourceUnitCounters'],requiredWholeClassFour100=False,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=event)))
    scan.BEFORE='719e58a0992089a5e52a1c6f3ad96b62fd836258';scan.OUT=BASE/'PG9586-web-close-handoff-public-delta-v1';scan.main()

if __name__=='__main__':main()
