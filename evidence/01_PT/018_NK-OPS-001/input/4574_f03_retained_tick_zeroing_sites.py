"""Review fourteen documented absence/diagnostic sites plus ten nonnull-erasure rethrow sites."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
prior=b/'evidence/PG37046-f03-same-rethrow66-applicability-v1';prev=load(prior/'manifest.json');rows=load(prior/'remaining-unmatched.json');assert len(rows)==389
owners={x['path']:x for x in load(next((r/'documents/400_PGPT/470_PMO').glob('485_*.json')))['artifacts']}
empty={
 ('MorningStartupLaunchOwner.java',160):'SSC326 explicitly contains clock/sink RuntimeException/Error in best-effort completion diagnosis so original UNKNOWN owner frame retains resources; no normal success/release is created',
 ('MorningStartupLaunchOwner.java',303):'Creation/readiness IOException means not ready; enclosing parent/budget loop still requires positive readiness and otherwise reverse owned stop. Catch grants no success or ownership',
 ('MorningStartupLaunchOwner.java',635):'Only ConnectException denotes fixed socket not yet listening; ready remains false, child/parent budgets and owner/database consistency checks remain outside this catch',
 ('MorningCaddyReadiness.java',404):'A raced closed kernel FD raises NoSuchFileException; absent link is never added to descriptor evidence; remaining owner/socket predicates are still mandatory',
 ('MorningServiceReadiness.java',243):'Closed kernel FD is omitted, never converted into owned socket evidence. This source-only rule disposition does not prove runtime peer/socket ownership',
 ('ServiceProcessResources.java',243):'Best-effort fixed public diagnosis failure does not leave UNKNOWN retention; parent owns nonreturning frame under SS321/342 and no normal cleanup is reported',
 ('ServiceProcessResources.java',254):'Observation tick and fallback failure are contained for one tick; enclosing fixed while(true) cannot return/release original owner. Native behavior remains untested/held',
 ('ServiceProcessResources.java',276):'Interrupted sleep is a single observation tick, not cancellation/release evidence; enclosing retained frame is still nonreturning, ordinary/final owner termination remains separate'}
erase={
 ('MorningBackupArtifacts.java',548):'owned is new byte[size] allocated before try; catch only overwrites this nonnull locally owned buffer with zeros then rethrows unchanged Throwable',
 ('InspectorUnitProbe.java',254):'bytes[0] initialized to empty byte[] before try, every replacement uses Objects.requireNonNull; erasure cannot receive null and same Throwable is rethrown',
 ('InspectorUnitProbe.java',329):'second process-read path independently initializes nonnull empty byte[] and guards every reader replacement; erases buffer then preserves primary identity',
 ('MorningPreviousBroker.java',379):'query result is Objects.requireNonNull before try; catch erases nonnull returned buffer and rethrows same IO/runtime/fatal failure after failed owner/length check',
 ('SystemctlStateSource.java',98):'byte[][] holder starts with empty byte[]; only replacement is Objects.requireNonNull stdout result. Catch zeroes this buffer and preserves same RuntimeException/Error'}
sourcepins={};sites=[];counts={}
for x in rows:
 raw=x['raw'];key=(Path(raw['path']).name,int(raw['beginline']));rule=raw['rule'];reason=None
 if key in empty and rule in ['EmptyCatchBlock','AvoidCatchingGenericException']:reason=empty[key]
 elif key in erase and rule=='AvoidCatchingGenericException':reason=erase[key]
 if reason is None:continue
 path=r/raw['path'];text=path.read_text();assert sha(path)==x['sourceSha256'] and text.splitlines()[key[1]-1]==x['actualSourceLine'];sourcepins[raw['path']]=x['sourceSha256']
 if key in erase and key[0] in ['InspectorUnitProbe.java','SystemctlStateSource.java']:
  assert 'byte[][] bytes = {new byte[0]};' in text
  assigned=re.findall(r'bytes\[0\]\s*=\s*([^;]+);',text);assert assigned and all(a.strip().startswith('Objects.requireNonNull(') for a in assigned)
 if key==('ServiceProcessResources.java',254):assert 'while (true) observeUnknownInterval(observation, fallback);' in text
 owner=owners[raw['path']];sites.append(dict(rawFindingIndex=x['rawFindingIndex'],path=raw['path'],sourceSha256=x['sourceSha256'],line=key[1],column=int(raw['begincolumn']),rule=rule,actualSourceLine=x['actualSourceLine'],owner=owner['owner'],costOwner=owner['costOwner'],decision='NOT_APPLICABLE_REQUIRED_REFUSAL_RETENTION_OR_ERASURE',reason=reason,functionalNativeAcceptanceImplied=False));counts[rule]=counts.get(rule,0)+1
assert counts==dict(EmptyCatchBlock=8,AvoidCatchingGenericException=16) and len(sites)==24
indices={x['rawFindingIndex'] for x in sites};assert len(indices)==24;left=[x for x in rows if x['rawFindingIndex'] not in indices];assert len(left)==365
canonicalCommit=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip();docs=[]
for path in ['documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md','documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md']:
 raw=subprocess.check_output(['git','show',canonicalCommit+':'+path]);docs.append(dict(path=path,commit=canonicalCommit,sha256=hashlib.sha256(raw).hexdigest()))
out=b/'evidence/PG37048-f03-retention-erasure24-applicability-v1';assert not out.exists();out.mkdir();(out/'site-decisions.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2)+'\n');(out/'remaining-unmatched.json').write_text(json.dumps(left,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=prev['sourceCore'],reviewOnly=True,newSpecificFinal=24,counts=counts,finalSpecificWithPrior=297,oldCandidateUnconfirmed=309,remainingUnmatched=365,totalOriginalRaw=971,all971Reconciled=297+309+365==971,sourcePins=sourcepins,prior=ref(prior/'manifest.json'),sites=ref(out/'site-decisions.json'),remaining=ref(out/'remaining-unmatched.json'),canonicalSpecPins=docs,sourceRuleSuppressionChanges=0,productTestsExecuted=0,realNativeBrowserDbRootOperations=0,wholeF03Accepted=False,newAcceptance=0,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,newFinal=24,final=297,candidatesUnconfirmed=309,remainingUnmatched=365,newAcceptance=0)))
