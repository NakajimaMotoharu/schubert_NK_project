"""Public Scenario contracts and before-fix fatal-conversion evidence; product execution zero."""
from pathlib import Path
import datetime, hashlib, json, re, subprocess
R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001'; D=R/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p))
O=B/'evidence/PG26838-scenario-replay-contract-v1'; assert not O.exists()
t=next(x for x in load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks'] if x['id']=='WBS-P008-02')
assert len(t['ownedArtifacts'])==4
own={p:sha(R/p) for p in t['ownedArtifacts']}
normal=load(B/'evidence/PG22106-api-stop-static-independent-input-v1/normal.json')
assert all(normal['begin']['inputHashes'][p]==h for p,h in own.items())
path=next(p for p in own if p.endswith('/ScenarioReplayService.java')); text=(R/path).read_text()
sites=[]
for m in re.finditer(r'catch\s*\(([^)]*)\)\s*\{\s*throw new TemporaryInfrastructureException\(\);\s*\}',text):
 sites.append(dict(line=text.count('\n',0,m.start())+1,catchTypes=m.group(1),body=m.group(),method=max((n for n in re.finditer(r'public (?:InboxCompletion|Snapshot|byte\[\]) (\w+)\(',text[:m.start()])),key=lambda n:n.start()).group(1)))
assert [s['method'] for s in sites]==['captureSuccess','captureFailure','read','replaceFile','reply','failure']
main=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip()
designs={}
for p in ['documents/300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md',t['evidencePlan']['designFiles'][0]]:
 data=subprocess.check_output(['git','show',main+':'+p]); designs[p]=dict(commit=main,sha256=hashlib.sha256(data).hexdigest())
 assert ('捕捉したfinite exception graph' in data.decode()) if '/312_' in p else ('### 6.3 Scenario保存結果の検証' in data.decode())
admission=[]
for p in t['evidencePlan']['candidateTestFiles']:
 s=(R/p).read_text(); reasons=[n for n in ['ResponseSnapshotCodec','FingerprintKeyRing','ApiLogDatabaseFixture'] if n in s]
 if p.endswith('/ScenarioAuditWriterTest.java'):
  assert not reasons; reasons=['ScenarioRequest direct FingerprintKeyRing typed footprint; target TemporaryInfrastructureException transitive boundary not admitted']
 assert reasons
 admission.append(dict(path=p,sha256=sha(R/p),tests=s.count('@Test'),wholeBodyReviewed=p.endswith('/ScenarioAuditWriterTest.java'),status='WHOLE_FIXTURE_HOLD_NO_METHOD_EXTRACTION',reasons=reasons))
checks=[
 dict(id='P00802-PG01',methods='Assembly.standard; Service.process/read/prepare/finish/transaction',testIds=['PT-SCN-010..014','PT-SCN-009-S01..S06'],expected='Decode before stage; private sameMessage serializer spans readonly fresh-actor/Inbox snapshot, file preparation outside TX, then final writable fresh actor same owner and Inbox arbitration. Lock/root acceptance remains separate. Borrowed snapshots grant no authority; prepare failure/final session rejection never persistent success. NEW captures successful query and critical audit atomically; replay neither requery nor duplicate audit except missing-file regeneration with owner/content verification and descriptor CAS. Connection owned commit/rollback/close failures stay infrastructure; no file I/O inside DB TX.'),
 dict(id='P00802-PG02',methods='Replay.captureSuccess/captureFailure/read/replaceFile/reply/failure',testIds=['PT-SCN-009-S01..S06'],expected='Original fixed header+DATA+records AES snapshot bound to requestMessage/responseLayout001/owner; completed_at micros agrees captured header millis. Persist success0000 or definite9001/SCN0104 only; 0102/9000 never persisted. Decrypt validates whole header,length,semantic,layout/ref/state/code/time/owner/script identity. Successful replay0200 only; failure originalcode. Fresh message/sentAt/current context/requestMessage correlation. Replace only verified equal-content file descriptor, preserve original state/ref/header/time. Wipe decrypted body/DATA/records. SS312 fatal graph must be inspected BEFORE fixed exception conversion; six current catches violate this source contract.'),
 dict(id='P00802-PG03',methods='AuditWriter.write/username',testIds=['PT-SCN-AUD469003..006'],expected='SRCREQ01 -> SCENARIO_SEARCHED with explicit totalCount; SCNREQ01 -> SCENARIO_VIEWED with INLINE record count or FILE fileRecordCount. Other four list queries no statement. Borrowed TX only, owned statement exactly one close and insert exactly1; all SQL faults reach caller. API ACTION INFO; request message/correlation, actor id/NFC username with CR LF TAB U2028 U2029 replaced by spaces; JSON only layout/resultCount. No body/filter/path/context/key/credential; failure rolls back by Service, not audit writer.')]
O.mkdir()
before=dict(actualExit=0,source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain='62960fc3b5d4a67cf7bd9df887b668169d10f87f',path=path,sourceSha256=own[path],sites=sites,designs=designs,productTestsExecuted=0,bug='BUG-2679',horizontal='YKT-2359',runtimeAdmission='HOLD_ACTUAL_FOUR_AND_DB',sourceOnlyFinding=True)
write(O/'fatal-conversion-before.json',before)
for filename,prefix,maximum,body in [
 ('915_障害表.md','BUG',2678,'## BUG-2679（PG、2026-11-12、Scenario replay六変換でwrapped fatal消失、修正前）\n\n対象ScenarioReplayService.captureSuccess/captureFailure/read/replaceFile/reply/failure、P00802-PG02/PT-SCN-009-S01..S06。重要度高/優先高。期待=SS312 §3有限cause/suppressed/SQL next内Errorを元objectで固定catalog変換前に伝播。実際=六catchが原因graphを確認せずnew TemporaryInfrastructureException()へ置換、外側Serviceは元Errorを失う。公開sourceの各catch/ResponseSnapshotException cause保持とSS312で再現条件を確認、実運転再現は未実行/HOLD。原因=非SQL snapshot/codec例外変換への共通規則適用漏れ。影響=この六経路、全域一般化しない。既BUG1592/YKT1345はSQL分類/plan6580に当六site無し、YKT1323もordinary send cleanup対象で本六を代替しない。関連FUN003～005/FIL001～009、UI223/224/234/237、SS312/324、YKT-2359、設計変更/QA不要。原状証跡PG26838/fatal-conversion-before.json、修正前記録。修正候補=既共有portを六変換前に接続、診断redaction不変更。修正commit/独立PT/coverage未実施、状態OPEN/完了日未定。actual4 binary/DB/Root操作0。'),
 ('916_横展開管理台帳.md','YKT',2358,'## YKT-2359（PG、2026-11-12、BUG2679、Scenario snapshot非SQL固定catalog六変換）\n\n共通原因=wrapped fatal分類前の原因破棄。検索条件=当P00802 owned ReplayServiceの全catchとnew TemporaryInfrastructureException、対象一覧captureSuccess/captureFailure/read/replaceFile/reply/failure（PG26838原状six sites）。Service/Repositoryは既preserveFatalを使用、AuditWriterはSQL再throwで変換しないためこの局所原因は対象外。ResponseSnapshotExceptionはcause保持、Codec source側cause保持のため新Codec修正を重複追加しない。SQL既YKT1345/非SQLsend既1323の完了へ紛れ込ませず本六を別管理、全API非SQL全域は未完のまま。修正前起票。追加check=各変換前共有port接続のsource/static、元Error identity/finite cycle/ordinary redactionは独立PT必要だがactualTemporary/Codec等のruntime・compile HOLDの間は未実施とする。検索だけで完了しない。関連SS312/324、修正commit/再試験未定、状態OPEN。')]:
 p=R/'documents/900_OTHER/910_台帳'/filename; s=p.read_text(); assert max(map(int,re.findall(prefix+r'-(\d{3,})',s)))==maximum
 first,rest=s.split('\n',1);p.write_text(first+'\n'+body+'\n\n'+rest)
v=dict(actualExit=0,atJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),source=before['source'],productionCoreMain=before['productionCoreMain'],ownedSourceHashes=own,designs=designs,checks=checks,candidateAdmission=admission,fatalConversionFinding=ref(O/'fatal-conversion-before.json'),wholeOwnSourceReviewed=True,completedOriginalPreparationWorkIds=['WBS-P008-02/1'],endingStatus='NOT_ACCEPTED_BUG2679_RUNTIME_ACTUAL4_DB_AND_EXIT_DEPENDENCIES',MainOrTestChanged=False,productTestsExecuted=0,newDefinitions=0,newAcceptance=0,whole451Accepted=False,formalUpdated=False,effortRate=None,actualBackendAndHeldClassBinaryActions=0,verifier=ref(Path(__file__).resolve()))
write(O/'manifest.json',v)
print(json.dumps(dict(actualExit=0,own4=True,newBug=2679,newYkt=2359,productTestsExecuted=0,manifest=ref(O/'manifest.json'))))
