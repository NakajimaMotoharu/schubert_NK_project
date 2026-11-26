# Batchの注入binder並行試験で一次診断を保持

WBS-F03/2-2-b、SS351/354、BUG-3953／YKT-2997。元の独立binder期待256/128/192、Transferの64入力と不変snapshot、4/8workerと10秒を保持する。既試験の供給値と注入portのみであり、実JVM/OS/GCの収集や実Transferは選択しない。期待値の出典は次の元仕様。

| ID | 選択メソッド | 試験仕様 |
| --- | --- | --- |
| BATCHJVM014 | BatchJvmMetricsTest#batchjvm014FiniteConcurrentPortsDoNotShareSourceState | [1781](1781_WebBatchJvmMetrics_単体テスト仕様.md) |
| BATCHSYS014 | BatchSystemMetricsTest#batchsys014FiniteConcurrentPortsDoNotShareSourceState | [1791](1791_WebBatchSystemMetrics_単体テスト仕様.md) |
| BATCHSTD013 | BatchStandardMetricsTest#batchstd013FiniteIndependentConcurrentCompositions | [1795](1795_WebBatchStandardMetrics_単体テスト仕様.md) |
| TRANSFERCONN008 | TransferHealthMonitorTest#transferConn008ConcurrentOneOwnerHasExactCountAndImmutableOldSnapshot | [1619](1619_Transfer警報Metric結線_単体テスト仕様書.md) |

共通の一次例外と抑制例外の挙動は既存のBatch fixture診断を参照する。実行終端を現正規Batch JARの単一runに記録し、生coverageを対象クラスだけ出力する。
