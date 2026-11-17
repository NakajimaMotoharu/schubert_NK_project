"""Review23 complete owned-JDBC close catches implementing one explicit priority helper call."""
from pathlib import Path
import datetime
import hashlib
import json
import re

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
prior=b/'evidence/PG37064-f03-typed-priority72-applicability-v1';previous=load(prior/'manifest.json');left=load(prior/'remaining-unmatched.json');assert len(left)==293
ids={x['rawFindingIndex'] for x in left if x['raw']['rule']=='AvoidCatchingGenericException'};joined=load(b/'evidence/PG37042-current287-catch-facts-v1/joined-facts.json');bodyrows=load(w/'pg37044-current-catch-bodies.json');keys={(x['raw']['path'],int(x['facts']['start'])) for x in joined if x['originalFindingIndex'] in ids};approved={}
for x in bodyrows:
 key=(x['path'],int(x['facts']['start']))
 if key not in keys:continue
 parameter=x['sourceParameter'].split()[-1];compact=re.sub(r'\s+','',x['body']);pattern=r'\{if\((?:JdbcAdmissionFailures\.replace|JdbcResourceFailures\.replace|closeReplace)\([A-Za-z_$][A-Za-z0-9_$]*,'+re.escape(parameter)+r'\)\)(?:\{throw'+re.escape(parameter)+r';\}|throw'+re.escape(parameter)+r';)\}'
 if re.fullmatch(pattern,compact):approved[key]=x
assert len(approved)==23
owners={x['path']:x for x in load(next((r/'documents/400_PGPT/470_PMO').glob('485_*.json')))['artifacts']};sites=[]
for x in joined:
 key=(x['raw']['path'],int(x['facts']['start']))
 if x['originalFindingIndex'] not in ids or key not in approved:continue
 body=approved[key];path=r/key[0];assert sha(path)==x['sourceSha256'];owner=owners[key[0]]
 sites.append(dict(rawFindingIndex=x['originalFindingIndex'],path=key[0],sourceSha256=x['sourceSha256'],line=int(x['raw']['beginline']),column=int(x['raw']['begincolumn']),rule=x['raw']['rule'],resolvedCurrentCatch=x['facts'],fullCatchBody=body['body'],owner=owner['owner'],costOwner=owner['costOwner'],decision='NOT_APPLICABLE_APPROVED_OWNED_JDBC_CLOSE_PRIORITY',reason='This whole catch handles exactly one already-owned JDBC resource close. Its only statement consults the source-defined SS332/343 primary-vs-secondary replacement matrix and, if replacement is required, throws the unchanged cleanup object. Otherwise an existing pending primary remains outgoing with safe secondary handling. It does not treat NPE/Error as a normal operation result, acquire a new resource, retry, log diagnostics or close the borrowed Connection. The generic warning cannot replace this compound failure context with caught-type-only handlers. Current source and typed catch are independently pinned; actual DB/native/all PT remain separate.',doesNotReplaceOwnerFaultMatrixTests=True))
assert len(sites)==len({x['rawFindingIndex'] for x in sites})==46
indices={x['rawFindingIndex'] for x in sites};remaining=[x for x in left if x['rawFindingIndex'] not in indices];assert len(remaining)==247
out=b/'evidence/PG37066-f03-jdbc-close46-applicability-v1';assert not out.exists();out.mkdir();(out/'site-decisions.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2)+'\n');(out/'remaining-unmatched.json').write_text(json.dumps(remaining,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=previous['sourceCore'],reviewOnly=True,wholeCatchBodies=23,newFinalDispositions=46,sourceClasses=7,finalWithPrior=724,remainingUnmatched=247,unconfirmedReuseCandidates=0,totalOriginalRaw=971,all971Reconciled=724+247==971,prior=ref(prior/'manifest.json'),typedFacts=ref(b/'evidence/PG37042-current287-catch-facts-v1/manifest.json'),sites=ref(out/'site-decisions.json'),remaining=ref(out/'remaining-unmatched.json'),sourceRuleSuppressionChanges=0,productTestsExecuted=0,newAcceptance=0,wholeF03Accepted=False,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,wholeCatchBodies=23,newFinal=46,final=724,remaining=247,newAcceptance=0)))
