# NK-OPS-001 Artemis起動前観測PT実行結果

2026-09-25 PG267/PT-OPS-MQ-029～031選択段階: JDK25.0.4/Maven3.9.12/Linux、branch `dev-foundation`、未commit差分で`ArtemisStartupObservationTest` 3/3、failure/error/skipped0。Production class instruction125/125・line24/24・method4/4・class1/1・branch2/2。初回選択runはtest-only proxyが`addressQuery`で投げるfatalを固定Runtimeと誤期待し1failure/exit1、試験oracleをfatal identityへ修正して再実行した。不合格試行を正式合格に含めない。証明対象は既存6実Broker個別clientの順序・失敗遮断・6件不変snapshotであり、全体Broker readinessや外部API/Web起動ではない。正式全reactor/静的解析/保存manifest/hashは未実施で不認定。
