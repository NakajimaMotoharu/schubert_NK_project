"""Review seven single-owner visibility booleans; do not infer correctness of real DB/handoff paths."""
from pathlib import Path
import datetime
import hashlib
import json
import re

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
prior=b/'evidence/PG37076-f03-memory-monitor15-applicability-v1';previous=load(prior/'manifest.json');left=load(prior/'remaining-unmatched.json');selected=[x for x in left if x['raw']['rule']=='AvoidUsingVolatile'];assert len(selected)==7
reason={
 'active':'Owner-lifetime tombstone: constructor true, outer owned release writes false only. Visibility is needed so a stale capability refuses work; there is no read-modify-write operation or counter.',
 'backupCommitted':'One-owner committed-state publication. It becomes true only on accepted commit/completion paths and is never reset; source contract admits no competing transaction writers.',
 'handoffStarted':'One-way same-owner cleanup handoff admission flag. Captured-thread guard plus inHandoff reentry refusal supplies operation exclusivity; volatile is visibility, not a substitute for concurrent compare-and-set.',
 'inHandoff':'Captured owner thread enters/exits the scoped borrowed-connection handoff; guard rejects ordinary reentry. True/false writes are plain publication and finally restoration, not a contested compound update.',
 'backupFinished':'One-owner published Backup completion condition. Mutually exclusive approved paths only set true; actual Backup/DB postconditions are not supplied by this field or static review.',
 'cleanupVerified':'One-way publication after the owner verifies cleanup sequence. Plain boolean visibility is needed, no arithmetic/collection mutation or RMW atomicity is claimed.',
 'expiryHandoffStarted':'One-way owner-thread Expiry handoff admission, guarded by prior cleanup state and existing single-owner/reentry contract. CAS would not establish transaction/authority ownership and is not required for a plain publication flag.'}
owners={x['path']:x for x in load(next((r/'documents/400_PGPT/470_PMO').glob('485_*.json')))['artifacts']};sites=[];seen=set()
for x in selected:
 raw=x['raw'];path=r/raw['path'];text=path.read_text();assert path.name=='MorningDatabaseSession.java' and sha(path)==x['sourceSha256'] and text.splitlines()[int(raw['beginline'])-1]==x['actualSourceLine']
 match=re.search(r'private volatile boolean (\w+)',x['actualSourceLine']);assert match;field=match[1];assert field in reason and field not in seen;seen.add(field)
 assert 'private final long thread = Thread.currentThread().threadId();' in text and 'if (!active || inHandoff || thread != Thread.currentThread().threadId()) throw unavailable();' in text
 assert not re.search(r'\b'+field+r'\s*(?:\+\+|--|\+=|-=|\|=|&=)',text)
 writes=[dict(line=i+1,sourceLine=line.strip()) for i,line in enumerate(text.splitlines()) if re.search(r'\b'+field+r'\s*=(?!=)',line)];assert writes
 owner=owners[raw['path']];sites.append(dict(rawFindingIndex=x['rawFindingIndex'],path=raw['path'],sourceSha256=x['sourceSha256'],line=int(raw['beginline']),column=int(raw['begincolumn']),rule=raw['rule'],field=field,owner=owner['owner'],costOwner=owner['costOwner'],writes=writes,decision='NOT_APPLICABLE_SINGLE_OWNER_VISIBILITY_FLAG',reason=reason[field]+' JMM volatile provides primitive read/write visibility/order; this use does not depend on unsupported atomic counter/compound update semantics. SS341/343 current session contract is one captured actor with borrowed JDBC ownership, not a concurrently shared transaction object. All actual concurrent/lifetime/DB/native owner tests and before/after authority remain separate obligations.',runtimeOrConcurrentTestsReplaced=False))
assert seen==set(reason)
indices={x['rawFindingIndex'] for x in sites};remaining=[x for x in left if x['rawFindingIndex'] not in indices];assert len(remaining)==185
out=b/'evidence/PG37078-f03-owner-visibility7-applicability-v1';assert not out.exists();out.mkdir();(out/'site-decisions.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2)+'\n');(out/'remaining-unmatched.json').write_text(json.dumps(remaining,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=previous['sourceCore'],reviewOnly=True,newFinalDispositions=7,sourceClasses=1,finalWithPrior=786,remainingUnmatched=185,unconfirmedReuseCandidates=0,totalOriginalRaw=971,all971Reconciled=786+185==971,prior=ref(prior/'manifest.json'),sites=ref(out/'site-decisions.json'),remaining=ref(out/'remaining-unmatched.json'),sourceRuleSuppressionChanges=0,productTestsExecuted=0,actualRootNativeOrRecoveryOperations=0,newAcceptance=0,wholeF03Accepted=False,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,visibilityFields=7,final=786,remaining=185,newAcceptance=0)))
