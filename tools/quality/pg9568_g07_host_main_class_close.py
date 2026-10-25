"""Save public historical classification delta without claiming current-source secret gate."""
import json
from pathlib import Path
import pg998_metrics as metrics
import pg6990_recovery_public_scan as scan
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
GROUP='G07_HOST_MAIN_CLASS_DIGEST_V1'
OUT=BASE/'PG9568-g07-host-main-class-metrics-v1'

def main():
    invocation=capture(Path(__file__))
    assert not OUT.exists() and not (BASE/'PG9570-g07-host-main-class-public-delta-v1').exists()
    rows=[json.loads(line) for line in metrics.EVENTS.read_bytes().splitlines()]
    starts=[r for r in rows if r['groupId']==GROUP and r['eventType']=='GROUP_START']
    assert len(starts)==1 and not any(r['groupId']==GROUP and r.get('groupBoundary')=='END' for r in rows)
    start=starts[0]
    assert start['groupStartEstimatePp']==dict(low=.5,base=2,high=6) and start['groupCapPp']==10
    assert start['quotaBefore']==dict(usedPercent=3,remainingPercent=97,resetsAt=1793513544)
    proofs=bind([
      (BASE/'PG9564-g07-host-main-class-provenance-v1/manifest.json','458970306a06b661c558c67f25b5769308fffb91d2c7d8603f996084a70de2ff'),
      (BASE/'PG9566-g07-host-main-class-provenance-post-v1/manifest.json','8ad5591f0f152f44a9efb0e87a38d3eb8a6c844a7dadb3ecb50934c0747a929b')],SOURCE)
    verify(invocation)
    event=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-G07',source=SOURCE,sourceBefore=SOURCE,
      workCategory='CONTRACT_AUDIT',groupStartEstimatePp=start['groupStartEstimatePp'],groupCapPp=10,
      quotaBefore=start['quotaBefore'],quotaAfter=dict(usedPercent=4,remainingPercent=96,resetsAt=1793513544),
      quotaBeforeObservedAtUTC='2026-10-25T07:41:55Z',quotaAfterObservedAtUTC='2026-10-25T08:07:04Z',
      sameQuotaWindow=True,observedSharedPp=1,actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,
      stopPolicy='FRESH_APPLICABLE_WINDOW_REMAINING_LE10_OR_UNAVAILABLE',oldCumulativeStopPolicyApplied=False,
      attemptResult='3829_ADDITIONAL_HISTORICAL_FINDINGS_ALL_CAPTURES_BOUND_TO_PUBLIC_ARTIFACTS_4550_UNCLASSIFIED',
      technicalMeasurementDelta=dict(publicMainClasses=1843,publicMainSourceFiles=965,additionalFalsePositives=3829,
        cumulativeFalsePositiveProof=35536,remainingUnclassified=4550,actualSecretCount=None,productTestsExecuted=0,
        newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
      historicalSubject=dict(contentCommit='05d73a7974da8df92228160b96d91e7a006768f3',
        scanSource='fb9fce0f91de3d9fdfa634fe277592700f915e45',notCurrentSourceSecretGate=True),
      originalPlanEngineeringDelta=dict(item='PUBLIC_HOST_MAIN_ARTIFACT_PROVENANCE',wholeG07Accepted=False),
      additionalDiscoveries=dict(bugs=[],ykt=[],oneExactCaptureStillUnresolved=True),
      sourceReauthentication=dict(publicNormalHostBytesOnly=True,oldProductPtTransferred=False),
      toolConstructionAndEnvironmentRework=dict(producerAttempts=1,independentPostAttempts=1,
        compilerInvocations=1,toolReadJvms=1,sdkPreflightGuardFailure=1,scannerCalls=0,exclusivePp=None),
      sourceProofs=proofs,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1939_G07HostMainDigest_公開artifact根拠結果.md'],
      tokenMeasurementIds=['74eb00e85644f271f688831941f74268e77c2f22339681d378cd85a30bd5d7ae'],
      pgptAllComplete=False,stopReason=None,nextCommand='9570 publicdelta/save-push; select existing public normal host artifact provenance for remaining4550, no old PT replay or actual operations'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=event,invocation=invocation,additionalFalsePositives=3829,
          remainingUnclassified=4550,whole451Accepted=False,currentSourceWholeG07Qualified=False,
          productTestsExecuted=0,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=event)))
    scan.BEFORE='9fe00e6f64f8bfe5d8d109208edd972c26da5819'
    scan.OUT=BASE/'PG9570-g07-host-main-class-public-delta-v1'
    scan.main()

if __name__=='__main__':main()
