# NK-OPS-001 検査起動wrapper・unit 実行結果

2026-09-12 最新確定: dev-foundation/source d2d3a0809de9e9805c1907eeef74721e6b95e4bf、正式PT-WEB-20260912-01（21:00:14～21:07:39 JST）、全1117件（Protocol80/Storage50/API634/Web241/Batch71/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/runの限定静的レビュー1件は維持しcoverage除外なし、CHR runnerのSpotBugsは未設定。12collector/35scopeの同run/source/branch/hashと17負canary成功。DB26部品240＋batch3部品37＋OPS7部品50＝36部分成果327 PT（全1117の内数）、今回CFG6件を追加。BUG147/YKT115再試験完了。保持inode reader PG-D-152/EFILE8は仕様のみで未合格。親制御/backup artifact/設定publish/SSC055原本・全cleanup caller・通常Question writer/replay・Logout RERUN001・QA045は残る。進捗は456の固定加重約4割（35～50%）、残件は460を参照。実NK CHR/IT/ST完了とはしない。前回の停止を解除し利用枠残99%でPG/PT継続中、元dev-web3file保全。以下は履歴。

001/PT-OPS-INBOX-001～008、SS341/342/343/352・SSC-049/053/PG-D-144。実装・探索8 PT成功、正式全体回帰/独立scope/trace/hashが揃うまで合格に算入しない。19:00:57 JST合同探索3は20件成功。実systemd配布・親OS/backup gateは別未完了。

探索1（18:53:05）はSC2194 1件で19/20成功、BUG-136をdc8215d7で修正前起票。専用変数へ固定値を入れ、抑止なしで探索2（18:54:55）20件成功。NUL追加探索は壊れたreceiptをexit0としたため1失敗、BUG-137/SSC-053/YKT-107をe20a45f4で先行起票、SS937cb33c後に全byte hex検査へ修正。探索3でNUL16位置/高bit/余分LF/od失敗/JVM異常/実Java負例・ShellCheck0・baseと4profileのsystemd静的verify成功。失敗runは正式合格に算入しない。正式39予定。
