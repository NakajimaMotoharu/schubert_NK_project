"""Review12 explicit UNKNOWN-retaining boundaries; no retention/native target is invoked."""
from pathlib import Path
import datetime
import hashlib
import json

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
prior=b/'evidence/PG37066-f03-jdbc-close46-applicability-v1';previous=load(prior/'manifest.json');left=load(prior/'remaining-unmatched.json');assert len(left)==247
keys={('MorningPermitPublication.java',209),('MorningPermitPublication.java',236),('MorningStartupLaunchOwner.java',312),('MorningStartupLaunchOwner.java',401),('MorningStartupLaunchOwner.java',436),('MorningStartupLaunchOwner.java',519),('MorningStartupLaunchOwner.java',660),('MorningStartupLaunchOwner.java',681),('MorningBackupUnitCycle.java',393),('MorningBackupUnitCycle.java',474),('MorningBackupUnitCycle.java',501),('MorningBrokerUnitCycle.java',231)}
bodyrows=load(w/'pg37044-current-catch-bodies.json');bodies={(x['path'],int(x['facts']['firstLine'])):x for x in bodyrows};owners={x['path']:x for x in load(next((r/'documents/400_PGPT/470_PMO').glob('485_*.json')))['artifacts']};sites=[];seen=set();pins={}
for x in left:
 raw=x['raw'];key=(Path(raw['path']).name,int(raw['beginline']))
 if raw['rule']!='AvoidCatchingGenericException' or key not in keys:continue
 path=r/raw['path'];text=path.read_text();assert sha(path)==x['sourceSha256'];body=bodies[(raw['path'],key[1])];assert 'retain' in body['body']
 if path.name=='MorningStartupLaunchOwner.java':assert 'static void retain()' in text and 'for (; ; ) {' in text and 'LockSupport.parkNanos(' in text
 elif path.name=='MorningPermitPublication.java':assert 'retainedRetain.indefinitely();' in text and 'publication owner retention returned' in text
 elif path.name=='MorningBackupUnitCycle.java':assert 'retainedRetain.indefinitely();' in text and 'unresolved Backup retention returned' in text and 'for (; ; ) pausePreservingInterrupt();' in text
 else:assert 'retain.indefinitely();' in text and 'unresolved Broker retention returned' in text
 seen.add(key);pins[raw['path']]=x['sourceSha256'];owner=owners[raw['path']]
 sites.append(dict(rawFindingIndex=x['rawFindingIndex'],path=raw['path'],sourceSha256=x['sourceSha256'],line=key[1],column=int(raw['begincolumn']),rule=raw['rule'],owner=owner['owner'],costOwner=owner['costOwner'],resolvedCurrentCatch=body['facts'],fullCatchBody=body['body'],decision='NOT_APPLICABLE_REQUIRED_UNKNOWN_RETENTION_BOUNDARY',reason='Explicit SS342/343 lifetime contract catches all IO/Runtime/Error only to keep already-delivered or unconfirmed owner state. The native static retainer loops indefinitely; injected retained callback entries have an immediate throw if unexpectedly returned. Completion diagnosis is protected by SSC326 before retention. No clause reports successful cleanup/start/termination; catching only checked IO would incorrectly unwind an unknown Runtime/Error owner. This source-only applicability decision does not prove an actual retained process, root/permit retirement or native postcondition.',actualHoldOrRecoveryInvoked=False))
assert len(sites)==24 and seen==keys and len(pins)==4
indices={x['rawFindingIndex'] for x in sites};assert len(indices)==24;remaining=[x for x in left if x['rawFindingIndex'] not in indices];assert len(remaining)==223
out=b/'evidence/PG37070-f03-required-retention24-applicability-v1';assert not out.exists();out.mkdir();(out/'site-decisions.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2)+'\n');(out/'remaining-unmatched.json').write_text(json.dumps(remaining,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=previous['sourceCore'],reviewOnly=True,wholeCatchBodies=12,newFinalDispositions=24,sourceClasses=4,sourcePins=pins,finalWithPrior=748,remainingUnmatched=223,unconfirmedReuseCandidates=0,totalOriginalRaw=971,all971Reconciled=748+223==971,prior=ref(prior/'manifest.json'),sites=ref(out/'site-decisions.json'),remaining=ref(out/'remaining-unmatched.json'),sourceRuleSuppressionChanges=0,productTestsExecuted=0,actualRootNativeHoldOrRecoveryOperations=0,newAcceptance=0,wholeF03Accepted=False,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,catchBodies=12,newFinal=24,final=748,remaining=223,operationsInvoked=0,newAcceptance=0)))
