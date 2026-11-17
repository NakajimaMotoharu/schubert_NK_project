"""Review24 explicit known/unknown JDBC or advisory-handoff cleanup priority sites."""
from pathlib import Path
import datetime
import hashlib
import json

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
prior=b/'evidence/PG37080-f03-owned-alias29-applicability-v1';previous=load(prior/'manifest.json');left=load(prior/'remaining-unmatched.json');selected=[x for x in left if x['raw']['rule']=='DoNotThrowExceptionInFinally'];assert len(selected)==24
owners={x['path']:x for x in load(next((r/'documents/400_PGPT/470_PMO').glob('485_*.json')))['artifacts']};sites=[]
for x in selected:
 raw=x['raw'];path=r/raw['path'];text=path.read_text();lines=text.splitlines();n=int(raw['beginline']);assert sha(path)==x['sourceSha256'] and lines[n-1]==x['actualSourceLine'] and 'finally' in x['actualSourceLine']
 if path.name=='InspectorLockHandoff.java':
  assert 'if (unknownCallback == null) throw new Failure();' in text and 'unknownCallback.addSuppressed(new Failure());' in text
  reason='SS343 handoff must attempt reacquisition/readiness of the original advisory lock in finally after the borrowed callback. Known restoration failure emits fixed Failure only without an unknown callback; otherwise it attaches a fresh fixed secondary and preserves the outgoing unknown callback. Silencing this finally failure could claim a restored parent ownership state without evidence. Actual handoff/lock/DB proof is separate and not executed.'
 else:
  assert any(t in text for t in ['JdbcResourceFailures.replace','JdbcAdmissionFailures.replace','closeReplace'])
  reason='SS332/341/343 owned JDBC close is attempted directly in the explicit finally. Conditional replacement follows the declared known-SQL versus unknown Runtime/Error primary/secondary matrix; it may deliberately let an unknown cleanup escape instead of known SQL or an absent primary. Otherwise the exact outgoing primary and safe suppression remain. Removing a finally throw or mechanically applying TWR would alter that matrix/cleanup uncertainty. The outer finally still attempts its own acquired resource; borrowed parent responsibility remains explicit.'
 owner=owners[raw['path']];sites.append(dict(rawFindingIndex=x['rawFindingIndex'],path=raw['path'],sourceSha256=x['sourceSha256'],line=n,column=int(raw['begincolumn']),rule=raw['rule'],method=raw.get('method'),owner=owner['owner'],costOwner=owner['costOwner'],sourceContext=lines[max(0,n-2):n+13],decision='NOT_APPLICABLE_EXPLICIT_APPROVED_CLEANUP_PRIORITY',reason=reason,actualJdbcHandoffOrNativeTestsReplaced=False))
indices={x['rawFindingIndex'] for x in sites};assert len(indices)==24;remaining=[x for x in left if x['rawFindingIndex'] not in indices];assert len(remaining)==132
out=b/'evidence/PG37082-f03-required-finally24-applicability-v1';assert not out.exists();out.mkdir();(out/'site-decisions.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2)+'\n');(out/'remaining-unmatched.json').write_text(json.dumps(remaining,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=previous['sourceCore'],reviewOnly=True,newFinalDispositions=24,finalWithPrior=839,remainingUnmatched=132,unconfirmedReuseCandidates=0,totalOriginalRaw=971,all971Reconciled=839+132==971,prior=ref(prior/'manifest.json'),sites=ref(out/'site-decisions.json'),remaining=ref(out/'remaining-unmatched.json'),sourceRuleSuppressionChanges=0,productTestsExecuted=0,actualRootNativeRecoveryOrDbOperations=0,newAcceptance=0,wholeF03Accepted=False,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,finallySites=24,final=839,remaining=132,newAcceptance=0)))
