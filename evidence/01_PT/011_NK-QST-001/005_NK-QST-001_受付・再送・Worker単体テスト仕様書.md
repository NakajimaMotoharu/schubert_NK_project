# NK-QST-001 受付・再送・Worker PT（実装前・未実行）

S3/D04/05の既存24＋質問関連7を実31processorへ結線する同一WIP。RD QST001～003/ASY001～009/AUT/MQ006～010、UI213/224/232/236/241/242、SS312§7～10/321/323/324/331/332/351/352、SSC151～155。ProductionのQuestionSubmitRequest/ReceiptIdGenerator、認証、JdbcInboxCoordinator、NKREF1、既存Outbox/typed protocolを再使用し、保守専用QuestionMutationInboxInspectorは業務/replayへ呼ばない。

## 終了試験と独立期待

| Test ID | fixture/入力/操作 | 独立oracle・終了条件 |
|---|---|---|
| PT-QST-ASUB-001 | 実PG18のUSER/ADMIN current session＋独立QSB4400 Q/A、固定receipt/UUID/UTC | questions/body/owner/token/submitted、job RECEIVED/original M0、notification ACCEPTED/RECEIVED、outbox W!=M0/correlationM0/PENDING、Inbox M0/COMPLETED/QUESTION ref/暗号0000を同txn。audit本文0。accepted時刻はµs、wire日時はms |
| PT-QST-ASUB-002 | DB5insert/audit/snapshot/commit/closeへ各failure | 全新規業務rollback、SENT偽装/response成功0、再操作1件。既存対象row/旧結果不変更 |
| PT-QST-ASUB-003 | 元M0再配送、新M1＋同owner/token/同本文、別payload、別owner、並行同token | 追加q/job/notification/work0、saved sourceM0/AAD/NKREF1/receipt/qid/time保持、新replyID＋correlation M1、SENT時0200、payload差0105。現在session毎回再検証 |
| PT-QST-ASUB-004 | 2秒total deadline（送信時刻と受信時刻の小さい期限）/monotonic clock | DB前timeoutは新q0、commit後timeout9000でも保存0000/COMPLETED不変更、後fresh同tokenはSENT確認後0200。wait時DB connection/lock0、request threadのJMS送信0、deadlineをcommit後に再開始しない |
| PT-QST-ASUB-005 | 対象Outbox送信前/commit後mark前/SENT lease残/別correlation/body/ID/null/time | 正しい元W/receipt/qid/jobとSENT・sent_at>=Inbox completion・lease解放を確認してだけ成功。別rowの送信で対象成功にしない。pending/ERROR9000、矛盾は9000で元Inbox不変更 |
| PT-QST-ASUB-006 | 正規7日保守でInboxだけ削除、questions owner/tokenは残す | 同本文でも真正saved証明欠落は9000、異本文0105、q再作成/Inboxalias/元時刻復元/延命0 |
| PT-QST-ASUB-007 | receipt UK collisionと他constraint/null/random failure | receipt名の23505だけbounded savepoint retry、owner/tokenや他SQLエラーをreceipt retryしない、無限retry0／原本保存 |
| PT-QST-AWORK-001 | actual Broker QWK320、W/correlationM0、実DB receipt/qid/job照合 | RECEIVED→PROCESSING CAS/W保存→DBclose→STUB空answer/現在UTC→Question lock/answer UK/COMPLETED・通知/audit同txn→元ACK。Provider中DB connection0 |
| PT-QST-AWORK-002 | sameW PROCESSING recovery／別W／既存Answer同一と矛盾／取消先着 | 同Wだけ再開、別W/原body不一致は整合拒否、既存answerを上書き0、cancelledはProvider0/冪等ACK、CAS commit先着のみ有効 |
| PT-QST-AWORK-003 | answer作成中に質問を論理削除 | 新Answerはquestionのis_deleted/deleted_at/deleted_by三点を継承、未削除false/NULL保持、矛盾errorと全rollback、Notification本文projectionは別query受入で確認 |
| PT-QST-AWORK-004 | delivery1/2/3一時failure／4以上最終failure／DB不能／DLQ pending | 実countをcapせず、retry_countだけ3上限。1～3JMSrollback、最終ERROR＋immutable D/W DLQ同DBtxn→D SENT後だけACK。ERROR再配送もpendingならACK0。DLQ各crashは018/303の下位実証と業務txnを接続 |
| PT-QST-AWORK-005 | count-less／null/unknown、STUB業務ERROR、permanent protocol | metadata欠落は成功禁止、予期した業務ERRORはDBcommit/ACKでDLQ0、不正wireは既存JMS同tx fatalで業務0、Provider/質問/回答/credential/tokenのlog漏れ0 |

未実行を合格に算入しない。現行full Source・選択command/日時/各FES/static/coverage B/L/M/C、BUG/SSCとsanitized evidence/hashは006/018と本Programの006結果へ保存する。期待wireはSSのoffset/lengthからliteralを独立作成し、DBは独立SQL後条件、暗号は独立key/vector＋AAD/参照改竄negative。Production codecをexpected作成に使わない。署名同Source普通起動・31登録/3consumer・専用Outbox lifetime・実NK CHR・全100%は別gateであり本仕様の作成/下位選択成功だけで受入としない。
