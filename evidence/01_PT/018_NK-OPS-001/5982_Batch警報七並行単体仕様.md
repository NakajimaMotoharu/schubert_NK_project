# Batchの供給値七警報と並行試験の一次診断

WBS-F03/2-2-b、SS351/354、BUG-3945／YKT-2997。元の固定値、8並行・64入力、10秒の一括実行と終了を保持する。合成の件数・閾値・時刻を使用し、実Backup・DB・キュー・systemdへ接続しない。期待値の出典は次の元仕様。

| ID | 選択メソッド | 試験仕様 |
| --- | --- | --- |
| BACKUPMON006 | BackupHealthMonitorTest#backupMon006ConcurrentSameOwnerKeepsExactCountAndOtherOwnerIndependent | [1683](1683_Backup供給観測警報_単体テスト仕様書.md) |
| INTEGRITYMON007 | IntegrityHealthMonitorTest#integrityMon007ConcurrentCallersKeepExactCountAndIndependentOwner | [1687](1687_Integrity供給観測警報_単体テスト仕様書.md) |
| RESTARTMON006 | RestartHealthMonitorTest#restartMon006ConcurrentSameOwnerAndDifferentOwnerKeepExactEvents | [1685](1685_Restart供給観測・rateLimit是正_単体テスト仕様書.md) |
| WEBLOG007 | WebLogBacklogMonitorTest#webLog007ConcurrentSameOwnerAndIndependentOwnerHaveExactCounts | [1672](1672_WebLog滞留警報_単体テスト仕様書.md) |
| EXPIRYMON007 | ExpiryBacklogMonitorTest#expiryMon007ConcurrentSameOwnerAndIndependentOwnerHaveExactCounts | [1676](1676_Expiry件数警報_単体テスト仕様書.md) |
| DLQMON006 | DlqHealthMonitorTest#dlqMon006ConcurrentSameOwnerAndSeparateOwnerKeepExactCounts | [1689](1689_DLQ供給観測警報_単体テスト仕様書.md) |
| ASYNCQUEUE007 | AsyncQueueMonitorTest#asyncQueue007ConcurrentSameOwnerAndIndependentOwnerHaveExactCounts | [1674](1674_AsyncQueue警報_単体テスト仕様書.md) |

共通の一次例外と抑制例外の挙動は既存のBatch fixture診断を参照する。実行終端を現正規Batch JARの単一runに記録し、生coverageを対象クラスだけ出力する。
