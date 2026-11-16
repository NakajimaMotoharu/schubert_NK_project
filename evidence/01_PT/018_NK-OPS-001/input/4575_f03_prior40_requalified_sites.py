"""Independently confirm forty source-exact candidate dispositions, without carrying historical PT."""
from pathlib import Path
import collections
import datetime
import hashlib
import json

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
base=b/'evidence/PG36968-current287-pmd971-candidates-v2';allrows=load(base/'all-site-candidates.json');prior=b/'evidence/PG37048-f03-retention-erasure24-applicability-v1/manifest.json';p=load(prior);assert p['finalSpecificWithPrior']==297 and p['oldCandidateUnconfirmed']==309
selected=[x for x in allrows if x.get('candidate') and x['raw']['rule'] in ['CompareObjectsWithEquals','DoNotUseThreads','UseConcurrentHashMap','ReplaceJavaUtilDate']];assert len(selected)==40
owners={x['path']:x for x in load(next((r/'documents/400_PGPT/470_PMO').glob('485_*.json')))['artifacts']};sites=[];proofs={}
for x in selected:
 raw=x['raw'];path=r/raw['path'];text=path.read_text();assert sha(path)==x['sourceSha256']==x['candidate']['sourceSha256'] and text.splitlines()[int(raw['beginline'])-1]==x['actualSourceLine']
 c=x['candidate'];old=c['priorClassification'];assert old['path']==raw['path'] and old['rule']==raw['rule'] and int(old['line'])==int(raw['beginline']) and old['disposition']=='NOT_APPLICABLE' and old['reason'].strip()
 for key in ['previousQualifiedPreflight','previousFullRootStatic','originalPerSiteAdmission']:
  pin=c[key];f=r/pin['path'];assert sha(f)==pin['sha256'];v=load(f)
  if key!='originalPerSiteAdmission':assert v['actualExit']==0
  proofs[pin['path']]=pin['sha256']
 rule=raw['rule'];line=x['actualSourceLine']
 if rule=='CompareObjectsWithEquals':
  assert 'cleanup != primary' in line or 'source == target' in line
  current='Same Throwable identity avoids prohibited self-suppression, or same borrowed Connection identity prohibits aliasing; equals cannot establish either required ownership/identity. Current whole-source matches source-qualified approval exactly.'
 elif rule=='DoNotUseThreads':
  assert 'Thread.currentThread()' in line
  current='Exact existing interrupt observation/restoration only, in standalone batch/bootstrap Jar under canonical SS311/321/341/343; J2EE container policy is inapplicable. No new worker or runtime qualification is inferred.'
 elif rule=='UseConcurrentHashMap':
  assert path.name=='MaintenanceStopSnapshot.java' and 'Map.copyOf(' in text and 'new HashMap<>()' in line
  current='This parse invocation owns the local index; private constructor freezes it with Map.copyOf, so there is no concurrent mutable map. Per-source current line and whole class match prior qualified static approval.'
 else:
  assert rule=='ReplaceJavaUtilDate' and 'Timestamp' in line and 'getTimestamp(' in line and '.toInstant()' in text
  current='Required nullable JDBC ResultSet.getTimestamp boundary is immediately converted to Instant; immutable domain/UTC comparison and original SQL bytes are unchanged. No calendar arithmetic or retained Date domain state. Driver/DB/native qualification stays separate.'
 owner=owners[raw['path']];sites.append(dict(rawFindingIndex=x['rawFindingIndex'],path=raw['path'],sourceSha256=x['sourceSha256'],line=int(raw['beginline']),column=int(raw['begincolumn']),rule=rule,actualSourceLine=line,owner=owner['owner'],costOwner=owner['costOwner'],decision='NOT_APPLICABLE_REVIEWED_CURRENT_SOURCE_EXACT',priorReason=old['reason'],currentReview=current,priorEvidencePins={k:c[k] for k in ['previousQualifiedPreflight','previousFullRootStatic','originalPerSiteAdmission']},oldPtCarriedToNewSource=False,newFunctionalAcceptance=False))
counts=dict(collections.Counter(x['rule'] for x in sites));assert counts==dict(DoNotUseThreads=8,UseConcurrentHashMap=1,CompareObjectsWithEquals=29,ReplaceJavaUtilDate=2)
indices={x['rawFindingIndex'] for x in sites};assert len(indices)==40;left=[x for x in allrows if x.get('candidate') and x['rawFindingIndex'] not in indices];assert len(left)==269
out=b/'evidence/PG37050-f03-reviewed40-reuse-v1';out.mkdir();(out/'site-decisions.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2)+'\n');(out/'remaining-candidates.json').write_text(json.dumps(left,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=p['sourceCore'],reviewOnly=True,reviewedReusedCandidates=40,counts=counts,finalSpecificWithPrior=337,remainingCandidateUnconfirmed=269,remainingUnmatched=365,totalOriginalRaw=971,all971Reconciled=337+269+365==971,prior=ref(prior),candidateSource=ref(base/'manifest.json'),sites=ref(out/'site-decisions.json'),remaining=ref(out/'remaining-candidates.json'),priorProofHashesRechecked=proofs,sourceRuleSuppressionChanges=0,productTestsExecuted=0,oldPtCarriedToCurrent=False,wholeF03Accepted=False,newAcceptance=0,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,reviewedReused=40,final=337,candidatesUnconfirmed=269,remainingUnmatched=365,newAcceptance=0)))
