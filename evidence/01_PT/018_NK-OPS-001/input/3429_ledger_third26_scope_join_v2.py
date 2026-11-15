"""Explicit historical scope decisions from already public evidence, no product execution."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';p=b/'evidence/provisional';e=b/'evidence/PG33718-ledger-third26-scope-join-v1';i=b/'input';load=lambda x:json.loads(x.read_text());sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
assert not e.exists();plan=load(i/'3425_ledger_third26_plan.json');ledger=r/'documents/900_OTHER/910_台帳/915_障害表.md';original=ledger.read_text();sections={int(m.group(1)):m.group(0) for m in re.finditer(r'^## BUG-(\d+)\b.*?(?=^## BUG-|\Z)',original,re.M|re.S)}
bindings={
1389:('PG4848-ssc301302-selected-v1/manifest.json','Host PostgreSQL path fixture: original59/10 FES0, toolchain path correction only; current actual DB HOLD preserved.',1155),
1390:('PG4946-current-physical-trace-v1/manifest.json','Historical941/current941 physical trace and two relocation scope; semanticG13/current-source/global not accepted.',1156),
1435:('PG5262-scope-classification-backup-worker-v2/manifest.json','Metadata legacy fixed count description only; original v1 retained; no Production or candidate semantic acceptance.',1199),
1436:('PG5266-morning-backup-bytecode-v1/manifest.json','Exact40hex source pin corrected and original post0; not a current backend/coverage qualification.',1200),
1538:('PG6082-web-factory-qualification-v1/manifest.json','Historical fixture compiler/serial contract corrected; old Web925 source only, current SDK/whole graph HOLD.',1298),
1581:('PG6442-morning-diagnostic-qualification-v1/manifest.json','CompletionProgress protected failure notification direct scope; Progress L18/M4/C1/B4 allmiss0. Wider YKT1320/Root retain unaccepted.',None),
1582:('PG6450-morning-sequence-qualification-v1/manifest.json','Fixed two-owner preallocation direct scope, original23/sequence counter proof; actual OOM/native and widerYKT1335 unaccepted.',None),
1741:('PG9216-api-factory-debug-trace-v1/manifest.json','Measurement reader current session accepted/old rejected, no product replay; whole four100 false retained.',1492),
1744:('PG9254-web-life-lock-metrics-v2/manifest.json','Output-v2 event recorded once using readonly old quota input; original failed OUT retained, no new product success.',1495),
1752:('PG9604-explicit-case-row-post-v2/correction-post.safe.json','Header spec token correction explicitly BUG1752; independent v2 post and eight metadata negatives, no oracle semantics/PT qualification.',1503),
1880:('PG10902-web-boundary-post-v1/manifest.json','Historical Web preflight dependency classification, original source snapshots and final independentpost; CP presence is not SDK execution permission.',1631),
1881:('PG10855-web-view-post-recovery-v1/manifest.json','Independent post old counterexample metadata correction; original product success retained, no fresh run.',1632),
1882:('PG10902-web-boundary-post-v1/manifest.json','Historical boundary constants Test-only value identity; actual per-locale8, 12 source negatives; globalJava four100false retained.',1633)}
reported={1245:'Original title/817 reports fixture/full historical closure; public selected11 available, original full2694/2695 public manifest not found. Do not replay broker or requalify full.',1384:'Original1013 reports full11 mapper actual4758/4756/4760 closure; original actual private proof unavailable in permitted public roots. Preserve historical report, no VM/readback retry.',1385:'Original1015/1016 reports SAVE/RAW_SAVE namespace correction and subsequent owned post; private actual receipts not accessed. Preserve historical report only.',1386:'Original1016 reports selector correction and actual4778 post; public native summary cannot itself prove selector contract. No stop/post/VM operation.',1387:'Original4824/4826 records nested graph tool closure; original public compiler/stage manifest not found. No SDK/class materialization or stage retry.',1393:'Original1030 reports browserguard release correction and historical12 Browser/owned stop/native chain; current Browser/VM not requalified, no private access.',1598:'Original1460 reports three sender/full4158 closure; public6632 selected86/17 exists but currentWholePending true, full6636 public manifest not found. Historical closure retained, no current qualification transfer.'}
pending={1467:'Capacity chain tool: no original public actual preflight/geometry/full11 proof found. Source/environment correction not re-executed; VM/storage HOLD.',1470:'Original failedRoot30/source0ea remains distinct from later candidates. No current same-run cause/fix/owned post proof; actual Root/cohort HOLD.',1574:'Startup UNKNOWN retention direct scope has no matched public source/PT receipt in this review. Foreign BUG1564/1565 closed paragraphs are not1574 proof. No runtime/child/Root retry.',1583:'Fixture generic Boolean compiler repair recorded before6480, subsequent serial warnings fail. Original successful6486/6488 public manifest not found; retrieve permitted saved evidence before any runtime action.',1584:'Fixture broad close compiler warning: correction planned but successful6486/6488 public manifest not found here. Do not infer complete from other six dependency tests; SDK fixture execution HOLD.',1746:'Public9338 metadata hash correction0 explicitly bugClosedfalse and wholeWbsAudit exit1/currentWIP mismatch. Preserve partial metadata fix and whole canonical scope HOLD.'}
assert set(bindings)|set(reported)|set(pending)==set(plan['targetBugIds']);assert not(set(bindings)&set(reported) or set(bindings)&set(pending) or set(reported)&set(pending))
proof={};rows=[]
def get(name):
 f=p/name;assert f.is_file() and not f.is_symlink();v=load(f);proof[name]=dict(path=str(f.relative_to(r)),sha256=sha(f));return v
for n,(path,reason,ykt) in bindings.items():
 v=get(path)
 if n==1435:assert v['metadataCorrection']=='BUG1435: fixed legacy count text only; original v1 retained' and v['acceptedLeafDelta']==0
 else:assert v['actualExit']==0
 if n==1389:assert v['tests']==59 and v['suites']==10 and v['actualMavenExit']==0 and not v['wholeProgramCoverage100']
 if n==1390:assert type(v['approvedRelocations']) is int and v['approvedRelocations']==2 and v['acceptedLeafDelta']==0 and v['productionChanges']==0
 if n==1436:assert re.fullmatch('[0-9a-f]{40}',v['source']) and v['source']=='4661101cae269ae709343282f029c5894d97fb95'
 if n==1538:assert v['tests']==925 and v['checkstyleFindings']==0 and v['originalSixSpotBugs']==0
 if n==1581:
  c=v['targetCounters']['batch:dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner$CompletionProgress.class'];assert all(c[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH']);assert c['LINE']['covered']==18 and c['BRANCH']['covered']==4
 if n==1582:assert v['source']=='bbbc3f7f13b6858535515dc495ad53839683fb24' and v['tests']==23
 if n==1741:assert v['bug1741Retest']=='CURRENT_SESSION_ACCEPTED_OLD_SESSION_REJECTED_NO_PRODUCT_REPLAY' and not v['requiredWholeClassFour100']
 if n==1744:assert v['eventId'] and not v['programPtComplete'] and not v['formalUpdated']
 if n==1752:
  assert v['bug']=='BUG-1752';q=get('PG9604-explicit-case-row-post-v2/manifest.json');assert q['actualExit']==0 and len(q['metadataCounterexamples'])==8 and q['productTestsExecuted']==0
 if n==1882:assert v['testsPerLocale']==8 and v['independentSourceNegativeVectors']==12 and not v['wholeJavaCoverage100']
 rows.append(dict(bug=n,disposition='HISTORICAL_LIMITED_SCOPE_VERIFIED_STATUS_SYNC',reason=reason,ykt=ykt,proof=proof[path],originalSectionSha256=hashlib.sha256(sections[n].encode()).hexdigest(),newProductTests=0,newAcceptance=0))
for bucket,label in [(reported,'HISTORICAL_COMPLETION_REPORTED_PUBLIC_FULL_PROOF_UNCONFIRMED'),(pending,'OPEN_OR_PARTIAL_HOLD_NOT_REQUALIFIED')]:
 for n,reason in bucket.items():rows.append(dict(bug=n,disposition=label,reason=reason,originalSectionSha256=hashlib.sha256(sections[n].encode()).hexdigest(),newProductTests=0,newAcceptance=0))
q=get('PG9338-wbs-reference-metadata-post-v1/manifest.json');assert q['bug']=='BUG-1746' and not q['bugClosed'] and q['wholeWbsAudit']['actualExit']==1
# Typed positive/negative metadata vectors, not production PT.
valid_count=lambda value:type(value) is int and value==2
assert valid_count(2) and not valid_count([1,2]) and not valid_count(3)
yktcheck=(r/'documents/900_OTHER/910_台帳/916_横展開管理台帳.md').read_text()
for _,_,no in bindings.values():
 if no is not None:assert re.search(r'^## YKT-'+f'{no:03d}'+r'\b',yktcheck,re.M)
e.mkdir();v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source='fb1783d3dfb1a2e850b81be50ec26b3949ccc398',productionCoreMain='fb1783d3dfb1a2e850b81be50ec26b3949ccc398',lastQualifiedMigrationCore='ef461eba8bea80b4ed17f52d832094c139fef122',lastQualifiedMigrationUnit='a48eec601dfeeb623e2ed073445b906e3560104a',newPgcopy='SOURCE_ONLY_UNCOMPILED_PT_HOLD',rows=sorted(rows,key=lambda x:x['bug']),proofRefs=list(proof.values()),reviewed=26,limitedSync=13,historicalReportedButPublicUnconfirmed=7,openPartialHold=6,totalOriginalReviewed=78,remainingOriginalUnreviewed=147,globalBug2999='OPEN',productTestsExecuted=0,newAcceptance=0,coverage=None,whole451Accepted=False,formalUpdated=False,effortRate=None,noPrivateVmDbSdkClassOrHeldOperation=True,ledgerWrittenAfterAllAssertions=True,bug3007CorrectedTypedCount=True,metadataShapeVectors=3)
(e/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
for row in sorted(rows,key=lambda x:x['bug']):
 n=row['bug'];section=sections[n];header,rest=section.split('\n',1)
 status=('CLOSED（既存の歴史限定scopeのみ）' if n in bindings else '歴史完了記録あり・公開全証拠未照合（新規CLOSED認定なし）' if n in reported else 'OPEN/partial/HOLD（元条件未完又は保存証拠未確認）')
 note='\n\n2026-11-15 scope照合現況: '+status+'。'+row['reason']+' PG33718へ元section/hash/公開proofを結合。元OPEN/外国BUG段落は履歴保持、新試験/新source受入0。\n'
 original=original.replace(section,header+note+rest,1)
ledger.write_text(original)
ykt=r/'documents/900_OTHER/910_台帳/916_横展開管理台帳.md';ys=ykt.read_text()
for n,(_,reason,no) in bindings.items():
 if no is None:continue
 match=re.search(r'^## YKT-'+f'{no:03d}'+r'\b.*?(?=^## YKT-|\Z)',ys,re.M|re.S);assert match is not None
 sec=match.group(0);header,rest=sec.split('\n',1);ys=ys.replace(sec,header+'\n\n2026-11-15 PG33718歴史限定状態CLOSED: 元BUG'+str(n)+'の上記scopeだけ元公開manifest/hash/固有後条件で照合。'+reason+' 元他対象/未実行/HOLD/失敗は保持、新試験/新受入0。\n'+rest,1)
ykt.write_text(ys)
print(dict(actualExit=0,reviewed=26,limitedSync=13,reportedUnconfirmed=7,openPartial=6,originalReviewed=78,remaining=147,productReplay=0))
