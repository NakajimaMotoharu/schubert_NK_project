# NK-OPS-001 Expiry管理権限 PT実行結果

2026-09-24、選択`PT-OPS-MQ-022`は隔離・認証有効Artemis2.56.0で1/1成功、failed/error/skipped0。保守roleのExpiry限定count/remove、DLQ/同期Queue/全件削除/Broker照会拒否、Web管理拒否、Ops既存照会/個別DLQ操作維持、一時reply Address残存0を確認。`ArtemisBrokerConfigurationTest`4/4、`ArtemisRoleReadinessClientTest`3/3、`ArtemisSecurityTest`1/1も選択合格。

正式`PT-WEB-20260924-36`/対象source `bbc3460c9732a650c143f0812344b401fd130b58`、全1830PT（CHR41/Protocol80/Storage82/API723/Web513/Batch391）、failed/error/skipped0。Java6 module全instruction/line/method/class/branch missed0、Production SpotBugs0、98負canary、48scope/hash・保存manifest再照合PASS。root `evidence/01_PT/008_NK-SCN-001/evidence/manifest.json` SHA-256 `7dd415d272659c8c512e48250b265527844990ed87bb42cb3cdbbc4a0c451726`、本program `evidence/01_PT/018_NK-OPS-001/evidence/manifest.json` SHA-256 `7668a4d5daa819fe7400a1bec45ce0565bf86c51f094a04efad4d8f818a13f17`。PG243のRBAC範囲のみ正式限定認定。SSC-076/BUG-236/YKT-187は7日selectorと実削除/永続記録/起動判断が未実装のため対応中。
