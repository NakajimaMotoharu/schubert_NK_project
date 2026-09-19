# NK-OPS-001 検査起動wrapper・unit 実行結果

2026-09-20 最新確定: dev-foundation/source139c74b3dd844a213bf5581d51f4814219386497、正式PT-WEB-20260920-05（02:55:42～03:07:25 JST、Maven11:42/exit0）、全1479件（Protocol80/Storage82/API668/Web241/Batch367/CHR41）PASS、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review/coverage除外なし、CHR SpotBugs未設定。15collector/38scope整合・49負canary成功。DB29/266＋Batch25/281＋OPS16/134＝70部分成果681PTを維持。PG187の8PT成功・BUG208/209/YKT164/165完了だが、BUG210/YKT166のTest ID表記差が残りSSC069/新OPS1部分成果は保留。今回再開比+64PT/+5部分成果。PG188受付IDは仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/Question/Web/Logout/QA045/実NKgateは未完了。固定加重約4割（35～50%）、利用枠残68%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

001/PT-OPS-INBOX-001～008、SS341/342/343/352・SSC-049/053/PG-D-144。実装・探索8 PT成功、正式全体回帰/独立scope/trace/hashが揃うまで合格に算入しない。19:00:57 JST合同探索3は20件成功。実systemd配布・親OS/backup gateは別未完了。

探索1（18:53:05）はSC2194 1件で19/20成功、BUG-136をdc8215d7で修正前起票。専用変数へ固定値を入れ、抑止なしで探索2（18:54:55）20件成功。NUL追加探索は壊れたreceiptをexit0としたため1失敗、BUG-137/SSC-053/YKT-107をe20a45f4で先行起票、SS937cb33c後に全byte hex検査へ修正。探索3でNUL16位置/高bit/余分LF/od失敗/JVM異常/実Java負例・ShellCheck0・baseと4profileのsystemd静的verify成功。失敗runは正式合格に算入しない。正式39予定。
