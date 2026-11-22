# 正式原runの開始branchとcheckout排他

NK-OPS-001、WBS-G08、SS352/354、451 §6、BUG-3635／3636、YKT-2856。PT-OPS-G08-BRANCH001は同じcommitの別branchで終了と収集を拒否。002は原branchなし・異値を拒否。003は旧v1/v2の保存読取を維持し、v3のbranchと保存rootの一致を求める。PT-OPS-G08-OWN001は同checkoutの別IDを二重起動せず、第二IDを消費しない。002は異なるcheckout・IDを並行できる。003はbranch名のないcheckoutを予約前に拒否する。

PG42864、fb2404e9af、2026-11-23 JST。手順はPython 3.14、隔離Git checkout、Maven代理と固定XMLを使用。元runnerの別ID二実行、同commit別branchの成功誤認を再現。現runner9、終端16、収集器119を完走。旧正式53 scopeはGit archiveを復元先の一時領域で検証した。実製品や全回帰の起動は0。収集器のv3原rawとbranchはrunに付随し、両端で検証する。正式品質の新規認定は0。既存の週次や実環境の保留を変更しない。

flockは同runner間でcheckout固有のGit directoryを境界とし、同じIDの永久予約はcheckout間で共有する。外部から直接実行したMavenは対象外。既認定の旧形式は保存検証のみ。構文・実行日時・Git source・各試験・元結果へのリンクは[PG42864 manifest](evidence/PG42864-formal-run-provenance-fixtures-v1/manifest.json)。
