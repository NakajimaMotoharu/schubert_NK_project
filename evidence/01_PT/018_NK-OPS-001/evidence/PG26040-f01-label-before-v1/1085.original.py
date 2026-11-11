"""F01 nonexecutable policy criteria; does not grant code/F03/full-WBS acceptance."""
from pathlib import Path
import datetime as dt,hashlib,json,re,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26038-f01-policy-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
master=load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json');f=next(v for v in master['tasks'] if v['id']=='WBS-F01')
assert f['ownedArtifacts']==f['sharedClassReferences']==f['requirementIds']==[] and f['dependencies']==[]
assert f['acceptance']['status']=='ACCEPTED' and {v['id'] for v in f['acceptanceChecks']}=={'WBS-F01:contract','WBS-F01:scope','WBS-F01:quality'}
paths=['documents/400_PGPT/410_工程標準/411_コーディング規約.md','documents/400_PGPT/450_品質/451_Build・静的解析・coverage方針.md','documents/400_PGPT/430_構成・追跡/431_Module・Program一覧.md']
pins={};text={}
for p in paths:
 data=(R/p).read_bytes();t=data.decode('utf-8');assert b'\r' not in data and data.endswith(b'\n')
 assert data==subprocess.check_output(['git','show',head+':'+p]);pins[p]=sha(R/p);text[p]=t
policy=text[paths[0]];quality=text[paths[1]]
topics={
 'priority-source':('## 1. 適用範囲と優先順位',['RD、UI、SS','`src`','`program/characterization`']),
 'java-naming':('## 2. Java 25・命名',['preview','UpperCamelCase','lowerCamelCase','UPPER_SNAKE_CASE']),
 'module':('## 3. Module依存',['schubert-nk-protocol','schubert-nk-storage','schubert-nk-bootstrap','schubert-nk-api','schubert-nk-web','schubert-nk-batch','Web→業務API禁止']),
 'null':('## 4. Null・invariant',['Nullability','Objects.requireNonNull','NullPointerException']),
 'transaction-exceptions':('## 5. 例外・transaction',['Outbox','Inbox','rollback','QA050']),
 'redaction-security':('## 6. Logging・redaction・security',['DIF-016','CSRF','deny-by-default','HMAC']),
 'sql':('## 7. SQL・DDL',['bind parameter','append-only','OffsetDateTime','0001～9999']),
 'codec':('## 8. 固定長codec',['256-byte','64 layout','NFC','golden vector']),
 'concurrency':('## 9. 並行処理・JMS・file',['private final lock','Inbox/Outbox','atomic rename']),
 'testability':('## 10. Testability・test規約',['独立算出','not-run','100%','全資源後条件']),
 'format-static':('## 11. Format・静的解析',['Spotless','NullAway','SpotBugs','Checkstyle']),
 'prohibited':('## 12. 禁止事項',['Force push','既存未commit変更','NPE正常扱い']),
 'review-trace':('## 13. Review checklist',['trace','canonicalOwner','canonicalCostOwner']),
 'history':('## 14. 更新履歴',['2026-09-01'])}
topicEvidence=[]
for name,(heading,words) in topics.items():
 start=policy.index(heading);end=policy.find('\n## ',start+len(heading));section=policy[start:end if end!=-1 else len(policy)]
 assert all(w in section for w in words),(name,words)
 topicEvidence.append(dict(topic=name,path=paths[0],line=policy[:start].count('\n')+1,independentReviewBasis=words))
assert all(v in quality for v in ['MissingClass','ClassStats','-Xlint:all -Werror','Line 100%','method 100%','class 100%','branch 100%','Failed','flaky','skipped','NullAway','Current baseline'])
designPins={}
for p in f['evidencePlan']['designFiles']:
 raw=subprocess.check_output(['git','show','origin/main:'+p]);assert (R/p).read_bytes()==raw
 designPins[p]=dict(approvedMain=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),sha256=hashlib.sha256(raw).hexdigest())
oldSource=f['acceptance']['source'];deltas={p:subprocess.check_output(['git','diff','--numstat',oldSource,'--',p],text=True).strip() for p in paths}
# Only existing public static descriptors and Git names; no classfile/native/Root Test content.
child=subprocess.run(['python3','-B','tools/quality/wbs_progress_audit.py','--current-source-structure-only'],capture_output=True,text=True,timeout=30)
assert child.returncode==0;structure=json.loads(child.stdout);assert structure['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5' and structure['runtimeQualified'] is False
assert not O.exists();O.mkdir()
checks=[dict(id='WBS-F01:contract',status='SATISFIED_NONEXECUTABLE_POLICY_SCOPE',basis='All fourteen policy sections reviewed against SS311/354/current six module responsibilities; code conformance remains F03.',testIds=['PT-QUALITY-FOUNDATION001'],evidence=topicEvidence),dict(id='WBS-F01:scope',status='SATISFIED_NONEXECUTABLE_POLICY_SCOPE',basis='Owned Java/DDL/config artifacts, requirements and shared classes empty by current F01 definition. Policy only, no added code denominator or duplicate common cost.'),dict(id='WBS-F01:quality',status='SATISFIED_POLICY_WITH_CODE_QUALITY_SEPARATE',basis='UTF8/LF/final newline and committed bytes; quality gates retain strict static/null/FES/coverage requirements. Runtime/negative/rollback/concurrency tests are N-A for policy text, not exempt for code.')]
v=dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),source=head,productionCoreMain=structure['source'],policyHashes=pins,approvedDesigns=designPins,previousAcceptedSource=oldSource,changesSincePriorAcceptance=deltas,criteria=checks,scope='NONEXECUTABLE_F01_ONLY',decision='POLICY_CRITERIA_REVIEW_COMPLETE_EXISTING_ACCEPTANCE_REQUALIFICATION_ONLY',existingAcceptanceStatusRetained='ACCEPTED',globalWbsAcceptanceUpdated=False,F03Accepted=False,whole451Accepted=False,staticStructure=structure,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,policyTopics=14,criteria=3,newAcceptance=0,manifestSha256=sha(O/'manifest.json'))))
