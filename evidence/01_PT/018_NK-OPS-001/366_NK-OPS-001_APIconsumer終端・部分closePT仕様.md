# API consumer終端・部分close PT仕様（PG474）

2026-10-20 REM004訂正追補（BUG1501/YKT1261/PG-D444、1223）：protocolFirstは最初のDLQ commit/元ACKだけを各group一回許し、それ以後は同groupの業務/再隔離/commit/rollbackを0とする。旧Testが期待したbusiness3/commit6はSS322§11のcommit後exitに反するため履歴として保持し、現期待はbusiness/questionCalls/rollback0・commit三（Sync/WebLog/Question各一）・通知一。非protocol modeの普通の再送/unknown期待は不変更、実Question正常wireは未処理/未ACKのままowner close後に返ることも確認する。下表の「fatal後ACK0」は最初の正常隔離commit自体を禁止する意味ではなく、終端後の新たなACK禁止と区別する。過去の成功結果を新期待の合格へ改記しない。

NK-MSG-001/002/ASY-001・NK-OPS-001、RD MQ003006008010/MON005、UI212213231251、SS312321342343/451。PG473/a5の同host+8fresh nativeはAPI96branch/122line/4method未網羅。まず公開起動経路での独立provider故障試験を追加し、未受入の分岐を除外しない。既承認仕様違反を発見した場合は修正前915/916・必要設計台帳へ登録する。

|Test ID|対象|独立期待値・fixture|
|---|---|---|
|PT-OPS-API-REM001|ApiMessagingRuntime.startSelected|4 sync context取得後WebLog factoryがruntime/fatalで失敗。通知は先行し一回、既所有4 contextは全close。通知の同一例外・別runtime・fatal、cleanup runtime/fatalを独立object identityと固定wrapper文字列で照合。失敗からready/runtime返却0。|
|PT-OPS-API-REM002|ApiMessagingRuntime.close/closeGroups|完成profileの6 contextを独立番号付け。Question→WebLog→sync4の順、全close一回、二重close0、ready false。複数Error・同一Error・runtime→Errorの優先度とsuppressionをidentityで照合。例外provider値を診断へ出さない。|
|PT-OPS-API-REM003|SyncRequestConsumers/WebLogConsumers.start/close|部分start・closeのruntime/fatal組合せ、同一Error自身suppression禁止、全所有close、通知先行、後段start0、null consumer/session mode拒否。既CORE004/007/008を関連回帰し独立provider call履歴を期待値とする。|
|PT-OPS-API-REM004|WebLog/Sync/Question callback及びAPI全体terminal|手書き固定長fixture又は既独立goldenを実Artemisへ投入。fatal後業務継続0、ACK0、rollback試行・故障後もstop一回、複数groupでterminal sticky。retryは承認brokerに委譲、正常化/再送仕様変更0。|
|PT-OPS-API-FACT001|ApiBrokerContexts.create/createOwned|同SYNC→WEB_LOG→ASYNCの固定profile/endpoint、factory一件目～三件目のruntime/fatal、既所有を逆順に全close。同一例外は自己suppression0、別close例外はoriginalへsuppression、password supplierはfactory取得中呼出0/借用close0。package限定seamだけ、公開createは固定singletonのまま。|

Productionを呼んでexpected生成しない。host fakeは所有・故障oracleのみ、実native接続の成功へ加算しない。command、source/diff、XML/FES、static、coverage、日時/hashは結果/manifestへ保存する。選択後は不足を確認して同契約内だけ補足し、source固定・451必要全6→必要同source nativeを一群で閉鎖する。PG473の全6/nativeや正式run24を新sourceへ流用0。QA051比較範囲・BUG544原因・全体coverage/正式品質は未閉鎖のまま。
