# PG289 横断回帰結果（正式不認定）

2026-09-27 16:44頃～16:58:16 JST、branch dev-foundation、基点385b7ccaf＋PG289 dirty。trigger: SSC084 POM/security所有境界変更、D01/02/05。対象source hash/XML hashはprovisional/PG289/manifest.json。秘密情報を出力証跡に保存しない。

Production6 module 1,944PT、fail/error/skip0、SpotBugs全module0。Protocol80/Storage101/Bootstrap64/API740/Web555/Batch404。Bootstrap他5moduleの全対象counter missed0、APIはnative main7instruction/2line/1method未網羅（branch/class missed0）。未結線必須gateの成功経路を迂回/coverage除外せず、正式不認定。105負canary成功、BUG264/YKT198限定確認、正式全scope照合は次の受入gate待ち。

初回のroot全module追加SpotBugs診断はCHR runner11件でexit1。規定Production解析成功へ上書きせず未認定の追加所見を保存。prefix解決失敗等のnot-runも成功件数へ算入しない。Current baselineは不変更。隔離VMは別424記録、実Production app受入に算入しない。
