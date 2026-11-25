# 1603 DBPool時系列警報 単体テスト仕様書

この仕様のDBTIME001～008は `TimedDbPoolMonitorTest` 専用。APIの同名旧ラベルは1712に示す別suite、現API IDは[対応表](evidence/PG45500-dbtime-suite-identities-and-oracles/manifest.json)を参照。

Program NK-OPS-001/P018-09、共有C07追加費0。RD171 MON005～013/UI252/SS351§7/10、PG-D534。TimedDbPoolMonitor constructor/observe/snapshot/Evaluation、独立DBTIME001～008。実JDBC/DB/Hikari接続・操作はしない。fixtureは明示percent/既知pending・timeout件数/UTC・monotonic経過だけ、未知countを0で代用する呼出は禁止。

| Test ID | 目的・入力/操作 | 独立期待値・算出根拠 |
|---|---|---|
| DBTIME001 | 80%の0/299.999999999/300秒、正常301/600/601秒 | SS351の80%以上5分でWARNING、5分正常でclose |
| DBTIME002 | pending=1とtimeout=1を別ownerで0秒、0件正常1/600/601秒、原因未/確認 | どちらも即CRITICAL、正常10分＋原因撤去でのみclose |
| DBTIME003 | percent未知→80%0/299→未知300→80%301/600/601、正常中未知 | 未知は0%/正常でない、違反と回復両方の連続期間を切断 |
| DBTIME004 | percent未知＋pending/timeout各1、未知＋両0 | 独立既知countはcritical、usage-present=false、両0だけで未知percentを正常化しない |
| DBTIME005 | null service/record/context/percent、NaN/無限/負/100超、負count、逆行 | 例外・既snapshot/個数不変、invalidをcriticalで隠さない |
| DBTIME006 | 明示gap直前/丁度、warning→critical→warning域、正常復帰 | windowを再起点、critical sticky、原因確認/正常期間を満たすまでopen |
| DBTIME007 | 64並行同elapsedでpending1 | 全critical、実count65、旧snapshot immutable、所有混同なし |
| DBTIME008 | 79.999/80/100境界、Long.MAX_VALUE既知counts、別API/WEB owner | 直前normal、80は300秒、100も最小持続あり、count加算overflowなし、owner独立 |

新8＋必要既124を当source固定後ordinary Maven verify、各XML method/終了/FES0とJaCoCo単一session/実CRC/allMain四counter100、NullAway/negative・lint/Werror/SB/CS/PMD個別適用性を独立post。実行command・JDK/OS/tool/commit・開始終了・原XML・coverage・静的結果・hashはPG7224/7226以降のmanifestと結果1604へ結合予定。未実行は未実行、旧124・4222/common44を現在の成功へ流用しない。BUGは発見時起票して修正前の証拠を保存する。

実pool sampling/timeout観測期間/provider接続・標準exporter・Root/finite collector/owned停止/制御/native/CHR/全体451は未受入HOLD。正式1964/53・原190受入/工数null・QA051final/PTALT0は更新しない。
