"""Confirm all remaining230 source-exact prior catch dispositions against current resolved types."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import sys

r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
from source_catch_context_inventory_test import facts
b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
prior=b/'evidence/PG37052-f03-reviewed39-resource-reuse-v1';previous=load(prior/'manifest.json');rows=load(prior/'remaining-candidates.json');assert len(rows)==230 and all(x['raw']['rule']=='AvoidCatchingGenericException' for x in rows)
fp=b/'evidence/PG37042-current287-catch-facts-v1/manifest.json';typed=load(fp);factslot=w/'pg37042-current287-catch-facts-v1';current={m:facts((factslot/(m+'.stdout')).read_text()) for m in ['bootstrap','batch']};assert {m:len(v) for m,v in current.items()}==typed['allCatchFacts']
for m in current:assert sha(factslot/(m+'.stdout'))==typed['stages'][m]['stdoutSha256']
owners={x['path']:x for x in load(next((r/'documents/400_PGPT/470_PMO').glob('485_*.json')))['artifacts']};sites=[];proofs={};reasonGroups=collections.Counter()
for x in rows:
 raw=x['raw'];path=r/raw['path'];text=path.read_text();c=x['candidate'];old=c['priorClassification'];assert sha(path)==x['sourceSha256']==c['sourceSha256']==typed['sourceInputs'][raw['path']]
 assert text.splitlines()[int(raw['beginline'])-1]==x['actualSourceLine'] and old['path']==raw['path'] and old['rule']==raw['rule'] and int(old['line'])==int(raw['beginline']) and old['disposition']=='NOT_APPLICABLE' and old['reason'].strip()
 for k in ['previousQualifiedPreflight','previousFullRootStatic','originalPerSiteAdmission']:
  pin=c[k];p=r/pin['path'];assert sha(p)==pin['sha256'];value=load(p)
  if k!='originalPerSiteAdmission':assert value['actualExit']==0
  proofs[pin['path']]=pin['sha256']
 module=raw['path'].split('/')[1].removeprefix('schubert-nk-');prefix='src/schubert-nk-'+module+'/src/main/java/'
 matched=[f for f in current[module] if f['path']==raw['path'][len(prefix):] and int(f['firstLine'])<=int(raw['beginline'])<=int(f['lastLine'])];assert len(matched)==1
 f=matched[0];assert any(t in f['type'].split('|') for t in ['java.lang.RuntimeException','java.lang.Error','java.lang.Exception'])
 owner=owners[raw['path']];reasonGroups[old['reason']]+=1
 sites.append(dict(rawFindingIndex=x['rawFindingIndex'],path=raw['path'],sourceSha256=x['sourceSha256'],line=int(raw['beginline']),column=int(raw['begincolumn']),rule=raw['rule'],owner=owner['owner'],costOwner=owner['costOwner'],actualSourceLine=x['actualSourceLine'],resolvedCurrentCatch=f,priorReason=old['reason'],currentReview='Reviewed all25 original reason groups. Whole source/imports/private helpers and exact rule/site still match their source-qualified approval. Current compiler-resolved exception types and catch control shape bind this same handler. Boundary retains primary/secondary identity and explicit resource-close priority, or emits fixed failure after fatal-graph preservation; no clause is accepted as successful NPE recovery. Required distinctions are per original source-qualified handler, not a blanket generic-catch waiver. Old PT/coverage is historical and is not transferred to current runtime/451/native.',decision='NOT_APPLICABLE_REVIEWED_CURRENT_TYPED_CONTRACT',priorEvidencePins={k:c[k] for k in ['previousQualifiedPreflight','previousFullRootStatic','originalPerSiteAdmission']},newFunctionalAcceptance=False,oldPtCarriedToCurrent=False))
assert len(sites)==len({x['rawFindingIndex'] for x in sites})==230 and len(reasonGroups)==25
out=b/'evidence/PG37054-f03-reviewed230-typed-catch-reuse-v1';out.mkdir();(out/'site-decisions.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=previous['sourceCore'],reviewOnly=True,reviewedReusedCandidates=230,reviewedReasonGroups=25,finalSpecificWithPrior=606,remainingCandidateUnconfirmed=0,remainingUnmatched=365,totalOriginalRaw=971,all971Reconciled=606+365==971,prior=ref(prior/'manifest.json'),currentTypedFacts=ref(fp),sites=ref(out/'site-decisions.json'),priorProofHashesRechecked=proofs,sourceRuleSuppressionChanges=0,productTestsExecuted=0,oldPtCarriedToCurrent=False,wholeF03Accepted=False,newAcceptance=0,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,reuseReviewed=230,reasonGroups=25,final=606,candidatesUnconfirmed=0,remainingUnmatched=365,newAcceptance=0)))
