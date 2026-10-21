# SSC329 / BUG1592 / YKT1345 ordinary JDBC transaction

Program NK-MSG-002/NK-AUT-001、`JdbcSyncRequestProcessor.process`。RD MQ-003/006/008、UI212/226/231/234、SS312/324/354、PG-D483。群1625の開始見積 .5/1.5/4共有ppは固定、WBS-P004-05主担当/P018-05参照費0。113site棚卸し6542は確認範囲であり受入0。

## 着手前判定

PT_DEFAULT。既存API requestは入力fixtureだけ、期待値は下記literalと別counter/元Error object。JDBC interface proxy、固定clock、有限Throwableだけを用い、DB/network/process/VM/Root/原本/鍵/permit操作なし。5秒timeout。拒否対象を探る実行や代替経路ではない。既保留/PTALT001/002を解除しない。

未修正Main1b663c1b0の新Test-only sourceを固定し、6544-redでformat→全六testCompile→選択PT/static、真正終端と原XMLを保存する。予定全20/8、APIで停止した場合は実11/5と後続not-runを区別。compile/timeout/errorは目的赤ではない。旧Mainによる下記001/002/003/004/007のassertion失敗を予測し、実結果は独立読取で確定する。PG後も同Test bytesを固定しgreen20/8、全体4073へ算術加算しない。

|Test ID / method suffix|入力・独立期待値|
|---|---|
|PT-TX-GRAPH329001 SqlPrimaryAndCloseFatalRetainIdentityAfterRollback|SQL primary＋close Error。元Error identity、acquire→auto:false→handle→rollback→close各1、応答なし|
|002 ProtocolPrimaryAndCloseFatalCannotBecomeTemporary|Protocol primary＋close Error。同じ順/元Error、Temporaryへ縮退不可|
|003 DirectFatalRollsBackOnceDespiteSecondaryAndSameClose|handler Error、rollback Runtime、close同Error。元Error優先、rollback/close各1。self-suppression wrapperも失fatal不可|
|004 CommitFatalWinsOverRollbackAndCloseFatals|commit Error、rollback/close別Error。handle→commit→rollback→close、commitの元Error優先|
|005 NonFatalCycleReturnsOnlyTheFixedCatalog|SQL-next双方向cycle＋rollback secondary。有限帰還、literal `request transaction is unavailable`、cause null/suppressed0、rollback/close各1|
|006 NormalSuccessCommitsAndClosesBeforeReturningLiteralBytes|handler literal byte[4,2]、handle→commit→close各1、rollback0、戻り値byte[4,2]|
|007 SqlNextCauseFatalCannotBecomeTheFixedCatalog|SQL next→cause Error、元Error identity、rollback/close各1|
|008 PostCommitCloseFailureIsNotAReplyOrAnInventedRollback|commit成功後close SQL。固定catalog/cause null/suppressed0、commit/close各1、rollback0/応答なし|

全caseでconnection/request同一性・固定UTC時刻を検査。通常null/constructor等既存domainも後続同source回帰へ結合する。本8件だけで共通helper全graph/113mapper/四100/全YKT/正式を完了にしない。PG後の共通helper pure graph testは別仕様で全edge/null/重複/優先/非fatalを明示する。

## 保存

Main/Test/operator/source/run/archive/start/end/exitとXML、失敗型/実assertion、後段未実行、当coverage/staticを原manifestへ記録。公開hashは実回収後追記、未実行値null。秘密/原本/実鍵なし、既失敗/旧nativeは保全。正式1964/53・17/190・工数null・QA051final・PTALT代替0は不変。
