# 1595 JVMHeap時系列警報 単体テスト仕様書

NK-OPS-001/P01809/C07、RD171/UI252/SS351§7、PG-D532。対象TimedJvmHeapMonitor constructor/observe/snapshot/Evaluation constructor、既AlertThresholds/ContinuousConditionWindow/AlertLifecycleへの接続。supplied percentとoutOfMemoryReported booleanは入力値・報告であって、実heap測定/OOM発生/プロセス制御の証明ではない。実OOMをcatchしたりGC/dump/停止を行わない。実source/時計/ownerへの連結は後続。

| Test ID | 入力・観点 | 独立期待値 |
|---|---|---|
| HEAPTIME001 | 75%の599.999999999秒/600秒と5分正常 | 前者未発火/600 warning、正常5分でclose。 |
| HEAPTIME002 | 90%即時、10分正常/原因未確認→確認 | 即時critical、原因未確認ではclose0、10分＋確認でclose。 |
| HEAPTIME003 | UNKNOWN/gapと75%継続・正常回復 | 未観測を正常にせず両期間を切断、count/firstSeen保持。 |
| HEAPTIME004 | percentなし＋OOM報告true、次UNKNOWN | suppliedValue=falseのままcritical、usage0%を捏造0、既event保持。 |
| HEAPTIME005 | null/service/null event/NaN/Inf/負/>100/context逆行 | 境界拒否、OOM報告で不正percentを隠蔽0、既状態不変。 |
| HEAPTIME006 | 正常期間途中の非consecutive、warning前gap | 正常/違反期間を再開始し早期close/発火0。 |
| HEAPTIME007 | 64並行同epoch/snapshot不変 | 同一key/critical維持・一意count65、旧immutable snapshot変異0。 |
| HEAPTIME008 | warning→critical→warningレベル/OOM報告 | critical sticky、同condition/serviceの一event継続、OOM報告は使用率不明と独立。 |

期待値はSS351の75%10分/90%即時・Warning5分正常/Critical10分正常＋原因撤去と固定UTC/elapsed/countから独立作成、production threshold methodでexpectedを作らない。新8と既監視100を同sourceで回帰、Failed/flaky/skipped/not-runをPASSへ入れない。private lock一方向・getter snapshotを並行確認。通常親lint/Werror/NullAway/Spotless/SpotBugs、実クラスCRC/四counter/static全指摘/正常六Jar/traceを結合する。環境/source/command/終了/XML/hash/BUGは結果へ記録。実Root/VM/GC/dump/JMX/ネットワーク/DB/鍵/配備/全体451/native/CHR/正式認定はHOLD未受入のまま。
