"""Keep source ownership, binding correction and genuine whole-WBS HOLD distinct."""
import json
from pathlib import Path
import pg998_metrics as metrics
from source_evidence_binding import bind
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9340-g13-storage-residual-metrics-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
GROUP='G13_STORAGE_RESIDUAL10_OWNER_V1'

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proof=bind([
      (BASE/'PG9334-g13-storage-residual-join-v1/manifest.json','69df39386cdb70e792f3ab31de0c050c6c465a4d9a6b0264e17f29b9d1390ffd'),
      (BASE/'PG9336-g13-storage-residual-post-v1/manifest.json','05078f46bf155f9e3f6d9a3b19074b707afbf1e1541a64220c61409f41b618a2'),
      (BASE/'PG9338-wbs-reference-metadata-post-v1/manifest.json','6fd966a06566f9c7fcff62b6addab0c879ee7a0681e40fdc3e00396a1e2ffe3c')],SOURCE)
    quota=json.loads((BASE/'PG9334-g13-storage-residual-join-v1/quota-end.safe.json').read_bytes())
    assert quota['primary']['usedPercent']==63 and quota['primary']['resetsAt']==1793382075
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-G13.07',wbsLeafIds=['WBS-G13.07'],source=SOURCE,
      sourceBefore=SOURCE,workCategory='CONTRACT_AUDIT',groupStartEstimatePp=dict(low=.5,base=2,high=4),groupCapPp=10,
      quotaBefore=dict(usedPercent=63,remainingPercent=37,resetsAt=1793382075),
      quotaAfter=dict(usedPercent=63,remainingPercent=37,resetsAt=1793382075),quotaAfterObservedAtUTC=quota['observedAtUTC'],
      sameQuotaWindow=True,observedSharedPp=0,stopPolicy='FRESH_APPLICABLE_WINDOW_REMAINING_LE10_OR_UNAVAILABLE',
      oldCumulativeStopAndLargeGroupPolicyApplied=False,
      attemptResult='STORAGE_SOURCE29_OF29_REGISTERED; BINDING_CORRECTED; WHOLE_WBS_CURRENT_SCOPE_HOLD_RETAINED',
      technicalMeasurementDelta=dict(newExplicitSourceOwners=10,newTestOwners=8,newHelperOwners=2,sourceRows=289,
        javaPaths=1789,registered=1114,registeredMain=965,totalMain=965,registeredTest=149,totalTest=824,
        unregisteredTest=675,storageTestSourceRegistered=29,storageTestSourceTotal=29,metadataOwnerNegatives=16,
        metadataBindingNegatives=8,productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
      originalPlanEngineeringDelta=dict(item='STORAGE_RESIDUAL10_TRACE_RESPONSIBILITIES',wholeG13Accepted=False),
      additionalDiscoveries=dict(bugs=['BUG-1746'],ykt=['YKT-1497'],bindingFixed=True,fullAuditHold=True),
      sourceReauthentication=dict(sourceUnchanged=True,original941AndHistorical943Preserved=True,oldSourceResultsTransferred=False),
      toolConstructionAndEnvironmentRework=dict(initialAuditHashMismatch=1,afterBindingCurrentScopeHold=1,
        finalAuditCurrentScopeHold=1,actualAuditCodeChanged=False,exclusivePp=None),
      sourceProofs=proof,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1901_G13StorageResidual_残10path責任対応結果.md'],
      tokenMeasurementIds=['0a191a971c3b3f3e24da34d19b9db9dfd451614b568cd9f4d9816d2d9cfd0597'],
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,pgptAllComplete=False,stopReason=None,
      nextCommand='9342 bounded public delta/normal save; fresh remaining>10 then next permitted pure PG/PT or exact companion source trace group; no PMO wait'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,eventId=identifier,invocation=invocation,newExplicitSourceOwners=10,
          wholeWbsAuditAccepted=False,wholeG13Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,newExplicitSourceOwners=10)))

if __name__=='__main__':main()
