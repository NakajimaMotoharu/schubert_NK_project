# Batch監視の純粋値と並行試験の一次診断

WBS-F03/2-2-b、SS351/354、BUG-3942／YKT-2997。元の固定値、4又は8並行・64入力、10秒の一括実行と終了を保持する。metric表・状態表示・固定clock・modeの純粋値を使用する。期待値の出典は次の元仕様。

| ID | 選択メソッド | 試験仕様 |
| --- | --- | --- |
| metric006 | MetricContractTest#metric006ConcurrentCallersObserveOnlyOriginalCatalog | [1543](1543_MetricContract_単体テスト仕様書.md) |
| monStatus006 | MonitoringStatusTextTest#monStatus006ConcurrentStatelessFormatting | [1558](1558_MonitoringStatusText_単体テスト仕様書.md) |
| OBSCLOCK007 | MonitoringObservationClockTest#obsClock007ConcurrentContextsHaveUniqueMonotonicSnapshots | [1586](1586_監視Clock時系列_単体テスト仕様書.md) |
| monMode007 | MonitoringModePolicyTest#monMode007ConcurrentCallersCannotChangePolicy | [1541](1541_MonitoringModePolicy_単体テスト仕様書.md) |

共通の一次例外と抑制例外の挙動は既存のBatch fixture診断を参照する。実行終端を現正規Batch JARの単一runに記録し、生coverageを対象クラスだけ出力する。
