# 2635 Web memory coordinator 元whole十七件 単体テスト仕様書

2026-10-30 JST / dev-foundation / source6b53efeec87f3ec36a840dd8e7759656cb4aee5c / HEADf6c88692fad2d084ef80e1d2348dce72781d487d / PG-D882。群3022開始0.5/3/5pp cap10は不変更。元JmsRequestReplyClientTest全327行8件＋ReplyCorrelationRegistryTest全137行5件、後続2391/92から発見した既存ReplyCorrelationTerminalRaceTest全180行4件を着手依存として実行前に追加し、17件3suiteへ固定。追加発見は既存PT観点で製品新実装/新TestID/原見積訂正ではない。既9件の2392旧source5590成功は履歴参照、当Source資格へ転用しない。

Program=JmsRequestReplyClient（constructor/exchange/onReply/pendingCount/lateReplyCount/validateRequest/failure）、ReplyCorrelationRegistry（register/complete/expire/cancel/count）、PendingReply（promise/view/copy/terminal）、JmsRequestReplyException＋Reason。Main四Sourceはcanonical/costP005-02、完全閉包五physical。関連NK-MSG001/MQ004005/UI212231/SS312§3.2/321§6§9。元Test三pathのbaseline ownerは未登録/UNKNOWN、Raceだけは2391/92・PG12902でP005-02の新logical候補が既記録済みなので、その候補根拠をUNKNOWNとは別に保持し正式ownerへ昇格させない。group主F03と既P005責任費の重複加算0。

Main/全Test/helper/Clock/callback/initializerを全読了。BrokerTopologyは固定enum値・body長/TTL値定義だけで接続なし。全senderはTest内memory callback、registryはJDK map/semaphore/futureのみ。PT_DEFAULT、実JMS/broker/DB/HTTP/process/VM/Root/graph9/permit/cohort操作0。private app rawlog参照0。原Test/Main/期待値を改変せず、一new-only JVM/execで測る。

|Test ID群（元method一意）|独立fixture/操作/期待|
|---|---|
|PT-JMS-008-CLIENT-01 exchangeRegistersBeforeOneSendAndReturnsDefensiveReply|固定ID/256byte request/response{4,5,6}、register→sender一回・pending1・reply後0・copy独立|
|CLIENT-02 sendFailureCancelsRegistrationAndPropagatesJmsException|合成JMS/unchecked sender例外を伝播、pending0|
|CLIENT-03 elapsedWaitExpiresAndSubsequentReplyIsLate|10ms実waitはtimeout分類/cause有/pending0/late1、性能合格ではない|
|CLIENT-04 replyAtDeadlineFailsTheWaitingFutureAsLate|mutable固定Clockを期限ちょうどへ、timeout cause/pending終端|
|CLIENT-05 interruptedWaitRemovesRegistrationAndRestoresInterruptFlag|自己所有threadのみinterrupt、latch2秒/join2000ms/finally再join、同threadのinterrupt状態とpending0|
|CLIENT-06 approvedConfiguredWaitsAccept1To20AndRejectTheNextWithoutSending|1/12/20自己worker全部登録後次waitはCAPACITY/送信しない、releaseはfinally/countDown、各Future.get2秒、枠全回収|
|CLIENT-07 constructorRegistryAndRequestBoundsDenyInvalidInputBeforeSend|null/0/21/255byte/1000001byte/0・負・2秒超wait拒否、1ns/2秒accept、registry capacity到達|
|CLIENT-08 exceptionReasonIsAClosedNonSecretClassification|Reason三定数・CAPACITY名前literal|
|PT-JMS-008-REGISTRY-01..05|bounded2/duplicate/cancel再利用、成功copy/late、期限equal/expire前後、nullとcapacity0/21、100自己並行応答のwinner1/late99/pending0|
|PT-JMS-TERM001..004|既2391独立oracleを原Test全bodyで再確認：64回complete/cancel/expire競合winner1と枠回収、capacity2へ20登録accepted2/rejected18、deadline-1ns/equal/+1nsとcopy、caller view任意完了/cancelが別view/sourceのpromiseを書換えない|

全expectedは固定literal/独立時刻/容量算術、Production呼出でexpected生成0。既future.joinは先に同期complete/fail済み又は明示bounded task後、自己latch/workerをfinally/TWRで閉じる。無期限latch箇所はfinite issuerのfinally releaseと親JVM180秒budgetを併記し、実サーバ性能/ITSTや全fixture例外分岐の証明へ拡張しない。

予定 `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14316_web_memory_coordinator_whole_seventeen_pt.py`。source6b53正常六Jar/元三Test/固定Reporterを使用しF/E/S/aborted/timeout/重複・actualexitを保存、環境は元JVM実測四prefixの既tested wrapperで構造化。14318独立postで元XML17・一session CRC・完全四Source五physicalの実counter（自然0/N/Aや未網羅は保持）を照合。結果2636/hash/時刻/SDK/command/関連BUGを記録、元83の再演/exec合成/旧成功転用0、全formal/個別17-190/工数null/QA051final/HOLD不変更。
