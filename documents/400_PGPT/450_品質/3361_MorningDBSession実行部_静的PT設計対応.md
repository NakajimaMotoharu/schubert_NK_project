# MorningDatabaseSession runtime 静的PT設計対応（未実行）

2026-11-01 / PG-D1079 / PG17246-MORNING-DB-RUNTIME-PG-REVIEW。source6b53efeec87f3ec36a840dd8e7759656cb4aee5c、保存HEAD6cda77a1667eec5812b076346b5e800734ac1cd8、事前2/5/9共有pp cap10・共有used72/rem28。index→3094/3095と2229を照合した。選定で661～980を読んだ費用も当群内に含め、事前開始時刻を遡及しない。

重要な区別：同byte五Main/helperの全文PGレビューは旧11580/82→現16112/14で既に参照済み。新規の全文レビュー完了件数へ再計上0。今回読んだruntime661～1645（及び所有外枠478～547）から、後続で未実測条件を見失わないため下記18観点を文書化する。既3346～49の「全PGレビュー未完」は当値PT単位が全runtimeを検証していないという限界であり、既存PGレビュー証拠を不存在と扱わない。新判断が元PMD44理由を覆したとはしない。

これはSTATIC_PT_DESIGN_MAPPING_RECORDED、動的PTはNOT_EXECUTED_HOLD。18行は将来の設計観点IDでJUnit18件でも新Test実装でもない。Main methodからexpectedを生成せず、承認済みSSの順序・独立literal行/状態/同run/date/µs/receipt表と、内部null/owner invariantを読み合わせた。分岐全網羅の実測、DB後条件、callback/close順位・並行所有・TRUE terminalを証明しない。元MorningDatabaseSessionTest65全6150行の本文レビュー済みとは主張しない。

|設計観点ID|対象method|根拠・契約|未実測の正常/境界/異常/null/例外/再送・並行観点|
|---|---|---|---|
|D-MDB-001|execute / Session.guard|341 SSC104;332 SSC063|callback終了でactive=false、同thread・非handoff・非interrupt限定。Connection/owned credentialの責務、SQL/IO既知固定と未知identity・close順位を区別。別thread/再入/終了後/取得前失敗/close同時失敗は非成功。|
|D-MDB-002|inspectPermitDatabase|341 SSC104/200|cleanupVerifiedかつexpiryHandoffStarted後だけ、同Connectionのrole/schema/advisoryを前後照合。null・role変化・lock消失・owner期限・schema unknownを拒否しpermitを生成しない。|
|D-MDB-003|requireUnused / requireConsistent|341 SSC094;332 §8.3|新runは参照0、resumeはidentityConsistent。backupCommitted前限定、同run/cutoffの前後guard。存在・不整合を成功補完せずSQL等の実後条件は未実測。|
|D-MDB-004|beginBackup|341 SSC104|schema確認→同TX二step begin→commit確定→autoCommit=true→backupCommitted。途中失敗では手修復/再発行しない。commit送達unknown後に権限や成功を付与しない。|
|D-MDB-005|successfulBackup / successfulHandle|341 SSC200;331 §8.3|最新二SUCCESSが同run/date/attempt/start/endの一束で、別step、µs、終了≦now、固定target/success1又は2/failure0/byte>0/error null。欠落/3行/未来/日違い/driver未知を拒否。SQL literalと独立14列値を将来oracleにする。|
|D-MDB-006|beginResumeBackup / completeReusedBackup|341 SSC200|同manifest再読と同handleの既SUCCESS確認、二SKIP確認後のみcommit。再用完了はreadback/rollback後backupFinished。元SUCCESSを今回新Backup成功へ数えず、manifest交換/null/不一致拒否。|
|D-MDB-007|completionGuard / completeBackup|341 SSC104/134|同begin、未finished/未handoff、autoCommit/RW/READ_COMMITTED/HELD。独立bundle完成callback前後に再確認し、返却時刻だけでDB/原本/Unit成功を認定しない。|
|D-MDB-008|failBackup / failedBackupSnapshot / failedObservationGuard|341 SSC134;332 SSC063|二FAILEDだけ同TX確定→独立二行再読→rollback後finished。正確なCOMMAND_FAILURE(1,0,1,0)二値だけended保持。snapshotは同begin/end/ownerの再読で、異なるfailed理由から代替権限を作らない。|
|D-MDB-009|observeBackup / observeBackupPair|341 SSC134/200|current二rowをid昇順lockしsemantic DB/config順へ戻す。再用では元manifest+prior二SUCCESS、通常ではexpected handle、未manifestでは正確なfailed/end一致。余行/NULL/不同値/owner故障は非成功。|
|D-MDB-010|handoffCleanup|341 SSC104|backupFinished後一回、開始前autoCommit=true、inHandoff中Session再入不可。子callback後にlock回収とguardを満たして返す。callback/再取得失敗でも開始済み印を戻して再発行しない。|
|D-MDB-011|requireAbandonedRequest|341 SSC104;332 §8.3|同run、元startがcutoff以後/今回start未満、二step元FAILED/ABANDONEDでattempt小・日付/終了窓一致。RO TX二row/余行拒否、rollback/状態復帰/consistent再読。既requestを書換えず別runを救済しない。|
|D-MDB-012|recheckConsistent|332 SSC063|JDBC RW設定のままserver SET TRANSACTION READ ONLY。Statement取得直後primary記録/direct close、SQL-only固定変換・未知identity維持。Connection借用とclose所有を分け、失敗時に値を返さない。|
|D-MDB-013|beginExpiry overloads|341 SSC200|cleanupVerified、expiry未handoff/未begin、同Backup run必須。prior auditとcurrent.SKIP整合、commit後に元SUCCESS又は正確RUNNING初期監査を独立再読、rollback/owner再確認後だけbeginsを保持。元audit更新や再purgeを許可しない。|
|D-MDB-014|handoffExpiry|341 SSC200/104|cleanupVerified＋expiryBegins後一回だけhandoff。開始済みを保持し、finally inHandoff解除は再実行許可ではない。別thread・重複・autoCommit false・子/再取得unknownを非成功。|
|D-MDB-015|observeExpiry|341 SSC200;331 expiry監査|同begins/EXPIRY receipt。SKIPはexit0＋元audit一致、通常SUCCESS0/WARNING10/FAILED30を厳密照合しended非null、許可error NONE/COMMAND_FAILURE/SAFETY_FAILUREだけ。rollback後owner再確認、未知status/終了/不一致を0補完しない。|
|D-MDB-016|observeCleanup variants|341 SSC199/200|Backupfinished＋handoff、receipt0/10のみ、failedBackupと保持failureEnded整合。七terminalを現在DBから読み各SKIP/backupUnavailable/finishedを再検査、receipt一致・rollback・owner再確認後だけcleanupVerified。拒否30とは分ける。|
|D-MDB-017|observeCleanupRejected / cleanupReferences overloads|341 SSC199/200/201|拒否はCLEANUP exit30・同ownerのreadRejected二回一致だけで完了/新attemptでない。元参照はexpected全row再読後だけ取得、元成功seals/進捗はRepository側別契約。NULL/交換/unknownを成功値で埋めない。|
|D-MDB-018|currentRunReference|341 SSC200|data-only same-run lookupでforeign UUID拒否。現在runを返すだけで原本session能力や管理検索・同日別run成功の認定を作らない。originals注入経路と区別。|

全行に共通：取得前/後、body、rollback、state復帰、owner再認証、Statement/ResultSet/Connection closeの失敗を独立に区別し、未知を既知DB不正へ正常化しない。SQLは手書の承認済みpostconditionで期待を作る。現在実DBを使うwhole65およびRoot/VM/native/credential/permit等依存はHOLD、代替fixture・切出し・試し起動を作らない。部分値PT7の真PASSと当18設計行を混ぜない。

17246は読取済みMainのnormal14216 source SHA、旧レビュー/現参照/独立post/SS331332341343の同main hashを保存する受動metadata工具で、Product/Test/JVM/SQL/ネットワーク/VMを起動しない。元review sourceとcurrent production sourceを別field保持、NULLcoverage/動的0/新受入0を壊すmetadata反例だけを確認する。工具検査は18PT成功とはしない。

固有2643/386・Main546940・四286430/partial71306・正式1964PT53scope/17of190/工数null/QA051final/全HOLD不変。旧source成功、元44理由、v3～v5/群開始見積/costを変更しない。元current registry/全WBSを当文書だけで再検証しない。次は許可済み未参照whole/静的不足へ継続し小区切り停止0。
