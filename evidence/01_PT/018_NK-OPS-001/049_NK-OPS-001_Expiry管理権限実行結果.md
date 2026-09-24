# NK-OPS-001 Expiry管理権限 PT実行結果

2026-09-24、選択`PT-OPS-MQ-022`は隔離・認証有効Artemis2.56.0で1/1成功、failed/error/skipped0。保守roleのExpiry限定count/remove、DLQ/同期Queue/全件削除/Broker照会拒否、Web管理拒否、Ops既存照会/個別DLQ操作維持、一時reply Address残存0を確認。`ArtemisBrokerConfigurationTest`4/4、`ArtemisRoleReadinessClientTest`3/3、`ArtemisSecurityTest`1/1も選択合格。SSC-076/BUG-236/YKT-187は7日selectorと実削除/永続記録/起動判断が未実装のため対応中。正式全reactor/48scope/hashとcoverageは未実施でありPG243は未認定。
