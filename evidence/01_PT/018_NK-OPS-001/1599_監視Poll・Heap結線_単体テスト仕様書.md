# 1599 監視Poll・Heap結線 単体テスト仕様書

NK-OPS-001/P01809/C07、RD171/UI252/SS351、PG-D533。対象MonitoringPoller.observe/observeNow/observeLocked・JvmHeapHealthMonitor constructor/observe/observeNow/snapshot・FilesystemHealthMonitorの同順序処理抽出。時刻/読取/alert遷移を一ownerで直列化し、失敗は同一再throwし欠測flagを次回消費、context逆行はprovider操作前に拒否する。clock/入力/observerの成否とlastCompletedを分離し、null結果も成功へ正規化しない。

| Test family | 目的/独立期待値 |
|---|---|
| POLL001..008 | 正常consecutive/context/結果、Runtime/NPE/Error同一・再送0、逆行はcallback0/既連続性不変、Clock故障はcallback0/新旧APIでgap消費、null境界操作0、null結果NPE/last未commit、64並行の非atomic counterが1..64一意、失敗後の2回目成功で連続性回復。 |
| HEAPCONN001..008 | 固定MXBean→clock→75%10分warning/90%critical、max不明が回復切断、getter Runtime/NPE/Error/合成OOM同一、Clock故障前のprovider0、新旧APIのgap消費、supplied OOMはunknown usageと独立、null/逆行無副作用、service/bean分離、64並行count。 |

新16件と既監視108を同sourceで回帰する。固定MemoryUsage・UTC/nanos・SS351期間/Severity/count・独立callback countをexpectedとしproduction methodで算出0。Fixtureは既owned MXBean/Clock/FileStoreをpackage scopeで再利用（期待値の弱化0）。Heap/FS wrapperのsource snapshot/Alert recordはimmutable、pollerはcallbackを保持/closeしない。実local provider/epoch認証・collector/timeout・OOM process制御・標準exporter/Root/VM/GC/dump/JMX/ネットワーク/DB/鍵/配備・全体451/native/CHRはHOLD未受入。

constructor/null/欠落、正常/境界/異常/例外、backward・gap・再試行0/並行を通常PTと静的解析で確認し、全当scope line/method/class/branch100・実CRC/単一session・正常六Jar/traceへ結合。環境/source/branch/command/終了/XML/hash/BUG/残リスクは結果へ記録。Source/時刻/変換の失敗をFailed/UNKNOWNのまま扱い、skipped/flaky/not-runや静的代替を実行PASSへ加算しない。
