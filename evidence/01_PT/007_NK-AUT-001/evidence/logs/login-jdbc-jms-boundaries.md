# PT-AUT-TX-001..004 — JDBC所有・JMS再配送の単体接続

対象: PG-D-050、SS311/312 §3/12/324 §7、JdbcSyncRequestProcessor/TransactionalRequestHandler/TemporaryInfrastructureException、LoginInboxService、SyncRequestListener。Production broker template・実Artemis2.56.0・実PostgreSQL18.6の隔離fixtureを使用する。実運用DB/鍵/credentialは使用しない。

## 独立期待値と操作

| Test ID | 操作 | 期待後条件・比較根拠 |
|---|---|---|
| PT-AUT-TX-001 | 実Login成功/失敗をJDBC ownerで処理→同ID再配送 | commit前別connectionでInbox/session/audit0、commit後成功1/1/1・失敗1/0/1。失敗counter1、再配送時照合追加0。新応答ID・成功0200/失敗元0101の688byte独立golden |
| PT-AUT-TX-002 | open/begin/handler SQL/runtime/null/commit前・後/close/rollback/rollback+close/provider null | lifecycle proxyの実delegate呼出順/回数を検査。commit後/close失敗だけDB1、その他DB0、同ID回復後全対象DB1。例外型/message固定・cause/suppressed0、所有connection閉鎖、password配列0 |
| PT-AUT-TX-003 | hostname入り不正Loginとrollback/closeの成功・失敗4組合せ | 正常rollback/closeだけ恒久型、付随故障は一時型。全件DB0/password照合0/commit0/rollback1/close1。DB確定不明で恒久DLQ処理へ移さない |
| PT-AUT-TX-004 | 実broker受信→実Login DBcommit→reply送信前またはJMS commit前で障害 | 別DBconnectionで1/1/1を確認して障害注入。replyはrollbackされ不可視、JMSXDeliveryCount2で再配送。次は0200・保存DATA、DB副作用/照合は各1。別途同IDを再sendしdeliveryCount1/cache用propertyなしでもDB重複0 |
| PT-AUT-TX-004 | DB取得障害→同Message再配送でDB回復 | DB0/照合0/replyなし、deliveryCount2の回復後0000/DB各1。最後はrequest/reply queueに余剰なし |

InputはUI232のheader offsetsとUI234 DATA offsetsから独立配置する。期待responseは既存test側688byte literal/JST/Role vector。Input生成にもproduction encoderを使用しない。暗号/password照合expectedは独立JCA、DBは限定API roleの実SQL後条件を正とする。

## 非合格の探索履歴

`/tmp/pgpt-login-jdbc-01.log`（SHA256 `febe9630ccdcd5159959af85123aa2e6d684039480f5a0b89ce72a338d902861`）: 新規test初回compileでjava.lang.IllegalStateExceptionとjakarta.jms.IllegalStateExceptionがwildcard importにより曖昧となり停止。test実行前であり合格算入0。JMS importを使用型の明示列挙へ直した。未実装接続testの初回compile修正であり業務仕様障害として起票していない。

正式Runは`PT-AUT-20260908-12`を予定する。対象commit/日時/環境/終了code/全counterと結果は同run-summary/manifestを正とし、成功確認前に完了としない。OS process kill、service reboot、Caddy/HTTPからの全段疎通・最終delivery処理は本PT完了範囲に含まない。
