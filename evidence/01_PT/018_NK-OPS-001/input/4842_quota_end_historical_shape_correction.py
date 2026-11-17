"""Append-only correction from actual saved receipts. No API/reset/token/cost inference or old writes."""
from pathlib import Path
import datetime,hashlib,json
from pmo_quota_binding import digest,window
from pmo_quota_legacy_end import metric_end_fields
import pg998_metrics as metrics
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ends=[f'PGPT-20261008-{n}' for n in (5657,5659,5661,5663,5665,5667,5669,5671)]
allrows=[json.loads(line) for line in metrics.EVENTS.read_bytes().splitlines()];assert not any(x.get('isHistoricalQuotaShapeCorrection') and x.get('bug')=='BUG3194' for x in allrows)
byid={x['eventId']:x for x in allrows};start_by_group={x['groupId']:x for x in allrows if x['eventType']=='GROUP_START'};corrections=[]
for eventid in ends:
    end=byid[eventid];start=start_by_group[end['groupId']];before=start['quotaReceipt']['observation'];after=end['quotaReceipt']['observation']
    assert digest(before)==start['quotaReceipt']['sha256'] and digest(after)==end['quotaReceipt']['sha256'] and end['postTerminalReceiptVerified'] is True
    assert end['quotaAfter']==after and end['quotaBefore']==before['primary']
    first,last=window(before['primary']),window(after['primary']);same=first is not None and last is not None and all(first[k]==last[k] for k in ['resetsAt','windowDurationMins']);delta=last['usedPercent']-first['usedPercent'] if same else None;assert delta is None or delta>=0
    original=end['quotaWindowReportedBeforeGuard'];assert original['sameQuotaWindow'] is same and original['observedSharedPp']==delta
    raw=dict(end);raw.update(sameQuotaWindow=same,observedSharedPp=delta);mapped=metric_end_fields(raw,before)
    canonical,_=metrics.canonical_fields(mapped,'GROUP_END')
    assert canonical['observedSharedPp']==delta and (canonical['sameQuotaWindow'] is True if same else canonical['sameQuotaWindow'] is None)
    corrections.append(dict(originalEndEvent=eventid,originalStartEvent=start['eventId'],groupId=end['groupId'],originalReportedSharedPp=end.get('observedSharedPp'),correctedObservedSharedPp=delta,beforePrimary=first,afterPrimary=last,exactSameMarkerAndWindow=same,startReceiptSha256=digest(before),endReceiptSha256=digest(after),historicalOnlyNotFreshPermission=True,dedicatedAllocationOrTokens=None,coarseZeroIsNotFreeOrTokenZero=True,originalPriceAndAcceptanceUnchanged=True,reason='Flatten saved verified primary only for legacy guard. Changed marker/window remains unknown; original events untouched.'))
assert len(corrections)==8 and sum(x['correctedObservedSharedPp']==0 for x in corrections)==5 and sum(x['correctedObservedSharedPp'] is None for x in corrections)==3
out=b/'evidence/PG37872-quota-end-append-only-correction-v1';assert not out.exists();out.mkdir();records=out/'historical-corrections8.json';records.write_text(json.dumps(corrections,indent=2)+'\n')
values=dict(wbsLeafIds=['WBS-G13.01'],workCategory='ADMIN',workAttributionKind='TOOL_FIX',bug='BUG3194',crossDeployment='YKT2661',isHistoricalQuotaShapeCorrection=True,correctionsForEvents=corrections,correctionOnlyNoFreshQuotaClaim=True,originalEventsUnmodified=True,originalPricesAndAllocationsUnchanged=True,newAcceptance=0,formalUpdated=False,effortCompletionRate=None,tokenTotals=None,actualAllocatedPp=None,proof=dict(path=str(records.relative_to(r)),sha256=hashlib.sha256(records.read_bytes()).hexdigest()))
id=metrics.append('PGPT-WBS66-QUOTA-END-SHAPE-20261118','CHECKPOINT',values)
manifest=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),correctionEventId=id,correctedHistoricalEnds=8,sameWindowObservedZero5=True,changedMarkerUnknown3=True,coarseZeroDoesNotProveDedicatedCostOrTokens=True,oldEventsOrCostsModified=False,existingUsageCursorNotReset=True,actualApiCallsOrResets=0,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,values=values)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,correctionEvent=id,originalEventsUntouched=8,sameObservedZero=5,changedUnknown=3,allocationOrTokens=None))
