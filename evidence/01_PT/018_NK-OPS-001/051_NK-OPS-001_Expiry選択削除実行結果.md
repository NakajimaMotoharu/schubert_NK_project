# NK-OPS-001 Expiry選択削除 PT実行結果

2026-09-24、選択PT-OPS-MQ-023～026の4/4成功、failed/error/skipped0。固定7日cutoff、選択0で削除呼出0、各計数異常/例外/null、空selector/全件削除拒否、隔離・認証有効Artemis2.56.0の実Expiry属性境界（同時刻保持・+1ms削除1件）、byte前後/返信Address cleanupを確認。続くBatch `clean verify`は全395PT、failed/error/skipped0、111 Production classの全coverage check達成/SpotBugs0、98負canaryPASS。正式全reactor/48scope/hashは未実施のためPG244は未認定。初回実Broker PTの`messageCount`取得失敗はBUG-236/SSC-076の未完了権限範囲で`getMessageCount`/`getPersistentSize`へ補正して再試験した。親の`batch_runs`記録、Broker health/critical、同run再実行とProduction credential/起動順は未完了。
