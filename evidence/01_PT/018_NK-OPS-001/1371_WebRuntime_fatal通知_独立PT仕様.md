# Web runtime fatal infrastructure通知の独立PT仕様

Program NK-WEB-002/NK-MSG-001/002、MQ003..008/AUT002/MON003、UI225226231235、SS312/313/321/342/352/354、PG231/SSC324。Test ID START324003、WebLogApplicationRuntimeTest.start324003FatalReplyInfrastructureSignalsRuntimeWithoutBusinessAck、対象startPathのonFatal callback（原da11/XMLではlambda$startPath$1）。元54/6372でL1/M1未実行と同定済み、getterは既存SCR128で検証済みなので無意味なgetter反復で補完しない。既実装callbackは正しいterminal.set(true)、未網羅PTの追加でありProduction障害/TDD失敗を予め捏造しない。

## 入力・独立期待値

自己所有temporary WebLogDatabaseFixture/PostgreSQL/Flyway、自己所有loopback Tomcatとsynthetic codecを用いて通常Log componentを起動する。brokerは外部接続のないJMS interface proxy、起動reply contextとreadiness contextを明示契約で実装し、reply listenerだけを公開setMessageListener portから取得する。private reflection/field書換え無し。空outboxなので業務message送信なし。実Artemis/ops管理/Root/VM/既存DB/credential/permitには触れない。

事前=通常ready/terminal false、listener取得済み、provider closeは正常。BytesMessage.getBodyLengthが同一の固定AssertionErrorを一回throwする入力（他の本文/getterへ到達しない）。listener.onMessage呼出後、同じErrorが再throw、getter1回、rollback1回、commit0、committed-protocol terminal callback0、runtime.terminalFailureObserved=true/ready=falseを固定期待とする。単なるrelated ReplyConsumers内terminalではなく、runtimeへ接続された独立fatal callbackの意味を確認する。expectedをProduction methodから生成しない。正常scopeをclose後、二proxy contextのclose回数も入力の取得数と一致し、実Tomcat/replayは既正規close・DB fixtureはfinally stopする。proxy数は実broker資源解放proofやnative判定ではない。

## 実行とgate

PGは当callback source/既SS/呼出元のError通知とACK非発行を点検しMain修正不要。全Mainは11ecc、全他Testはda11固定、新Runtime Test method一つだけ追加する。PG6376新only宣言22件/8suite（既baseline12/7＋当runtime10）で、変更Test/関連実HTTP・startup/normalcloseをまとめる。元54/18/4048を再実行せず、前54はそのsourceの歴史証拠として保持、当sourceの新22原XML/六Jar/全8511667同byte/四counter/静的を6378で照合する。必要全体は新sourceの全Testを一campaignへ集約し、異sourceの選択PT/native/coverageを合成しない。

予定commandは新工具定義で固定、保存commit後beginへ対象source/branch/実command/時刻、原XMLのOS/JDK・終了code・input/expected/actual/coverage/BUGpath/hashを保存する。現在未実行。PT_DEFAULT：同じ承認済み自己所有fixture契約、通信先はloopback HTTP/自分のtemporaryPGのみ、JMSはproxy。失敗/flaky/skipped/not-runは成功へ算入0。原票BUG1574/1575/YKT1329/1330と前中断は保持、当testだけでnative/全451/正式を認定しない。

WBS-P018-06の既残PTとして小群開始.25/.75/2pp（原-v4へ加算/減額0）、前startup群.5/2/6と計測・実費を分離し、実N/T専有費/工数null。freshused41残59/reset1793082865/secondary不明。正式1964/53・17/190/QA051final/PTALT不明代替0・実環境HOLD/全保全物不変更。通常unit/commitで停止しない。
