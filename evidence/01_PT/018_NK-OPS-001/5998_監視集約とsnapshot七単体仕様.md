# Batch監視集約とsnapshotの並行一次診断

WBS-F03/2-2-b、SS351/354、BUG-3949／YKT-2997。元の固定値、64の集約入力、snapshotの32遷移と六つのunlock確認を維持する。所有workerの方式、latch順序、10秒の終了を保持する。合成観測だけを実行する。期待値の出典は次の元仕様。

| ID | 選択メソッド | 試験仕様 |
| --- | --- | --- |
| POLL007 | MonitoringPollerTest#poll007ParallelNonAtomicActionsAreSerializedIntoOneToSixtyFour | [1599](1599_監視Poll・Heap結線_単体テスト仕様書.md) |
| MONPIPE006 | MonitoringPolicyEngineTest#monPipe006ConcurrentSingleEntryKeepsOneOwner | [1549](1549_MonitoringPolicyEngine_単体テスト仕様書.md) |
| PT-OPS-MON-SNAP005 | TimedMonitorSnapshotConcurrencyTest#rejectedElapsedTimeReleasesAllSixLocks | [5738](5738_C07時系列四種・監視集約の現単体と独立測定.md) |
| PT-OPS-MON-SNAP001..004 | TimedMonitorSnapshotConcurrencyTest#verifySnapshots | [5738](5738_C07時系列四種・監視集約の現単体と独立測定.md) |

共通の一次例外と抑制例外の挙動は既存のBatch fixture診断を参照する。実行終端を現正規Batch JARの単一runに記録し、生coverageを対象クラスだけ出力する。
