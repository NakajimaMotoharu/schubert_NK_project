# C07四監視snapshot並行観測の仕様・結果

WBS-C07／F03、NK-OPS-001、MON005～013、RD171・UI252・SS351 §7／SS-D-044、PG-D-1195、BUG-3642／YKT-2861。対象はTimedFilesystemMonitor／TimedJvmHeapMonitor／TimedDbPoolMonitor／TimedSyncLatencyMonitorのsnapshot、監視側observe、公開不変Event。JDK25.0.4、実行命令・環境・元XML／execはPG42964に記録。

| Test ID | 合成入力と独立期待 |
|---|---|
| PT-OPS-MON-SNAP001 | 92%を0秒と300秒に観測しFilesystem criticalを開く。301～332秒の32更新に対し、公開snapshotは単一イベントを維持 |
| PT-OPS-MON-SNAP002 | 90% heapで300秒からcriticalを開き、32更新後の同イベントを確認 |
| PT-OPS-MON-SNAP003 | pending 1、timeout 0で300秒からDB pool criticalを開く。更新中のsnapshotでも原因キーは同じ |
| PT-OPS-MON-SNAP004 | p95 3秒の連続300秒でcriticalを開く。32更新に対し公開snapshotを照合 |

各群のreader／writerはJDKの二workerで開始を同期。読取中のcountは1～33で単調、lastSeen=300+count−1秒、firstSeen=300秒、条件／service／severity／openの独立定数を照合する。完了後count33、保存した元Eventはcount1。通信、ファイル実測、実DBやserviceなし。従来の閾値・欠落／gap・反転・時刻・生成値を含む41と新4を同原execで測る。

2026-11-23 JST、dev-foundation、source `51e8da82333e56515e059e8f32d615cafeacff37`。当45 F/E/S0。9物理の無フィルター L184/M53/C9/B84/I1003すべて不足0。通常Batch compile/jar各0、660物理中4変更、比較可能な他656のZIP CRC/長さ一致。公開ABI・snapshot以外の命令一致。NullAway・SpotBugs・Checkstyleは指摘0。PMD生10件を保持し、二重同期の4件が消えた。初回の集計はPMD件数の減少を扱えず、元成果を読み戻して訂正。製品試験と解析の再演0。現実用監視、F02/F03、全体451は未受入。

公開manifest SHA-256 `fe0942930c7a2ed746877552adfa1638b5786a7c7dab260e2add0f1bf6a9a340`。同sourceの局所結果は元41の別source結果と合算しない。
