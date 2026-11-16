"""Classify exactly source-reviewed primitive-state/same-object rethrow bodies, not generic catches en masse."""
from pathlib import Path
import datetime
import hashlib
import json
import re

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
prior=b/'evidence/PG37040-f03-specific38-applicability-v1';previous=load(prior/'manifest.json');remaining=load(prior/'remaining-unmatched.json');fp=b/'evidence/PG37042-current287-catch-facts-v1/manifest.json';facts=load(fp);assert facts['actualExit']==0 and facts['joinedWarnings']==261 and previous['remainingUnmatched']==455
joined=load(fp.parent/'joined-facts.json');bodies=load(w/'pg37044-current-catch-bodies.json');approved={}
for x in bodies:
 f=x['facts'];parameter=x['sourceParameter'].split()[-1];body=re.sub(r'//[^\n]*|/\*.*?\*/','',x['body'],flags=re.S)
 pattern=r'\{\s*(?:[A-Za-z_$][A-Za-z0-9_$]*\s*=\s*(?:true|false|'+re.escape(parameter)+r')\s*;\s*)*throw\s+'+re.escape(parameter)+r'\s*;\s*\}'
 if not re.fullmatch(pattern,body):continue
 assert f['finalDirect']=='true' and f['sameThrows']=='1' and all(f[k]=='0' for k in ['otherThrows','returns','assignments','breaks','continues'])
 assert 'java.lang.RuntimeException' in f['type'] or 'java.lang.Error' in f['type']
 approved[(x['path'],int(f['start']))]=x
assert len(approved)==34
owners={x['path']:x for x in load(next((r/'documents/400_PGPT/470_PMO').glob('485_*.json')))['artifacts']};sites=[]
for x in joined:
 key=(x['raw']['path'],int(x['facts']['start']))
 if key not in approved:continue
 a=approved[key];path=r/key[0];assert sha(path)==x['sourceSha256'] and facts['sourceInputs'][key[0]]==x['sourceSha256'];source=path.read_text();assert source[int(x['facts']['start']):int(x['facts']['end'])]==a['sourceParameter']
 owner=owners[key[0]];sites.append(dict(rawFindingIndex=x['originalFindingIndex'],path=key[0],sourceSha256=x['sourceSha256'],line=int(x['raw']['beginline']),column=int(x['raw']['begincolumn']),rule=x['raw']['rule'],resolvedType=x['facts']['type'],method=x['facts']['method'],parameter=a['sourceParameter'],fullCatchBody=a['body'],owner=owner['owner'],costOwner=owner['costOwner'],decision='NOT_APPLICABLE_IDENTICAL_THROWABLE_RETHROW',reason='Full body inspected: only unqualified local/this primitive-state or primary-reference assignments followed by exactly one throw of the unchanged caught symbol. No method invocation, allocation, wrapping, normal return, parameter reassignment or nested scope. Broad union preserves RuntimeException/Error identity while recording poison/ownership/rollback state, as required by SS311/333/341/342/343/354. It never catches NPE/Error as normal success. Callee/finally/actual-native/transaction quality remains governed by separate original owner tests.',doesNotProveFinallyCleanupOrRuntimeNative=True))
assert len(sites)==66 and len({x['rawFindingIndex'] for x in sites})==66
indices={x['rawFindingIndex'] for x in sites};left=[x for x in remaining if x['rawFindingIndex'] not in indices];assert len(left)==389
out=b/'evidence/PG37046-f03-same-rethrow66-applicability-v1';assert not out.exists();out.mkdir();(out/'site-decisions.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2)+'\n');(out/'remaining-unmatched.json').write_text(json.dumps(left,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=facts['sourceCore'],reviewOnly=True,reviewedFullCatchBodies=34,newSpecificFinal=66,finalSpecificWithPrior=273,oldCandidateUnconfirmed=309,remainingUnmatched=389,totalOriginalRaw=971,all971Reconciled=273+309+389==971,prior=ref(prior/'manifest.json'),currentTypedFacts=ref(fp),sites=ref(out/'site-decisions.json'),remaining=ref(out/'remaining-unmatched.json'),sourceRuleSuppressionChanges=0,productTestsExecuted=0,wholeF03Accepted=False,newAcceptance=0,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,catchBodies=34,newFinal66=True,final=273,candidatesUnconfirmed=309,remainingUnmatched=389,newAcceptance=0)))
