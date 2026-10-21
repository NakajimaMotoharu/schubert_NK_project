# Consumer332 ordinary graph/rollback PT仕様

## 事前compile失敗・新only是正（BUG1603/YKT1356）

元6652/11185と6654/22215はf0c1fa87e/archive ca43a4c6、phase0,1真正1/0PT0suite。API fixtureの汎用checked closeがjavac try警告四件で-Werrorへ違反、予定反例とは異なるので原赤資格なし。具体三owner close dispatch/unchecked署名へ限定是正し、入力/期待値/全Main/既Testは固定。Web同型は既具体ownerで非該当。旧run/manifestを上書きせず、新赤6660/6662-v2・green6664-v2/原6666-v2を使用する。以下6652/6654/6656/6658は旧初期計画として保持、現在のcommandは同driver/新SLOTS。再試験前は当fixture障害OPEN。

Program NK-MSG-001/002、対象API SyncRequestConsumers/WebLogConsumers/QuestionWorkConsumers、Web ArtemisReplyConsumer/Consumers。RD MQ003～010/ASY001～009/MON005、UI212213231、SS312/321/354/SSC332、BUG1602/YKT1355・1354。主費WBS-P005-02、P005-03/P006-05/P012-01は同群参照・追加共通費0。着手event1665、低.5/標準2/高5共有週次pp・未較正、原/v4/旧群不変更、実N/T/専有費null。

設計only sourcefe21609a9/PR196→main9cca2275bef6ffb29d96d623e7637b61e05d3d58は通常merge/remote確認済。SS321354/914三fileのみ、PG/tool/evidence混入0、自己承認/保護迂回0。添付API cap100一回失敗/再試行・既添付削除0。gh pr diff --checkは未対応flagで終了1、local git diff --check終了0と変更三file/内容確認を使用、失敗を検査成功へ変換しない。

## PT_DEFAULTと独立期待値

純interface JMSContext/JMSConsumer/BytesMessage proxy、最初のgetBodyLengthを固定故障点にする。createConsumerはlistener捕捉のみ、start/close/rollbackはcounterのみ、外部JMS/DB/VM/Root/業務/実鍵0。新二class八methodでsource164f1d9b7の反例を先行する。literal整数/事前固定Error objectと明示因果edgeがoracle、production methodでexpected生成0。未知proxy操作はAssertionErrorにして、元予定boolean assertion以外なら反例資格へ加算しない。

|Test ID/method suffix|fixture/操作|独立期待値|
|---|---|---|
|332001～003 Sync/WebLog/Question CannotRetryConfirmedRollbackWithFatalGraph|cause/suppressed/JMSlinked/SQLnextのError、正常rollback、三owner|getBodyLength1/rollback1/commit0/business0後、halt/通知1。通知正常return時は旧API直接Errorと同じreturn、停止後全context配送無処理|
|332004 OrdinaryCyclesRetryAndDirectFatalKeepsApiNotificationPolicy|非fatal循環の二配送、各owner直接Error|ordinaryはread2/rollback2/通知0/ready、直接Errorはrollback1/通知1/非ready、owner closeはSync4/他1|
|332005 WrappedFatalSignalsThenRethrowsOriginalWithoutSecondRollback|Web各四graph、正常rollback|read1/rollback1/commit0、通知1後に同一Error、terminal/非ready/停止後read不増|
|332006 PreflightIsNotConfirmedAndStateResetsPerDelivery|一回ordinary正常rollback後にnull又はsession不正|前回confirmedを再利用せず通知1/非ready、read1/rollback1のまま/commit0|
|332007 RollbackFatalIsNeverReissuedAndNotificationCannotMaskIt|ordinary getter故障→rollback Error、通知Runtime/Error/正常|rollback1だけ、通知1後に同一rollback Error、停止後read不増、commit0|
|332008 OrdinaryCycleDirectFatalAndPublicListenerContractsRemain|Web非fatalcycle二配送/public入口、直接Error＋通知RTE/Error/正常|普通retry rollback2/通知0/ready、公開入口元Runtime identity/rollback1追加/null preflight追加rb0、直接Errorは通知1/rollback1/元Error|

API/Web fixture close回数は各TWRで検査。DLQ/processorは未到達を明示assert、ACKは未知methodとして拒否。null/preflight公開例外は既契約を保持し、NPEをcatchして正常扱いしない。実broker旧domain/既rollback/graph portはgreenでまとめる。

## 実行・保全

PYTHONPATH既三path、`python3 -B tools/quality/pg6652_consumer_graph_selected.py PHASE`。red-api=6652/宣言16-8、実10-5/F3/phase0,0,1/not-run6、red-web=6654/宣言16-8、実14-6/F4/not-run2を予測。原readerは七予定boolean assertionの完全一致/真正1/source/archive/XMLを照合し、別fixture不具合/compile/error/skipped/flakyを反例へ加算しない。Main変更は両真正終端・原資格後だけ、全新旧Test bytesを固定。

green6656=77-20（全六baseline12-7＋API37-7＋Web28-6）、compile-first/SpotBugs六module0。原6658は原Jar/XML/851Main1667physical/五Main差分/四counter/raw静的を照合。当source全体は既4158/635＋local4/1＋consumer8/2=4170/638の予定であり未実行・合格ではない。旧全体/旧native/別source成功を足さず、PTALT代替完了0・実Root等全HOLD/正式1964-53/個別17-190/工数null/QA051final維持。timestamp/OS/tool/branch/commit/command/exit・input/oracle/actual/hash/BUGSSCは元begin/manifestと後続原結果に保存する。
