# Batch監査metricの並行一次機能

WBS-F03/2-2-b、SS351/354、BUG-3952／YKT-2997。元のfixtureから独立合算した各組の集計、64観測、旧snapshotと借用registry、8worker・10秒を保持。実ファイル・process・integrityの照会や環境監視は使わない。期待値の出典は次の元仕様。

| ID | 選択メソッド | 試験仕様 |
| --- | --- | --- |
| TRANSFERMET007 | TransferMetricRecorderTest#transferMet007ConcurrentAtomicSnapshotNeverMixesCohortsOrChangesOldValues | [1615](1615_Transfer二Metric記録_単体テスト仕様書.md) |
| INTEGRITYMET007 | IntegrityFailureMetricRecorderTest#integrityMetric007ConcurrentTotalsComeFromPrecomputedInputsAndOwnersStaySeparate | [1708](1708_BatchIntegrityMetric_単体テスト仕様書.md) |
| RESTARTMET007 | ProcessRestartMetricRecorderTest#restartMetric007ConcurrentTotalsComeFromPrecomputedInputsAndOwnersStaySeparate | [1710](1710_ProcessRestartMetric_単体テスト仕様書.md) |

共通の一次例外と抑制例外の挙動は既存のBatch fixture診断を参照する。実行終端を現正規Batch JARの単一runに記録し、生coverageを対象クラスだけ出力する。
