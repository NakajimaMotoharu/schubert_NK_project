# NK-OPS-001 検査起動wrapper・unit 実行結果

2026-09-13 最新確定: dev-foundation/source 820554603bca7e5ddd358139f33dee27c9ae87c3、正式PT-WEB-20260913-13（09:48:33～10:04:44 JST）、全1415件（Protocol80/Storage66/API660/Web241/Batch327/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/etc・/run・/varの3 method限定静的レビューを維持しcoverage除外なし、CHR runnerのSpotBugsは未設定。15collector/38scopeの同run/source/branch/hashと41負canary成功。DB29部品266＋batch22部品241＋OPS14部品118＝65部分成果625 PT（全1415の内数）。PG169 root manifest reader16 PTとPG170共通資源scope8 PT、実保持inode/排他/Probeの複合故障回帰を認定。BUG196～197/YKT155～156完了、BUG195/SSC063の直接対象は修正済みだがYKT154の広域残候補は未完了。SSC062のreader範囲は完了。root manifest生成/実dump・tar・age/7世代・親実子制御/全cleanup接続/通常Question writer/replay/Logout RERUN001/QA045は残る。固定加重約4割（35～50%、456）を維持、残件460。実NK CHR/IT/ST完了とはしない。利用枠残19%で継続中、元dev-web3file保全。以下は履歴。

001/PT-OPS-INBOX-001～008、SS341/342/343/352・SSC-049/053/PG-D-144。実装・探索8 PT成功、正式全体回帰/独立scope/trace/hashが揃うまで合格に算入しない。19:00:57 JST合同探索3は20件成功。実systemd配布・親OS/backup gateは別未完了。

探索1（18:53:05）はSC2194 1件で19/20成功、BUG-136をdc8215d7で修正前起票。専用変数へ固定値を入れ、抑止なしで探索2（18:54:55）20件成功。NUL追加探索は壊れたreceiptをexit0としたため1失敗、BUG-137/SSC-053/YKT-107をe20a45f4で先行起票、SS937cb33c後に全byte hex検査へ修正。探索3でNUL16位置/高bit/余分LF/od失敗/JVM異常/実Java負例・ShellCheck0・baseと4profileのsystemd静的verify成功。失敗runは正式合格に算入しない。正式39予定。
