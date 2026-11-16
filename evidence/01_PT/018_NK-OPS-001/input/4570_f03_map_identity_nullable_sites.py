"""Review38 concrete local-map, same-capability, nullable-lifecycle and strict-reader sites."""
from pathlib import Path
import datetime
import hashlib
import json

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
prior=b/'evidence/PG37038-f03-j2ee169-applicability-v1';v=load(prior/'manifest.json');rows=load(prior/'remaining-unmatched.json');assert len(rows)==493 and v['newSourceMatchedFinalDispositions']==169
p485=next((r/'documents/400_PGPT/470_PMO').glob('485_*.json'));owners={x['path']:x for x in load(p485)['artifacts']}
identity={
 ('BackupStartIntentFiles.java',270):'intent.owner != this: same factory capability object; value equality cannot establish owned publication lifetime',
 ('BackupStartIntentFiles.java',286):'intent.owner == this: exact same publication capability, not value equivalence',
 ('InspectorEnvironmentFiles.java',191):'Thread.currentThread() == ownerThread: exact originating actor, Thread identity not value content',
 ('MorningCompletionEvidence.java',144):'completedReceipt() != backupReceipt: exact retained completed-cycle receipt, equal-looking replacement is not owned',
 ('BackupUnitReceiptGate.java',194):'receipt.owner != this: exact verifier owner capability',
 ('BackupUnitReceiptGate.java',209):'baseline.owner != this: exact gate that issued baseline',
 ('BackupUnitReceiptGate.java',210):'before.owner != this: exact same receipt gate, not cloned/equivalent value',
 ('BackupUnitReceiptGate.java',211):'before.baseline != baseline: exact originally held baseline receipt',
 ('MorningBackupUnitCycle.java',379):'receipt.stopped(baseline,held) != held: port must return exactly held receipt, no replacement',
 ('MorningBackupUnitCycle.java',408):'receipt.stopped(baseline,before) != before: repeated verification preserves held receipt identity plus quiescence',
 ('MorningBackupUnitCycle.java',479):'actual != observedReceipt.get(): exact child terminal evidence observed by same handoff',
 ('FixedNativeCoverageStopHold.java',76):'Thread.currentThread() != owner: refuse foreign capture actor, not object content equality',
 ('FixedNativeCoverageStopHold.java',95):'Thread.currentThread() == owner: do not wait for own thread; lifetime actor identity',
 ('FixedNativeCoverageTerminal.java',38):'Thread.currentThread() == owner: terminal collection only by exact constructor actor',
 ('FixedNativeCoverageTerminal.java',52):'Thread.currentThread() == owner: closing collection same actor and sequence',
 ('PostgresMigrationCopyPort.java',89):'cleanup != primary: Throwable identity guard prevents illegal self-suppression; equals may be overridden and does not establish self'}
# 17 original sites: two comparisons at one gate source line are separate PMD positions.
# The exact PMD index remains unique even when source path/line coincide.
nulls={
 ('ContinuousConditionWindow.java',32):'nullable violationStart reset under private lock when observation ceases violating; UNKNOWN/NORMAL must break old interval; subsequent VIOLATING null guard initializes before subtraction',
 ('InspectorAesCredential.java',56):'nullable decoded local is cleared only after ownership transfer into credential; finally erases only still-owned buffer, preserving moved key; no raw credential input is accessed by this review',
 ('SystemManagerObservation.java',166):'nullable pending session reset only after closed() true; stopped lifetime reference cannot be reused; read checks/opening guards are explicit'}
maps={
 ('BackupArtifactVerifier.java',185):'per-observePending callback snapshots index, no publication to shared worker',
 ('BackupArtifactVerifier.java',186):'per-observePending callback observed digest index, returned value copied for current observation',
 ('BackupArtifactVerifier.java',493):'per-verifyAt callback snapshots index, one synchronous verification lifetime',
 ('BackupArtifactVerifier.java',494):'per-verifyAt callback observed digest index, no shared field mutation',
 ('MaintenanceRunFiles.java',1039):'retirementScan local runs by UUID, one file-tree observation',
 ('MaintenanceRunFiles.java',1040):'retirementScan local begins by UUID, same scan only',
 ('MaintenanceRunFiles.java',1041):'retirementScan local completions by UUID, same scan only',
 ('MaintenanceRunFiles.java',1042):'retirementScan local plans by UUID, same scan only',
 ('MaintenanceRunFiles.java',1128):'scan local runs index, owned synchronous directory scan',
 ('MaintenanceRunFiles.java',1129):'scan local begins index, no static publication',
 ('MaintenanceRunFiles.java',1130):'scan local completions index, same observation only',
 ('InspectorUnitSnapshot.java',104):'parse local fixed eighteen-property index; immutable parsed snapshot output',
 ('MaintenanceUnitStopPolicy.java',53):'parse local fixed four-property index; immutable policy output',
 ('ReleasePayloadVerification.java',49):'jars instance index belongs to fresh one-shot verification object, constructor called only twice in StartupReleaseManifest verify paths, object never published',
 ('ReleasePayloadVerification.java',50):'checksums instance index belongs to same fresh unshared verification object; Contents returns immutable projection, no verifier escape',
 ('ReleasePayloadVerification.java',297):'archive callback local sql index; synchronous zip-entry read, no cross-thread map mutations'}
reader={
 ('BrokerJournalEvidence.java',334):'Strict JsonReader.peek mandatory trailing-token validation for side effect; return is intentionally unused after parsed root, exception refuses trailing garbage. Existing explicit comment pins this contract',
 ('ReleaseInventory.java',143):'Strict JsonReader.peek forces trailing-data parse; schema has already consumed complete root, no redundant compare with impossible false side; preserves original independent malformed/trailing oracle'}
selected=[];counts={}
for item in rows:
 raw=item['raw'];key=(Path(raw['path']).name,int(raw['beginline']));rule=raw['rule'];reason=None
 if rule=='UseConcurrentHashMap':reason=maps[key]
 elif rule=='CompareObjectsWithEquals':reason=identity[key]
 elif rule=='NullAssignment':reason=nulls[key]
 elif rule=='UnusedReturnValue':reason=reader[key]
 if reason is None:continue
 path=r/raw['path'];data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==item['sourceSha256'];lines=data.decode().splitlines();assert lines[key[1]-1]==item['actualSourceLine']
 owner=owners[raw['path']];selected.append(dict(rawFindingIndex=item['rawFindingIndex'],path=raw['path'],sourceSha256=item['sourceSha256'],line=key[1],column=int(raw['begincolumn']),className=raw.get('class'),method=raw.get('method'),rule=rule,actualSourceLine=item['actualSourceLine'],sourceContext=lines[max(0,key[1]-3):key[1]+3],owner=owner['owner'],costOwner=owner['costOwner'],decision='NOT_APPLICABLE_TO_CONCRETE_REQUIRED_CONTRACT',reason=reason,doesNotReplaceFunctionalNativeOrConcurrentTests=True));counts[rule]=counts.get(rule,0)+1
assert counts==dict(UseConcurrentHashMap=16,CompareObjectsWithEquals=17,NullAssignment=3,UnusedReturnValue=2)
indices={x['rawFindingIndex'] for x in selected};assert len(indices)==38
remaining=[x for x in rows if x['rawFindingIndex'] not in indices];assert len(remaining)==455
out=b/'evidence/PG37040-f03-specific38-applicability-v1';out.mkdir();(out/'site-decisions.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n');(out/'remaining-unmatched.json').write_text(json.dumps(remaining,ensure_ascii=False,indent=2)+'\n')
value=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=v['sourceCore'],reviewOnly=True,productTestsExecuted=0,newAnalysisOrRegressionReplayed=False,totalOriginalRaw=971,newSpecificFinal=38,counts=counts,finalSpecificWithPrior=207,oldCandidateUnconfirmed=309,remainingUnmatched=455,all971Reconciled=207+309+455==971,sites=ref(out/'site-decisions.json'),remaining=ref(out/'remaining-unmatched.json'),prior=ref(prior/'manifest.json'),ownerSource=ref(p485),reviewExtraCallGraphPins=[dict(path=str(p.relative_to(r)),sha256=sha(p)) for p in [r/'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/StartupReleaseManifest.java']],noSourceRuleSuppressionChanges=True,wholeF03Accepted=False,newAcceptance=0,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,counts=counts,final=207,candidatesUnconfirmed=309,remainingUnmatched=455,newAcceptance=0)))
