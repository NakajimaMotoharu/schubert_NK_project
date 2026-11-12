"""Publish P00702 preparation delta, preserve original fees and unaccepted endings."""
from pathlib import Path
import copy, datetime, hashlib, json
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';D=R/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';P=R/'evidence/01_PT/007_NK-AUT-001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
old=D/'728_WBS65予実・Login十sourceとPW六件後版59.json';f=copy.deepcopy(load(old));m=B/'evidence/PG26724-two-session-contract-v1/manifest.json';a=load(m);assert a['actualExit']==0
out=D/'731_WBS65予実・最大二session原三source後版60.json';assert not out.exists()
f.update(revision='WBS65-EXEC-FORECAST-60-SESSION3_PREPARATION',atJST=a['atJST'],previousForecast=ref(old))
wid='WBS-P007-02/1';assert wid not in f['completedPlanWorkIds'];f['completedPlanWorkIds'].append(wid);f['completedPreparationWorkIds'].append(wid)
for k,x in dict(low=.087,base=.227,high=.455).items():
 f['completedPlanPriceSumPp'][k]=round(f['completedPlanPriceSumPp'][k]+x,3)
 f['remainingOriginalPlanPricePp'][k]=round(f['remainingOriginalPlanPricePp'][k]-x,3)
 f['revisedRemainingPp'][k]=round(f['revisedRemainingPp'][k]-x,3)
f['partiallyCompletedPlanWorkIds'].append('WBS-P007-02')
for k in ['canonicalSchedulePricePrefixBasePp','startedRowPriceSumBasePp']:f[k]=round(f[k]+.65,3)
technical=dict(kind='P00702_OWN3_CONTRACT_SOURCE_AND_HISTORICAL_TARGET_BINDING',evidence=ref(m),ownSources=3,retainedIssueOriginal8=True,retainedAuditOriginal9=True,productTestsExecuted=0,MainOrTestChanged=False,newAcceptance=0)
f['latestGroupTechnicalResult']=technical
f['individualDecisions'].append(dict(id='WBS-P007-02',preparation='COMPLETED_ONLY_625_ROW_1',ending='NOT_ACCEPTED',evidence=ref(m),reason='Own3/publicSQL/oracles and whole candidate sources reviewed; historical issuance8/audit9 target source/Test/physicalCRC identical retained without replay. Real DB concurrency and transaction/SDK/current dependency qualifications remain unaccepted. Provider application-marker origin not fully tested, no assertion of complete exception matrix.'))
f['remainingPriceAccountingNote']='P00702/1 original .087/.227/.455 preparation completed, /2 .163/.423/.845 and P00401/P00601/whole451 endings retained. Original group .25/.65/1.3 and previous additional fees unchanged; no new test execution or acceptance. Price delta is not effort or dedicated token cost.'
write(out,f)
spec=P/'4066_P00702最大二session原三source契約対応.md';assert not spec.exists()
spec.write_text('''# P00702 最大2session・3件目最古revoke：原3sourceの契約対応

- Program NK-AUT-001、WBS-P007-02、AUT-004、DIF-016、UI225/226/234/241、origin/main SS314 §6.1（commit/設計hashはmanifest）。
- 対象: AuthSessionService.issue/constructor、SessionAuditWriter.write、SessionRevocationReason全6値。
- Test IDと独立期待値: PT-AUT-ISS001～008、AUT-SESSION-AUDIT001～009、PT-AUT-005-I/006。各目的/入力/SQL/値/資源/例外/並行観点は下記manifestのchecksおよび既存全Testソースへ対応。
- 発行はapp_users lock→INSERT→有効行のlast_accessed_at,id順lock→size-2件のREPLACED＋同TX重要監査。期限一致は有効外、同owner最大2。SQL、固定日時、独立AES-GCM vector、固定hash、ログの閉fieldを期待値とする。
- 原発行8件・監査9件は対象Main/Test sourceSHA・normal physicalSHA/CRC一致を確認。**原runの限定成功を保持し、新規実行0、whole依存や現DB実績へ転用しない。**監査原本SDK review未設定等の制限も保持。
- AuthSessionServiceTest全6件/576行は公開source読取のみ。実DB/100同時発行/commit・rollback等を含むwhole fixtureはHOLD。部分method選択や別経路で実行しない。
- 正常/境界/NULL/SQL/affected-count/close/再送契約を記録。未知runtimeの元試験はIllegalStateExceptionであり、provider起点AuthenticationContextException等の全例外行列を確認済みにしない。実DB競合・same-source全依存・451/終了依存は未受入。
- metadata実行command: `python3 -B evidence/01_PT/018_NK-OPS-001/input/1319_two_sessions_contract_audit.py`。exit0、新規PT0。対象branch/source/設計/証跡hash/独立期待値はmanifest。
- 証跡: [PG26724 manifest](../018_NK-OPS-001/evidence/PG26724-two-session-contract-v1/manifest.json)。BUG修正なし、Main/Test変更なし、元190新受入0、正式1964PT/53scope維持、工数完成率null。
''')
for name in ['001_NK-AUT-001_単体テスト仕様書.md','002_NK-AUT-001_実行結果.md']:
 p=P/name;p.write_text(p.read_text()+'\n\n## WBS65 P00702 原三source対応（2026-11-12）\n\n[4066契約/TestID/原run制限](4066_P00702最大二session原三source契約対応.md)と[PG26724 manifest](../018_NK-OPS-001/evidence/PG26724-two-session-contract-v1/manifest.json)へ対応。原発行8/監査9は対象byte同一で保持・再実行0。原/1準備のみ完了、実DB/競合/終了依存・451/元190未受入。\n')
nextcmd='Continue canonical625 P00703 authentication context validate/role owner/CSRF exact own source inventory and whole candidate fixture admission; original ending dependencies held. Reuse old same-target proofs only after source/CRC binding; ordinary whole pure missing PT after full closure/preprice. No real auth/DB/keys/held4/Root/VM/intent. Usage last11:25:53 nextNOTBEFORE12:25:53 compare actual clock; continue at normal boundaries.'
cfg=load(B/'input/1318_two_sessions_contract_start.json')
c=dict(groupId=cfg['groupId'],recordPath=str((D/'732_WBS65最大二session原三source準備結果.json').relative_to(R)),manifestPath=str(m.relative_to(R)),manifestSha256=sha(m),terminalAtUTC=a['atJST'],run='PG26724',workIds=cfg['workIds'],outcome='OWN3_PREPARATION_ONLY_ORIGINAL8_AND9_TARGET_BYTE_RETAINED_NO_NEW_EXEC_ENDING_HELD',technical=technical,forecastRef=ref(out),nextCommand=nextcmd,checkpointText='P00702 own3/承認DIF016/SS3146を独立SQL・TestIDへ対応。PG26724 metadata0、原発行8/監査9対象source/Test/physicalCRC同一で原scope保持・再演0。全DBfixture6件source読取のみ、最大2実競合/TX/SDK/終了依存・451未受入。provider同型context例外等の未試験観点は未確認として保持、BUG未確定/修正0。原/1 .087/.227/.455準備のみ完了、版60残'+str(f['revisedRemainingPp'])+'未較正、元190新0/正式1964-53/工数null。Main629不変更、次P00703へ継続。usage11:25:53次12:25:53実clock比較。')
write(B/'input/1321_two_sessions_close.json',c)
print(json.dumps(dict(actualExit=0,forecast=ref(out),remaining=f['revisedRemainingPp']),ensure_ascii=False))
