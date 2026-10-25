"""Close current registry group and enter original90 preservation, not weekly exhaustion."""
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9322-g13-storage-companion-metrics-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
GROUP='G13_STORAGE_COMPANION19_OWNER_V1'

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proof=bind([
      (BASE/'PG9320-g13-storage-companion-join-v1/manifest.json','a68a1cddb4cbf42db72f8d9794170d229ac4ce2a068822694e910951adbe58bd'),
      (BASE/'PG9321-g13-storage-companion-post-v1/manifest.json','e2dd7b131c13134dd86c961ec72072acf67af6610e4d285bdc12c6afa8d56081')],SOURCE)
    quota=json.loads((BASE/'PG9320-g13-storage-companion-join-v1/quota-end.safe.json').read_bytes())
    assert quota['primary']['usedPercent']==63 and quota['primary']['resetsAt']==1793382075
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-G13.07',wbsLeafIds=['WBS-G13.07'],source=SOURCE,
      sourceBefore=SOURCE,workCategory='CONTRACT_AUDIT',groupStartEstimatePp=dict(low=.25,base=.5,high=1),groupCapPp=1,
      quotaBefore=dict(usedPercent=62,remainingPercent=38,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=63,remainingPercent=37,resetsAt=1793382075),quotaAfterObservedAtUTC=quota['observedAtUTC'],
      sameQuotaWindow=True,observedSharedPp=1,
      original90Preservation=dict(originalBaselineUsed=0,originalBaselineReset=1793306748,capturedLowerBoundPp=88,
        unknownIntervalPp=2,cumulativeExactPp=None,cap=90,preservationReservePp=2,reserveIsMeasurement=False,rebased=False,
        newLargeGroupsSuppressed=True,newWorkStopped=True,reason='CAPTURED_LOWER88_PLUS_PRESERVATION_RESERVE2_AT_ORIGINAL90; NOT_EXACT90_OR_WEEKLY10'),
      attemptResult='NINETEEN_TEST_SOURCE_OWNERS_REGISTERED; TEST_EXECUTION0; ENTER_PRESERVATION',
      technicalMeasurementDelta=dict(newExplicitTestSourceOwners=19,previousSourceRows=260,currentSourceRows=279,
        explicitRegisteredBefore=1085,explicitRegisteredAfter=1104,javaPaths=1789,mainRegistered=965,mainPaths=965,
        testRegistered=139,testPaths=824,remainingUnregisteredTests=685,independentGolden=19,metadataCounterexamples=25,
        productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='STORAGE19_EXACT_COMPANION_TRACE_CANDIDATES',wholeG13Accepted=False),
      additionalDiscoveries=dict(bugs=[],ykt=[]),sourceReauthentication=dict(sourceUnchanged=True,oldProductPtTransferred=False),
      toolConstructionAndEnvironmentRework=dict(retries=0,exclusivePp=None),sourceProofs=proof,
      sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1897_G13StorageTest_直接対応19件結果.md'],
      tokenMeasurementIds=['90395ec23932ba0740e8b17f22ffab6e4dad19db467e16041dbcc38c0137e4a7'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,pgptAllComplete=False,
      stopReason='ORIGINAL90_PRESERVATION_RESERVE_NOT_PGPT_COMPLETE',
      nextCommand='9324 public delta; persist1898/456/460 and exact source/head/cursor; normal commit/push; no new PG/PT group'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=identifier,invocation=invocation,newExplicitTestSourceOwners=19,
          original90CapturedLowerBoundPp=88,cumulativeExactPp=None,wholeG13Accepted=False,whole451Accepted=False,
          formalUpdated=False,newAccepted=0,newWorkStoppedForPreservation=True),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,newExplicitTestOwners=19,preservation=True)))

if __name__=='__main__':main()
