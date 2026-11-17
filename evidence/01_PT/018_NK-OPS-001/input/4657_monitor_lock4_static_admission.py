"""Explicitly classify unchanged same-throwable boundaries and finite ordinary JUnit workers."""
from pathlib import Path
import calendar,datetime,hashlib,json,re
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG37242-monitor-lock-oracle-current-preflight-v1/manifest.json';p=ld(pp);sp=b/'evidence/PG37226-monitor-lock4-fresh-sibling-spotbugs-v2/manifest.json';sb=ld(sp);abi=b/'evidence/PG37232-monitor-lock4-abi-physical-v1/manifest.json';a=ld(abi)
assert p['actualExit']==sb['actualExit']==a['actualExit']==0 and p['expectedTests']==113
assert sb['sourceCore']==p['sourceCore']==a['sourceCore']
assert sb['stages']['batch']['actualExit']==0 and not sb['stages']['batch']['timedOut']
assert sb['reports']['batch']['bugs']==0 and not sb['reports']['batch']['missingClasses'] and not sb['reports']['batch']['errors'] and len(sb['reports']['batch']['classStats'])==646
assert a['publicAbiAndInternalMethods'] and a['changedPhysicalCount']==3 and a['unchangedPhysicalCount']==1098
assert all(sha(r/n)==h for n,h in {**p['mainInputHashes'],**p['testSourceHashes']}.items())
test=r/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/MonitoringLockContractTest.java';text=test.read_text();main=r/'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/MonitoringPoller.java'
pattern=r'catch\s*\(RuntimeException\s*\|\s*Error\s+(\w+)\)\s*\{\s*interrupted = true;\s*throw \1;\s*\}'
assert len(re.findall(pattern,main.read_text()))==2
assert text.count('pool.shutdownNow();')==text.count('pool.awaitTermination(STOP_SECONDS, TimeUnit.SECONDS)')==2
assert '@Timeout(30)' in text and 'WAIT_SECONDS = 5;' in text and 'STOP_SECONDS = 10;' in text
assert text.count('assertFalse(second.isDone());')==2
state=text.index('assertTrue(\n          waiter.getState()')
assert text.index('assertFalse(second.isDone());',state)<text.index('release.countDown();',state)
assert calendar.timegm((2026,11,17,0,0,0))==1794873600 and '1_794_873_600.0' in text
classified=[]
for x in p['rawFindings']:
 assert Path(x['path']).name==test.name and x['rule'] in ['CloseResource','DoNotUseThreads']
 assert x.get('method') in ['anotherThread','lock406OtherMethodWaitsForOwnedCallbackThenCompletes']
 classified.append(dict(raw=x,applicable=False,basis='Standalone JUnit owns finite daemon workers. Future/latch waits5s, finally shutdownNow/await10s, class30s; release before join. Unknown/nonterminal workers fail assertions. No webapp scheduling or product runtime authority.'))
assert len(classified)==20
for x in p['reusedUnchangedMainFindings']:
 assert x['rule']=='AvoidCatchingGenericException' and Path(x['path']).name==main.name
 classified.append(dict(raw=x,applicable=False,basis='Exactly two unchanged callback/clock boundaries mark the next observation discontinuous and rethrow the identical RuntimeException/Error. No swallow/translation/normal success/NPE handling. Whole ordinary tests and LOCK401/402 cover failure and the next gap.'))
assert len(classified)==24
out=b/'evidence/PG37244-monitor-lock4-static-admission-v1';assert not out.exists();out.mkdir()
value=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=p['sourceCore'],prepare=ref(pp),spotbugs=ref(sp),abi=ref(abi),raw=24,applicable=0,unclassified=0,dispositions=classified,changedMainAvoidSynchronizedFindings=0,staticRuleOrSuppressionChanges=0,independentOracle=dict(fixedUtc='2026-11-17T00:00:00Z',gregorianCalendarEpochSeconds=1794873600,productionCodeUsedForExpected=False,waiterIdleRaceRejectedByPostStateNotDone=True),expectedTests=113,originalWholeTests=107,newWholeTests=6,productTestsExecuted=0,heldNativeActions=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=24,applicable=0,unclassified=0,expected113=True,productTests=0)))
