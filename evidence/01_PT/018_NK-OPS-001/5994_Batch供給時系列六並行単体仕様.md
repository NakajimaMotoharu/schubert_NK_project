# Batchの供給時系列と六並行試験の一次診断

WBS-F03/2-2-b、SS351/354、BUG-3948／YKT-2997。元の固定値、4または8並行・64入力、10秒の一括実行と終了を保持する。合成件数、時間、欠測値、固定ヒープ代理のみを使用する。実DB poolや稼働JVMの観測は別。期待値の出典は次の元仕様。

| ID | 選択メソッド | 試験仕様 |
| --- | --- | --- |
| DBTIME007 | TimedDbPoolMonitorTest#dbTime007ConcurrentSameEpochKeepsImmutableExactEventCount | [1603](1603_DBPool時系列警報_単体テスト仕様書.md) |
| timedFs006 | TimedFilesystemMonitorTest#timedFs006ConcurrentOwnerAndLocalStatusLiteral | [1563](1563_TimedFilesystemMonitor_単体テスト仕様書.md) |
| HEAPTIME007 | TimedJvmHeapMonitorTest#heapTime007ConcurrentSameEpochKeepsOneEventAndImmutableSnapshot | [1595](1595_JVMHeap時系列警報_単体テスト仕様書.md) |
| SYNCTIME007 | TimedSyncLatencyMonitorTest#syncTime007ConcurrentSameEpochMaintainsExactImmutableEventCounts | [1607](1607_SyncP95時系列警報_単体テスト仕様書.md) |
| heapConn008 | JvmHeapHealthMonitorTest#heapConn008ConcurrentInputsHaveExactReadsAndImmutableCountSnapshots | [1599](1599_監視Poll・Heap結線_単体テスト仕様書.md) |
| monMissing003 | MonitoringMissingObservationTest#monMissing003ConcurrentAbsencePreservesImmutableSnapshot | [1567](1567_Registry欠測接続_単体テスト仕様書.md) |

共通の一次例外と抑制例外の挙動は既存のBatch fixture診断を参照する。実行終端を現正規Batch JARの単一runに記録し、生coverageを対象クラスだけ出力する。
