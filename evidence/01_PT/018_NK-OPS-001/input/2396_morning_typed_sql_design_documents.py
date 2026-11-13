"""SSC341 isolated design-only sparse-tree candidate; no product or DB operation."""
from pathlib import Path
import subprocess,json,hashlib,datetime
r=Path.cwd();w=r.parent/'ssc340-null-check-design-20261113';base=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip();assert base=='983c34856297cbe1fadaa3d18898a9e7a4691d75';assert not subprocess.check_output(['git','-C',str(w),'status','--porcelain']);p332='documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md';p354='documents/300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md';ledger='documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md'
ss332='''
## SSC341 Morning専用DBの既知SQL変換とconnection解放の限定fatal確認（2026-11-13）

BUG2852/YKT2359、SS341/343、WBS-P017-01.03/P017-02.03、PT-MDB-CAT341-001～012。対象はMorningDatabaseSessionの既知SQLException/BatchRepositoryExceptionから固定IOExceptionへ変換する既存20捕捉箇所と、そのexecute所有connectionのSQL close変換/closeReplaceだけである。既SS332のtyped priorityを先に適用し、batchのchecked IOException/未知Runtime/Errorを一般化して置換しない。SQL、DB role、transaction/commit/rollback回数、run/cutoff、原本・M/A/advisory・callback lifetime、正常結果を変更しない。

- 捕捉したSQLException又はBatchRepositoryExceptionを固定診断へ捨てる直前だけ、既storage.StorageIoExceptionのpure finite graph portでcause/suppressed/SQLException.nextをidentity visitedで確認する。到達可能なErrorは元objectで伝播し、非fatal循環は有限帰還、新IOExceptionのmessage/cause/suppressedへprovider本文/graphを保存しない。SQLExceptionでもBatchRepositoryExceptionでもないchecked IOException/CleanupStoppedException等は既固定化・既型順位のままとする。
- execute最外捕捉でこの確認がErrorを伝播する場合、finallyのprimaryにもその実Errorを記録してからthrowする。元SQLExceptionをprimaryのまま残して未知cleanupにErrorを上書きさせない。分類を追加したことでowned credentialのwipe/close、取得済connectionの一回close、Session.active=falseを省略しない。
- body成功後のconnection.closeがSQLExceptionの場合は、そのSQL graph確認後だけ既固定IOExceptionへ変換する。nonnullのSQL/BatchRepositoryException primary＋SQL secondaryは、既false選択で破棄する前にprimary graph→secondary graphの順で確認する。両方非fatalなら既固定結果を保持する。
- 既SQL primary＋未知cleanupのcleanup選択、未知Runtime/Error primaryの同一性＋新固定secondary、同一Throwableのself-suppression回避、checked IOException primaryの既処理を変更しない。既policyで先に選択されるunknown/checkedIOへ新しい一律graph分類を追加しない。null primary・取得失敗・直接Error等の既各経路と明確に区別する。

本補足は例外の既固定化境界だけの内部具体化であり、raw graphのlogging、追加DB/close/rollback/stop/再送、非同期callbackや合成capabilityから実所有を推定することを許可しない。実DB/Root/VM/原本/Backup/鍵/native/intent/permit等のHOLDは不変更。source強化review/静的確認と未実行PT・coverageを分離し、同sourceの全関連単体/実DB/所有後条件と451未完を保持する。

'''
ss354='''
## SSC341 Morning既知SQL catalog境界・独立故障PT（2026-11-13）

SS332 SSC341、SS341/343、BUG2852/YKT2359。production分類methodをexpected生成に使わず、fixtureで事前固定したError/unknown object identity、SQLSTATE、固定catalog、literal close/wipe/operation件数と既typed優先を期待値とする。元20変換siteはPG29726の公開source hash/行/捕捉型で固定し、queryのResultSet/Statement二scopeとexecuteの所有connectionを別に確認する。

|Test ID|独立入力・期待値と後条件|
|---|---|
|PT-MDB-CAT341-001|非fatal SQL/Batch例外の既固定IOException message/cause/suppressedを保持、成功へ戻さず取得済connection close1/credential消費1。|
|PT-MDB-CAT341-002|SQL cause/suppressed/nextの各Errorを元identityで伝播。未知provider文字列を新catalogへ出さない。|
|PT-MDB-CAT341-003|非fatal自己next/相互cause/suppressed循環は有限帰還し既固定診断、同一Throwableの再利用も自己抑制しない。|
|PT-MDB-CAT341-004|最外known SQL内Error＋未知cleanupの二故障で、分類後の実Errorがprimaryとして保持される。owned close/credentialwipeを省略しない。|
|PT-MDB-CAT341-005|非fatal SQL primary＋未知cleanupは既cleanup元identityの選択を保持、SQL graphだけを理由に元非fatal型順位を変更しない。|
|PT-MDB-CAT341-006|body成功＋SQL close内Errorは成功値を返さず元Error、SQL close非fatalは既固定IOException。close再試行0。|
|PT-MDB-CAT341-007|SQL/Batch primary＋SQL secondaryはprimary graph→secondary graph。片方/両方Errorと両非fatalを独立に確認。|
|PT-MDB-CAT341-008|checked IOException/CleanupStoppedException primaryの既固定化/typed policyは不変、SQL専用確認を一般化しない。|
|PT-MDB-CAT341-009|未知Runtime/Error primaryの同一性・fresh固定secondary・suppression無効/同一objectを既表どおり確認、raw secondaryを公開しない。|
|PT-MDB-CAT341-010|null/欠落・取得前拒否・credential consume/wipe/Properties clear・Session callback後失効と異thread拒否の既契約を退行させない。|
|PT-MDB-CAT341-011|query rows→statement→owned connectionの必要close各1、未取得close0、追加commit/rollback/SQL/stop0、原role/SQL/bind/timeout/所有後条件を維持する。|
|PT-MDB-CAT341-012|当source whole MorningDB/owner/実DB依存の関連回帰・全scope四counter・NullAway/静的・原本/同run/同budget/終了依存を照合し、部品source reviewを実所有や正式451に代用しない。|

実環境の前提未成立なら製品PTはNOT_RUN、coverageは未測定として残す。新しいfake DB/Root/issuer authority、held Testのmethod抽出、拒否操作のprobe/retryを行わない。独立した既許可host作業は継続できる。PG/静的代替は製品PT PASS・実測counter・正式1964/53・IT/STに加算しない。

'''
entry='''
## SSC-341 Morning専用DBの既知SQL catalog変換・型優先の内部具体化（2026-11-13、PG、設計確定）

BUG2852/YKT2359、WBS-P017-01.03/P017-02.03。SS332 SSC341でMorningDatabaseSession既20known捕捉と所有connection closeだけへSQL/BatchRepositoryExceptionのfinite fatal確認を限定し、checkedIO/unknown・SQLと未知cleanup・directErrorの既型順位を維持した。executeで分類されたErrorをfinally primaryへ記録し、ownedclose/credentialwipeとSession失効を省略しない。SQL/role/TX/原本/run/cutoff・正常外部動作は不変更、RD/UI変更不要の内部詳細で新QA不要。

SS354 SSC341はPT-MDB-CAT341-001～012の独立object/循環/固定catalog/typed priority/owned資源後条件を確定。設計のみorigin/main隔離sparse三mdで公開、未受入source/config/tools/evidence混入0。実装・関連whole PT/DB/原本/終了依存・451は未完で、既HOLDを解除しない。main公開commitは三file履歴/remote照合を正とする。状態: 設計記述確定・main公開前、PG/PT未完。

'''
adds={p332:ss332,p354:ss354,ledger:entry};rows=[]
for name,addition in adds.items():
 p=w/name;old=p.read_text();assert old.encode()==subprocess.check_output(['git','show',base+':'+name]);head,rest=old.split('\n',1);new=head+'\n'+addition+rest;assert new.replace(addition,'',1)==old;p.write_text(new);rows.append(dict(path=name,beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=hashlib.sha256(new.encode()).hexdigest()))
changed=set(subprocess.check_output(['git','-C',str(w),'diff','--name-only','-z'],text=True).split('\0'))-{''};assert changed==set(adds);assert subprocess.run(['git','-C',str(w),'diff','--check'],capture_output=True).returncode==0
e=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG29764-ssc341-typed-sql-design-candidate-v1';assert not e.exists();e.mkdir();(e/'manifest.json').write_text(json.dumps(dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),baseMain=base,worktree=str(w),designOnlyPaths=rows,wholeExistingTextInverseEqual=True,testViewpoints=12,sourceOrDbActions=0,protectedFilesMaterializedOrRead=False,published=False),ensure_ascii=False,indent=2)+'\n');print('SSC341 three-design-file candidate with12 independent viewpoints; no code/DB orprotected access')
