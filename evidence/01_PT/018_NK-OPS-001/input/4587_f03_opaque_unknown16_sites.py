"""Review source-only client uncertainty boundaries; no start/stop/client target is executed."""
from pathlib import Path
import datetime
import hashlib
import json

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
prior=b/'evidence/PG37070-f03-required-retention24-applicability-v1';previous=load(prior/'manifest.json');left=load(prior/'remaining-unmatched.json');assert len(left)==223
keys={('BackupUnitStartClient.java',363),('BackupUnitStartClient.java',640),('BackupUnitStartClient.java',654),('BackupUnitStartClient.java',670),('MaintenanceUnitStopClient.java',129),('MaintenanceUnitStopClient.java',193),('MaintenanceUnitStopClient.java',207),('MaintenanceUnitStopClient.java',223)}
bodyrows=load(w/'pg37044-current-catch-bodies.json');bodies={(x['path'],int(x['facts']['firstLine'])):x for x in bodyrows};owners={x['path']:x for x in load(next((r/'documents/400_PGPT/470_PMO').glob('485_*.json')))['artifacts']};sites=[];seen=set()
for x in left:
 raw=x['raw'];key=(Path(raw['path']).name,int(raw['beginline']))
 if raw['rule']!='AvoidCatchingGenericException' or key not in keys:continue
 path=r/raw['path'];text=path.read_text();assert sha(path)==x['sourceSha256'];body=bodies[(raw['path'],key[1])];assert 'return Status.UNKNOWN;' in text and 'if (!closed) return Status.UNKNOWN;' in text and 'return closeOne(stderr) && clean;' in text
 owner=owners[raw['path']];seen.add(key)
 sites.append(dict(rawFindingIndex=x['rawFindingIndex'],path=raw['path'],sourceSha256=x['sourceSha256'],line=key[1],column=int(raw['begincolumn']),rule=raw['rule'],method=raw.get('method'),owner=owner['owner'],costOwner=owner['costOwner'],resolvedCurrentCatch=body['facts'],fullCatchBody=body['body'],decision='NOT_APPLICABLE_REQUIRED_OPAQUE_UNKNOWN_CLIENT_STATE',reason='SS342/343/SSC105: invoking start can deliver a client even when its call fails, so this exact boundary returns an opaque Attempt with no reaping proof. Poll/close faults poison or retain UNKNOWN, and closeOne(false) cannot satisfy streamsClosed/success. Inner read failure attempts stdout close and rethrows to that UNKNOWN boundary. These values are explicit non-success/ownership-uncertain, never NPE recovery as a completed operation or permission to release M/A. Both streams are still attempted, and throwing raw unknown outside this boundary would falsely allow normal parent unwind. No actual client/Root/socket/VM state is proved by source applicability.',actualStartStopOrClientExecuted=False))
assert len(sites)==16 and len({x['rawFindingIndex'] for x in sites})==16 and seen==keys
indices={x['rawFindingIndex'] for x in sites};remaining=[x for x in left if x['rawFindingIndex'] not in indices];assert len(remaining)==207
out=b/'evidence/PG37072-f03-opaque-unknown16-applicability-v1';assert not out.exists();out.mkdir();(out/'site-decisions.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2)+'\n');(out/'remaining-unmatched.json').write_text(json.dumps(remaining,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=previous['sourceCore'],reviewOnly=True,wholeCatchBodies=8,newFinalDispositions=16,sourceClasses=2,finalWithPrior=764,remainingUnmatched=207,unconfirmedReuseCandidates=0,totalOriginalRaw=971,all971Reconciled=764+207==971,prior=ref(prior/'manifest.json'),sites=ref(out/'site-decisions.json'),remaining=ref(out/'remaining-unmatched.json'),sourceRuleSuppressionChanges=0,productTestsExecuted=0,actualRootNativeStartStopOrRecoveryOperations=0,newAcceptance=0,wholeF03Accepted=False,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,catchBodies=8,newFinal=16,final=764,remaining=207,operationsInvoked=0,newAcceptance=0)))
