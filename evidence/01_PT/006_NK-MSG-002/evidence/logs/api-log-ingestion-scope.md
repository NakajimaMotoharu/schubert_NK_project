# API Web log取込み PT-IDEM-012 部分

Run PT-IDEM-20260907-02、source b3b5740。追加7 JUnit method（RequestLogDetailsTest 2、WebLogIngestServiceTest 5）を全reactorで再実行。SQL afterconditions/JSON literal/SS323 offsetが独立oracle。

- 全列保存・任意ActionのHTTP_REQUEST_COMPLETED正規化・SQL NULL・表示Role・IPv4/IPv6を確認。Username/Roleから認可やactor ID逆引きを行わない。
- Detailsはstrict object/許可key/重複拒否/型/byte上限を検査。不正入力・必須欠落・未知role・不正IP/PathはDB取得前に拒否。
- 100件同時投入でinsert成功1、保存1。別内容の同source Message IDは初回rowを保持。
- 接続/設定/statement/execute/commit/rollback/close各例外で成功へ変換せず、transactionとconnection解放を検査。
- 実Artemisと実PostgreSQLで、DB commit直後ACK失敗→rollback/redelivery→UKにより追加保存0→ACK成功を確認。broker duplicate propertyを付けない新規配送でも最終DB UKで1件を保証。
- DB障害では保存0/ACKなし、brokerの2回目配送で回復後1件。これは隔離component PTでありLinux server IT/STではない。

Java全coverage100%/SpotBugs0。共通NullAway/format gate、HTTP response投影、cleanup/stress、実NK HTTP Characterizationは未完了。BUG-014/015の既存cleanup不備は別途再試験が必要。
