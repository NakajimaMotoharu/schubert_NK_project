"""Align exactly eight original public Test consumers; retain unrelated fixture fields and every oracle."""
from pathlib import Path
import datetime,hashlib,json,re
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';root=r/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform';out=b/'evidence/PG37158-root-fixture-consumer-alignment-v1';assert not out.exists();out.mkdir();rows=[]
changes={'BackupUnitStartClientTest.java':('root',1),'BackupUnitTerminationTest.java':('f',1),'MorningStopEvidenceTest.java':('f',1),'RootReleaseAdmissionTest.java':('kernel',3),'MaintenanceUnitTerminationTest.java':('root',2),'MaintenanceUnitStopClientTest.java':('root',1),'BackupUnitReceiptGateTest.java':('root',1),'MorningUnitTerminalsTest.java':('f',1)}
for p in sorted(root.glob('*.java')):
 if p.stem in ['RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest']:continue
 old=p.read_text()
 if not re.search(r'RootStartupContextTest\.(Fixture|LaunchFixture)',old):continue
 row=dict(path=str(p.relative_to(r)),shaBefore=hashlib.sha256(p.read_bytes()).hexdigest(),changes=0,reason='no old pid/boot/unit field access')
 if p.name in changes:
  var,count=changes[p.name];pattern=rf'\b{var}\.unit\b(?!\s*\()';assert len(re.findall(pattern,old))==count
  new=re.sub(pattern,var+'.unitValues',old);assert re.sub(rf'\b{var}\.unitValues\b',var+'.unit',new)==old
  assert len(re.findall(r'@Test',new))==len(re.findall(r'@Test',old));assert not re.search(pattern,new)
  if p.name=='BackupUnitTerminationTest.java':assert 'busy.unit = UNIT.replace(' in new
  (out/(p.name+'.before.txt')).write_text(old);p.write_text(new);row.update(changes=count,shaAfter=hashlib.sha256(p.read_bytes()).hexdigest(),inverseWholeByteExact=True,reason='typed original Root fixture field only; all literals/assertions/methods unchanged')
 rows.append(row)
assert len(rows)==14 and sum(x['changes']>0 for x in rows)==8 and sum(x['changes'] for x in rows)==11
(out/'consumer-inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),consumerSources=14,changedSources=8,changedFieldReferences=11,unrelatedBusyUnitPreserved=True,remainingConsumersNoOldFields=6,caddyFixtureExternalConsumers=0,productMainChanged=False,wholeTestCasesExecuted=0,strictCompile='PENDING_CURRENT_CLOSURE',bug='BUG3158',horizontal='YKT2627');(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
