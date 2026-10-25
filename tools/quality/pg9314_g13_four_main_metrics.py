"""Four explicit registry entries are neither production tests nor formal acceptance."""
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9314-g13-four-main-metrics-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
GROUP='G13_FOUR_MAIN_EXPLICIT_OWNER_V1'

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    rows=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in rows)
    proof=bind([
      (BASE/'PG9312-g13-four-main-join-v1/manifest.json','7fd038ec63dbf02d5f7b2d2c8b71d651a08da16b19d1bbbe518429ebe569b6b4'),
      (BASE/'PG9313-g13-four-main-post-v1/manifest.json','2f8b959fc23f22905b25452b6fe24fece15f0145a8151b64ef9a92a7656e27dd')],SOURCE)
    quota=json.loads((BASE/'PG9312-g13-four-main-join-v1/quota-end.safe.json').read_bytes())
    assert quota['primary']['usedPercent']==62 and quota['primary']['resetsAt']==1793382075
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-G13.07',wbsLeafIds=['WBS-G13.07'],
      source=SOURCE,sourceBefore=SOURCE,workCategory='CONTRACT_AUDIT',groupStartEstimatePp=dict(low=.25,base=.5,high=1),groupCapPp=1,
      quotaBefore=dict(usedPercent=62,remainingPercent=38,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=62,remainingPercent=38,resetsAt=1793382075),quotaAfterObservedAtUTC=quota['observedAtUTC'],
      sameQuotaWindow=True,observedSharedPp=0,
      original90Preservation=dict(originalBaselineUsed=0,originalBaselineReset=1793306748,capturedLowerBoundPp=87,
        unknownIntervalPp=2,cumulativeExactPp=None,cap=90,preservationReservePp=2,reserveIsMeasurement=False,rebased=False,newLargeGroupsSuppressed=True),
      attemptResult='FOUR_EXACT_MAIN_REGISTERED; MAIN965_OF965; TEST120_OF824_UNCHANGED; NO_PRODUCT_ACCEPTANCE',
      technicalMeasurementDelta=dict(newExplicitOwnerRows=4,previousBoundedSourceRows=256,currentBoundedSourceRows=260,
        javaPaths=1789,explicitRegisteredBefore=1081,explicitRegisteredAfter=1085,unregisteredBefore=708,unregisteredAfter=704,
        mainRegistered=965,mainPaths=965,testRegistered=120,testPaths=824,literalGoldenCases=4,metadataCounterexamples=10,
        productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='FOUR_MAIN_TRACE_OWNERSHIP_CANDIDATES',wholeG13Accepted=False),
      additionalDiscoveries=dict(bugs=[],ykt=[]),sourceReauthentication=dict(sourceUnchanged=True,oldProductPtTransferred=False),
      toolConstructionAndEnvironmentRework=dict(preflightMissingGuessedDocumentDirectory=2,exclusivePp=None),
      sourceProofs=proof,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1895_G13FourMain_所有対応補完結果.md'],
      tokenMeasurementIds=['c1a0eff76e7de1aef7271ab27163708ed6a969f9112d581d51a331cf2575e3a2'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,pgptAllComplete=False,stopReason=None,
      nextCommand='9316 public delta and normal commit/push; fresh original90; only bounded necessary ordinary PT or quality if cap plus reserve2 fits'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=identifier,invocation=invocation,newExplicitOwnerRows=4,
          wholeG13Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,newExplicitOwnerRows=4)))

if __name__=='__main__':main()
