# NK-OPS-001 検査起動wrapper・unit 実行結果

2026-09-20 最新確定: dev-foundation/source 1d5b44ad26736366950936653914f67e7e096fe2、正式PT-WEB-20260920-03（02:01:07～02:16:34 JST、Maven15:26/exit0）、全1463件（Protocol80/Storage74/API660/Web241/Batch367/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定path3method限定静的レビュー・coverage除外なし、CHR runnerのSpotBugsは未設定。15collector/38scopeの同run/source/branch/hashと48負canary成功。DB29部品266＋Batch25部品281＋OPS15部品126＝69部分成果673 PT（全1463の内数）。今回9月19日再開比+48 PT/+4部分成果、PG184のroot検証・全4file照合からDB両step原子確定caller8PTを追加認定しSSC067限定完了。PG178～183のSQL資源905複合は既存Test ID内で新件数増算0。BUG195/206・YKT154/162・SSC063の別境界分類は継続。PG185試験並列化/PG186・SSC068 private子生成は仕様のみ。実archive/7世代/親実子制御/全cleanup/通常Question/Web/Logout/QA045/実NK互換gateは未完了、固定加重約4割（35～50%、456）を維持。利用枠残76%で継続、元dev-web3file保全、IT/ST完了ではない。以下は履歴。

001/PT-OPS-INBOX-001～008、SS341/342/343/352・SSC-049/053/PG-D-144。実装・探索8 PT成功、正式全体回帰/独立scope/trace/hashが揃うまで合格に算入しない。19:00:57 JST合同探索3は20件成功。実systemd配布・親OS/backup gateは別未完了。

探索1（18:53:05）はSC2194 1件で19/20成功、BUG-136をdc8215d7で修正前起票。専用変数へ固定値を入れ、抑止なしで探索2（18:54:55）20件成功。NUL追加探索は壊れたreceiptをexit0としたため1失敗、BUG-137/SSC-053/YKT-107をe20a45f4で先行起票、SS937cb33c後に全byte hex検査へ修正。探索3でNUL16位置/高bit/余分LF/od失敗/JVM異常/実Java負例・ShellCheck0・baseと4profileのsystemd静的verify成功。失敗runは正式合格に算入しない。正式39予定。
