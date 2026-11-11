# A4-02 QA054共有fixtureと六呼出元

PG26034はsource witnessと公開証拠の照合だけで、Java compile/parser/runtime/PT/実DB/broker/held例外は実行していない。原六TestのGit blobは停止HEAD b713の計画原票と一致。共有goldenはPG25760資格source6fからbyte不変、候補Main7aed。変更は承認済みAction HTTP_COMPLETED→HTTP_REQUEST_COMPLETED、absolute297/64byte中22byteと42space、wire2336byteを維持。既PG25794独立vectorを参照し再実行しない。

| 呼出元 | source期待値の結論 | 原suiteの動的未実施条件 |
|---|---|---|
| HttpRequestLoggingValveTest | shared goldenのencrypt/decrypt比較に旧Action固定値なし | whole-suite DB fixtureのinitdb/ProcessBuilder/JDBCがDB HOLD |
| JmsSecondary330Test | proxyによる送信/副例外観点はgolden更新と矛盾しない | WebLogMessageSender→held WebStartupExceptionへ依存、全suite動的HOLD |
| WebApiLogReplayIntegrationTest | 自前Action再設定は同じ承認literal、API projection期待も同値。Details projectionStatus上書き保持 | 実DB/broker/shared sender依存でHOLD |
| WebLogDispatcherTest | cipher/golden動的比較に旧Action固定値なし | 実brokerおよびheld WebStartupException依存でHOLD |
| WebLogMessageSenderTest | JMS byte期待はgolden動的比較、旧固定Actionなし | EmbeddedActiveMQ起動とheld例外依存でHOLD |
| WebLogReplayWorkerTest | 再送rowの暗号化fixtureはcurrent goldenを使用 | 実DB/broker/shared sender依存でHOLD |

これは全bodyのPG強化レビュー・静的解析PASS・実行PT・coverageの代替ではない。明確な未許可依存をsourceで確認した時点でその動的操作を保留し、原suiteの抜粋・helper置換・別経路による実行をしない。再試行やHOLD解除を求めない。全六の実証完了までBUG2615/YKT2303は閉鎖しない。

費用主担当はA4-02のみ。既leaf名義はValve=P00603、Dispatcher/Sender/Worker=P00604。未登録JmsSecondary330/WebApiLogReplayIntegrationのlog関連はSender/P00604への参照を残し、request/API固有契約は当該主担当が別途受け持つ。名義参照による受入数や費用の追加0。残動的検証は既計画の各B/N契約に引継ぎ、新規budgetを足さない。

証拠: evidence/PG26034-qa054-six-callers-source-v1/manifest.json、SHA256 38aa1fa6b83778816cc14c36e5f1f16e8849e4b2e1e10ad61b4ed14dcfd7f6f7。全六のpath/SHA/blob/Test method名・golden呼出し行・依存witness・未完条件を保存。実command `python3 -B evidence/01_PT/018_NK-OPS-001/input/1082_qa054_six_callers_metadata.py` 終了0。PT0/newAcceptance0/coverage null、正式1964/53・工数null維持。A402計画行の終了条件「六件すべての結論又は未完条件を保存」を満たし、個別Bの終了とは分ける。
