"""Record bounded registry measurement separately from full trace/PT acceptance."""
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9306-g13-registered-owner-metrics-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
GROUP='G13_CURRENT_JAVA_REGISTERED_OWNER_GAP_V1'

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    rows=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in rows)
    proof=bind([
      (BASE/'PG9304-g13-registered-owner-gap-v1/manifest.json','bf0371f1eb4a85462ee8db6b265814fe933038b9084243aba933ada81ba162f0'),
      (BASE/'PG9305-g13-registered-owner-post-v1/manifest.json','d7e18d48aa6ab253b3ce981c06dba02a7caf850e892c66ae7b96ee6b41141b03')],SOURCE)
    quota=json.loads((BASE/'PG9302-g13-registered-owner-start-v1/quota-end.safe.json').read_bytes())
    assert quota['primary']['usedPercent']==62 and quota['primary']['resetsAt']==1793382075
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-G13.07',wbsLeafIds=['WBS-G13.07'],
      source=SOURCE,sourceBefore=SOURCE,workCategory='CONTRACT_AUDIT',groupStartEstimatePp=dict(low=.25,base=.5,high=1),groupCapPp=1,
      quotaBefore=dict(usedPercent=62,remainingPercent=38,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=62,remainingPercent=38,resetsAt=1793382075),quotaAfterObservedAtUTC=quota['observedAtUTC'],
      sameQuotaWindow=True,observedSharedPp=0,
      original90Preservation=dict(originalBaselineUsed=0,originalBaselineReset=1793306748,capturedLowerBoundPp=87,
        unknownIntervalPp=2,cumulativeExactPp=None,cap=90,preservationReservePp=2,reserveIsMeasurement=False,rebased=False,newLargeGroupsSuppressed=True),
      attemptResult='1789_JAVA_PATHS_1081_EXPLICIT_REGISTERED_708_UNREGISTERED; NOT_WHOLE_TRACE_ACCEPTANCE',
      technicalMeasurementDelta=dict(javaPaths=1789,explicitRegistered=1081,baselineLogicalReferences=847,
        currentReviewedCandidates=234,unregistered=708,mainPaths=965,mainRegistered=961,mainUnregistered=4,
        testPaths=824,testRegistered=120,testUnregistered=704,metadataCounterexamples=8,
        newTestIds=0,newMain=0,productTestsExecuted=0,coverage=None,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='G13_EXPLICIT_REGISTRY_DENOMINATOR_AND_GAP_MEASUREMENT',wholeG13Accepted=False),
      additionalDiscoveries=dict(mainRegistryGaps=4,testRegistryGaps=704,bugs=[],ykt=[],notNewProductFailures=True),
      sourceReauthentication=dict(currentAndSnapshotAndGit1789HashesMatch=True,oldProductPtTransferred=False),
      toolConstructionAndEnvironmentRework=dict(metadataReadDiagnostics=2,exclusivePp=None),
      sourceProofs=proof,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1893_G13SourcePath_登録所有網羅差分結果.md'],
      tokenMeasurementIds=['afc27d4e47c57544f4697ebc409d590e77ca1c67a5a4763aa841b34875ff6eef'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,pgptAllComplete=False,stopReason=None,
      nextCommand='9308 public delta/commit-push; fresh original90 check; main four explicit RD/UI/SS/Program registry review only if cap plus reserve fits'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=identifier,invocation=invocation,unregisteredMain=4,
          unregisteredTest=704,wholeG13Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,unregistered=708)))

if __name__=='__main__':main()
