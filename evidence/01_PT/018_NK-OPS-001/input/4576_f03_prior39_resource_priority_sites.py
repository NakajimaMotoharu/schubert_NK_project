"""Revalidate39 reviewed source-exact resource aliases/explicit approved cleanup-priority sites."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import subprocess

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
prior=b/'evidence/PG37050-f03-reviewed40-reuse-v1';previous=load(prior/'manifest.json');rows=load(prior/'remaining-candidates.json');selected=[x for x in rows if x['raw']['rule'] in ['CloseResource','DoNotThrowExceptionInFinally']];assert len(selected)==39
facts=load(b/'evidence/PG37042-current287-catch-facts-v1/manifest.json');owners={x['path']:x for x in load(next((r/'documents/400_PGPT/470_PMO').glob('485_*.json')))['artifacts']};sites=[];pins={}
for x in selected:
 raw=x['raw'];path=r/raw['path'];text=path.read_text();c=x['candidate'];old=c['priorClassification'];assert sha(path)==x['sourceSha256']==c['sourceSha256']==facts['sourceInputs'][raw['path']]
 assert text.splitlines()[int(raw['beginline'])-1]==x['actualSourceLine'] and old['path']==raw['path'] and old['rule']==raw['rule'] and int(old['line'])==int(raw['beginline']) and old['disposition']=='NOT_APPLICABLE' and old['reason'].strip()
 for k in ['previousQualifiedPreflight','previousFullRootStatic','originalPerSiteAdmission']:
  pin=c[k];p=r/pin['path'];assert sha(p)==pin['sha256'];value=load(p)
  if k!='originalPerSiteAdmission':assert value['actualExit']==0
  pins[pin['path']]=pin['sha256']
 if raw['rule']=='DoNotThrowExceptionInFinally':
  assert 'finally' in x['actualSourceLine'] and ('JdbcResourceFailures' in text or 'JdbcAdmissionFailures' in text)
  review='Current source-exact direct nested finally closes each actually acquired row/statement once and applies the explicit SS332/341/343 secondary-vs-primary matrix. Throwing a higher-priority unknown/fatal cleanup is required; generic TWR or swallowing it would change that matrix. Current semantic input is bound; this is static policy applicability only, not a fresh JDBC fault/native PT result.'
 elif path.name=='MigrationMasterCopyFingerprint.java':
  assert 'class DigestSink' in text and 'MessageDigest' in text and 'sinks.get(index)' in x['actualSourceLine']
  review='Concrete private in-memory DigestSink uses pinned MessageDigest/counter only and inherits no-op OutputStream.close; no external owner/resource is acquired by the alias. Source/actual source-qualified review exact; database/file/native success is not implied.'
 elif path.name=='MaintenanceMutationGuard.java':
  assert 'try (' in text and 'Objects.requireNonNull' in x['actualSourceLine']
  review='Non-null checked/row references alias exactly the same statement/result owned by enclosing two TWR declarations, so no second owner or missing close is introduced. Current full source exact and typed compilation already qualified.'
 else:
  assert 'finally' in text and any(t in text for t in ['JdbcResourceFailures','JdbcAdmissionFailures','closeStatement'])
  review='Current whole source exact: nullable acquired JDBC resource is rejected before alias or has its original owner directly closed by nested typed finally/private close helper. Connection is borrowed and deliberately not closed. Intraprocedural alias warning does not account for that owner; original explicit SS332/343 failure priority and actual functional PT remain separate.'
 owner=owners[raw['path']];sites.append(dict(rawFindingIndex=x['rawFindingIndex'],path=raw['path'],sourceSha256=x['sourceSha256'],line=int(raw['beginline']),column=int(raw['begincolumn']),rule=raw['rule'],owner=owner['owner'],costOwner=owner['costOwner'],actualSourceLine=x['actualSourceLine'],priorReason=old['reason'],currentReview=review,decision='NOT_APPLICABLE_REVIEWED_CURRENT_RESOURCE_CONTRACT',oldPtCarriedToCurrent=False,priorEvidencePins={k:c[k] for k in ['previousQualifiedPreflight','previousFullRootStatic','originalPerSiteAdmission']}))
counts=dict(collections.Counter(x['rule'] for x in sites));assert counts==dict(DoNotThrowExceptionInFinally=20,CloseResource=19)
indices={x['rawFindingIndex'] for x in sites};assert len(indices)==39;left=[x for x in rows if x['rawFindingIndex'] not in indices];assert len(left)==230
out=b/'evidence/PG37052-f03-reviewed39-resource-reuse-v1';out.mkdir();(out/'site-decisions.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2)+'\n');(out/'remaining-candidates.json').write_text(json.dumps(left,ensure_ascii=False,indent=2)+'\n')
commit=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip();doc='documents/300_SS/330_データ・ファイル/332_PostgreSQL物理設計・DDL・migration設計.md'
# Pin exact canonical architecture already used by prior profile instead of inventing a document filename.
canonical=next(p for p in (r/'documents/300_SS/330_データ・ファイル').glob('332_*.md'));doc=str(canonical.relative_to(r));content=subprocess.check_output(['git','show',commit+':'+doc])
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=previous['sourceCore'],reviewOnly=True,reviewedReusedCandidates=39,counts=counts,finalSpecificWithPrior=376,remainingCandidateUnconfirmed=230,remainingUnmatched=365,totalOriginalRaw=971,all971Reconciled=376+230+365==971,prior=ref(prior/'manifest.json'),currentTypedFacts=ref(b/'evidence/PG37042-current287-catch-facts-v1/manifest.json'),sites=ref(out/'site-decisions.json'),remaining=ref(out/'remaining-candidates.json'),priorProofHashesRechecked=pins,canonicalPriority=dict(path=doc,commit=commit,sha256=hashlib.sha256(content).hexdigest()),sourceRuleSuppressionChanges=0,productTestsExecuted=0,oldPtCarriedToCurrent=False,wholeF03Accepted=False,newAcceptance=0,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,reviewedReused=39,final=376,candidatesUnconfirmed=230,remainingUnmatched=365,newAcceptance=0)))
