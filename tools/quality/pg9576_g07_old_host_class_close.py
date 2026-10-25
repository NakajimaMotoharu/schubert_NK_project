"""Close one historical public provenance group, not current-source PT or whole G07."""
import json
from pathlib import Path
import pg998_metrics as metrics
import pg6990_recovery_public_scan as scan
from source_evidence_binding import bind
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
GROUP='G07_OLD_HOST_MAIN_CLASS_DIGEST_V1'
OUT=BASE/'PG9576-g07-old-host-class-metrics-v1'

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    rows=[json.loads(line) for line in metrics.EVENTS.read_bytes().splitlines()]
    starts=[r for r in rows if r['groupId']==GROUP and r['eventType']=='GROUP_START']
    assert len(starts)==1 and not any(r['groupId']==GROUP and r.get('groupBoundary')=='END' for r in rows)
    start=starts[0];assert start['groupStartEstimatePp']==dict(low=.5,base=2,high=6) and start['groupCapPp']==10
    proofs=bind([
      (BASE/'PG9572-g07-old-host-main-class-provenance-v1/manifest.json','7cb508e23ab7f35e07ed82271885bae50d2ab2c8a07b97a7295f189fbc899c79'),
      (BASE/'PG9574-g07-old-host-main-class-post-v1/manifest.json','7dd344f9520f3a10788cf16a1de2e2d88133200d80b6c492371fa08200c7c7ed')],SOURCE)
    verify(invocation)
    event=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-G07',source=SOURCE,sourceBefore=SOURCE,workCategory='CONTRACT_AUDIT',
      groupStartEstimatePp=start['groupStartEstimatePp'],groupCapPp=10,quotaBefore=start['quotaBefore'],
      quotaAfter=dict(usedPercent=4,remainingPercent=96,resetsAt=1793513544),quotaBeforeObservedAtUTC='2026-10-25T08:09:15Z',
      quotaAfterObservedAtUTC='2026-10-25T08:12:35Z',sameQuotaWindow=True,observedSharedPp=0,actualAllocatedPp=None,
      tokenTotals=None,effortCompletionRate=None,attemptResult='57_ADDITIONAL_HISTORICAL_PUBLIC_CLASS_DIGEST_FINDINGS_4493_UNCLASSIFIED',
      technicalMeasurementDelta=dict(oldArtifactMainClasses=1799,oldArtifactMainSourceFiles=922,additionalFalsePositives=57,
        cumulativeFalsePositiveProof=35593,remainingUnclassified=4493,actualSecretCount=None,productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='OLD_NORMAL_HOST_ARTIFACT_PUBLIC_PROVENANCE',wholeG07Accepted=False),
      additionalDiscoveries=dict(bugs=[],ykt=[]),sourceReauthentication=dict(artifactSource='e196d0816c8a4920696d4f601f8b4cf97e9e8b48',oldProductPtTransferred=False),
      toolConstructionAndEnvironmentRework=dict(producerAttempts=1,independentPostAttempts=1,compilerInvocations=1,toolReadJvms=1,
        closeImportEnvironmentFailureBeforeEvent=1,exclusivePp=None),
      sourceProofs=proofs,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1941_G07OldHostDigest_公開artifact根拠結果.md'],
      tokenMeasurementIds=['25ef4b56ea701b8dc6382f1925c070f66001165b05ab50d736bf18204c0143e7'],
      stopPolicy='FRESH_APPLICABLE_WINDOW_REMAINING_LE10_OR_UNAVAILABLE',oldCumulativeStopPolicyApplied=False,
      pgptAllComplete=False,stopReason=None,nextCommand='9578 publicdelta/save-push; select next permitted PGPT by concrete remaining evidence, do not repeat old success or access private/native/actual HOLD'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=event,invocation=invocation,additionalFalsePositives=57,remainingUnclassified=4493,
          productTestsExecuted=0,currentSourceWholeG07Qualified=False,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=event)))
    scan.BEFORE='1893eb0e5eac124a1c504c1a887735d9ab3a3c18';scan.OUT=BASE/'PG9578-g07-old-host-class-public-delta-v1';scan.main()

if __name__=='__main__':main()
