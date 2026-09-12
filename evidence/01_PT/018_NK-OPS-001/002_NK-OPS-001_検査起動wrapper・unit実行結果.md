# NK-OPS-001 検査起動wrapper・unit 実行結果

2026-09-13 最新確定: dev-foundation/source af2526dda0e64ca3d0a427a66fd9335afff836ae、正式PT-WEB-20260913-11（08:08:31～08:24:20 JST）、全1375件（Protocol80/Storage58/API660/Web241/Batch295/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/etc・/run・/varの3 method限定静的レビューを維持しcoverage除外なし、CHR runnerのSpotBugsは未設定。15collector/38scopeの同run/source/branch/hashと36負canary成功。DB29部品266＋batch19部品209＋OPS13部品110＝61部分成果585 PT（全1375の内数）。PG167 Inspector状態/終端観測16 PT、独立373byte18field・3query/fresh receipt・全11native境界/複合close/NULL/64並行を認定、BUG187～190/YKT147～150完了。SSC060のread-only観測範囲は完了、実子起動/停止/quarantine/OS排他寿命はSSC049/R003へ残す。親実子制御/全cleanup接続/通常Question writer/replay/Logout RERUN001/QA045は残る。PG168/SSC061のbackup両step確定16 PTは仕様先行・未算入。固定加重約4割（35～50%、456）を維持、残件460。実NK CHR/IT/ST完了とはしない。利用枠残29%で継続中、元dev-web3file保全。以下は履歴。

001/PT-OPS-INBOX-001～008、SS341/342/343/352・SSC-049/053/PG-D-144。実装・探索8 PT成功、正式全体回帰/独立scope/trace/hashが揃うまで合格に算入しない。19:00:57 JST合同探索3は20件成功。実systemd配布・親OS/backup gateは別未完了。

探索1（18:53:05）はSC2194 1件で19/20成功、BUG-136をdc8215d7で修正前起票。専用変数へ固定値を入れ、抑止なしで探索2（18:54:55）20件成功。NUL追加探索は壊れたreceiptをexit0としたため1失敗、BUG-137/SSC-053/YKT-107をe20a45f4で先行起票、SS937cb33c後に全byte hex検査へ修正。探索3でNUL16位置/高bit/余分LF/od失敗/JVM異常/実Java負例・ShellCheck0・baseと4profileのsystemd静的verify成功。失敗runは正式合格に算入しない。正式39予定。
