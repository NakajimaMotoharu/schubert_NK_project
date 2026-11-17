"""Admit exact source/compile/static/ABI and the single pure codec constructor white-box scope."""
from pathlib import Path
import datetime,hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG37278-record-codec-test-static-v1/manifest.json';p=ld(pp);sp=b/'evidence/PG37276-record-codec-fresh-sibling-spotbugs-v1/manifest.json';s=ld(sp);ap=b/'evidence/PG37280-record-codec-abi-physical-v1/manifest.json';a=ld(ap)
assert p['actualExit']==s['actualExit']==a['actualExit']==0 and p['expectedTests']==20 and p['sourceClosureCount']==4
assert p['sourceCore']==s['sourceCore']==a['sourceCore'] and not p['rawFindings'] and not p['processingErrors']
assert s['stages']['batch']['actualExit']==0 and not s['stages']['batch']['timedOut'] and s['reports']['batch']['bugs']==0 and not s['reports']['batch']['missingClasses'] and not s['reports']['batch']['errors'] and len(s['reports']['batch']['classStats'])==646
assert a['publicAbiExact'] and a['allPrivateSignaturesExact'] and a['changedPhysicalCount']==1 and a['unchangedPhysicalCount']==1100
assert all(sha(r/n)==h for n,h in {**p['mainInputHashes'],**p['testSourceHashes']}.items())
old=ld(b/'evidence/PG29956-maintenance-records16-post-v2/manifest.json');original={n:h for n,h in old['inputHashes'].items() if '/src/test/' in n};assert len(original)==3 and all(sha(r/n)==h for n,h in original.items())
new=r/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MaintenanceRecordsRawContractTest.java';text=new.read_text();assert text.count('MaintenanceRecords.class.getDeclaredConstructor()')==1 and text.count('.getDeclaredConstructor()')==1 and 'constructor.setAccessible(false);' in text and 'constructor.canAccess(null)' in text
assert p['reflectionReview']['noOtherPrivateMembers'] and not p['reflectionReview']['osOrApplicationPermissionChanges']
assert 1*31+17==48 and 48*31+79==49*31+48==1567
out=b/'evidence/PG37282-record-codec-static-admission-v1';assert not out.exists();out.mkdir();v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=p['sourceCore'],prepare=ref(pp),spotbugs=ref(sp),abi=ref(ap),raw=0,applicable=0,unclassified=0,expectedTests=20,originalWholeCases=16,newWholeCases=4,reflectionReview=p['reflectionReview'],independentHashVectors=[dict(bytes=[1,17],hash=48,expected='IOException canonical status rejection'),dict(bytes=[48,79],hash=1567,expected='IOException canonical status rejection')],guardExpected='AssertionError: MaintenanceRecords is a static codec',old16ExecCombined=False,qualityRuleOrSuppressionChanges=0,productTestsExecuted=0,heldClassfileActions=0,actualNativeRootDbVmActions=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=0,expected20=True,changedPhysical1=True,productTests=0)))
