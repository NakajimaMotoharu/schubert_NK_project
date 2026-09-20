# NK-OPS-001 検査起動wrapper・unit 実行結果

2026-09-20 最新確定: 正式PT-WEB-20260920-25/source42d8bfbf0c0d88a27ba29a8f9cf0054d5cdacc58、09:26:44～09:39:24 JST/Maven12:39/exit0、全1679PT（Protocol80/Storage82/API689/Web420/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review継続・coverage除外追加なし、CHR SpotBugs未設定。JS1file全line/function/branch100%、18collector/41scope整合・76負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web20/179＝94部分成果889PT（全1679の内数）、今回再開比+264PT/+29部分成果。PG210 Music通信8PT・PG211分類/区分HTTP12PTを限定認定、BUG223/YKT179完了。PG212～214 Log表示/通信/入力は仕様のみ・SSC073対応中。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/残Web・本文controller-file/readiness/Logout/QA045/実NKgateは未完了。Music2画面HTTP接続を根拠にWeb38～53%・固定加重40.85～52.35%（中心46.6%≒47%、約41～52%）へ更新。残量16%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

001/PT-OPS-INBOX-001～008、SS341/342/343/352・SSC-049/053/PG-D-144。実装・探索8 PT成功、正式全体回帰/独立scope/trace/hashが揃うまで合格に算入しない。19:00:57 JST合同探索3は20件成功。実systemd配布・親OS/backup gateは別未完了。

探索1（18:53:05）はSC2194 1件で19/20成功、BUG-136をdc8215d7で修正前起票。専用変数へ固定値を入れ、抑止なしで探索2（18:54:55）20件成功。NUL追加探索は壊れたreceiptをexit0としたため1失敗、BUG-137/SSC-053/YKT-107をe20a45f4で先行起票、SS937cb33c後に全byte hex検査へ修正。探索3でNUL16位置/高bit/余分LF/od失敗/JVM異常/実Java負例・ShellCheck0・baseと4profileのsystemd静的verify成功。失敗runは正式合格に算入しない。正式39予定。
