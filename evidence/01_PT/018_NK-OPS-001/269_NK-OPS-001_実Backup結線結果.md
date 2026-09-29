# PG379 実Backup結線結果（途中・未認定）

2026-09-30 JST、dev-foundation、source固定commitは後続manifestに記録。host Java25.0.4/Maven3.9.12/Node24.19.0、全コマンドは固定JAVA_HOME/PATH/m2/`-Dnk.pt.node`でbatch選択`spotless:apply test`。8suite/75PTの最終選択run41269 exit0、F/E/S=0/0/0（07:31:32 JST）。BGATE009/BUCYCLE008/MBSTAGE009/MDB015/ARCHPROC009はhost限定PASS、実VM MBACKUP001は未実行。期待値は268の固定wire/call順・独立SQL/count値・残7ns。

失敗履歴：最初の24PTは旧順序oracleと追加root再確認でF1/exit1。次33PTはPASS。DB port追加後64PTでMDB015 E1（BUG326: readback transaction欠落）。修正後64PTは製品処理を通過したがobserver側advisory不足でE1、fixture前提を補正後75PT F/E/S0。失敗runは合格に算入しない。BUG325/326、YKT257/258の直接host再試験だけで台帳全体・実親完了にしない。

source `91c1e8692`の全6 clean testは2,522PT（80/149/181/756/565/791）F/E/S0。ただしBatch SpotBugsの完了state非volatile2件で全command exit1、静的gate不合格（BUG328）。clean verifyはBootstrap既存未網羅でexit1、API/Web/Batch not-run。成功扱いにしない。raw外部log `work/pgpt-runs/PG379/six-provisional.log` SHA256 `bb6dcd287fd804f24d9fd9b0de09a0ed93ebe31706aff5868cf9ef34021aa3e2`。次sourceでの15PT/static0再試験は270/271の別記録とし、元runをPASSへ書換えない。

実Main/固定全8Unit/実archive assemblyは未結線、S1未完了。全Coverage100%/collector gate未達、既存正式run24/1,964PT/中心48.3%を更新しない。隔離VMは復帰しPostgreSQLonline、Caddyactive、Morning/Backup/Artemisloaded inactive、Cleanup/Inspector/Expiry/API/Webnot-found。前回test-only Morning Unit/drop-insは不変更、原本/credential/DBdumpはGit外保全。

次は同source群の全6回帰/static/未網羅採取→親budget/実bundleと正規Expiry配備の同経路依存を接続→固定外部Morningから実Backupを採取する。レビューは6.1Sol/ultra一名の読取限定で実施済、再委任/共有編集なし。
