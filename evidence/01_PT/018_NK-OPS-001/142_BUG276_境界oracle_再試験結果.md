# BUG276 境界oracle再試験結果

Source1f6b1fec3/dev-foundation固定、2026-09-28 01:01:21 JST終了、exit0。Batch476/Storage149/Bootstrap127、計752PT、failure/error/skipped0、3module静的0。Boundary内の独立negativeはAPI/Web/Protocol/未知class/wildcard依存を拒否し、固定Bootstrap classと実配置だけを許可。Production/POM/上位仕様不変更。105canary成功、初期限定command2回のdependency no-tests失敗は不合格保存。

全suite/XML/hash/source digest/coverage/static/logはevidence/provisional/BUG276-regression/manifest.json。修正前6module2121中1failedのmanifestは別保存。Protocol/API/Webはsource3002ab8f9で成功済み、本test-only是正後は再実行していないので同一全runに読み替えない。Bootstrap native入口とBatch Worker NativePorts/mainのhost coverage gapは除外しない。Worker byte hashはPG309 native025と同一、既存same-byte host/native merged counter0を保全しているが、whole scope認定ではない。formal run24/1964/53scope/48.3%不変更。

BUG276/YKT209は本件の境界oracle・全対象検索/非該当根拠/negative/Batch依存全回帰範囲で再試験完了。BUG272～275/YKT206～208も直接限定の修正が依存全回帰で成功した。BUG271/YKT205は親M/A全cgroup接続未達のため対応中を維持する。次はSSC093/root親の真正cold/fresh終端と連続M/A/DB原本接続、通常区切り停止なし。
