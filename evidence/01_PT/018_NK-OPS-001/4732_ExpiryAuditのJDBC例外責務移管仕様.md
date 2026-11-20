# ExpiryAuditのJDBC例外責務移管仕様

NK-BAT-001／DAT-009／OPS-009、UI251、SS311・331・332・341、SSC-461、BUG-3233、YKT-2680、WBS-F02/SYS-005、PT-BAT-284～287。

対象は `ExpiryAuditRepository.successful`、`stage`、`finish`、`read` のJDBC例外処理。元の呼出しを既存 `JdbcFailureGraph` へ移し、SQL next・cause・suppressedの走査とfatalの伝播を維持する。

| Test ID | fixtureと操作 | 期待値 |
| --- | --- | --- |
| PT-F02-EXPIRY-GRAPH-001 | 4入口。借用JDBC proxyは参照検査に一行を返し、対象SQLのprepareでnext例外のcauseに合成Errorを持つSQLExceptionを投げる | 入口ごとに同じError objectが出る。参照SQL一回、行とstatementは各1回解放、対象SQLを一度だけ試行。接続のcommit・rollback・closeなし |
| PT-F02-EXPIRY-GRAPH-002 | 同4入口、fatalを持たない合成SQLException | 入口ごとに固定文のBatchRepositoryException、causeなし、suppressedなし。参照資源後条件とSQL順序は001と同じ |
| PT-F02-EXPIRY-GRAPH-003 | 元・新sourceを比較し、対象4呼出しのみ既存分担に変更 | 公開ABI・SQL・owner指示・動的条件式は元と同じ。4入口の独立期待値を変更しない |

fixtureは独立で固定した時刻・カウント、JDKのインメモリproxyのみ。接続文字列・外部DB・実削除・brokerを使用しない。正常CRUD、nullと欠落、並行、再実行、全branch・全451、旧Storage JDBC入口は元試験と後続条件で継続する。実行環境・command・input/output hash、実測coverageと障害対応は証票に記録する。
