# NK-DAT-001 検査launcher 実行結果

2026-09-20 最新確定: dev-foundation/source6575b21bf467002cccda7fbb9a6980e4cdfc9a71、正式PT-WEB-20260920-06（03:13:05～03:24:50 JST、Maven11:44/exit0）、全1487件（Protocol80/Storage82/API676/Web241/Batch367/CHR41）PASS、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review/coverage除外なし、CHR SpotBugs未設定。16collector/39scope整合・52負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST1/8＝72部分成果697PT（全1487の内数）、今回再開比+72PT/+7部分成果。PG187配備設定・PG188受付IDを認定、BUG210/YKT166・SSC069限定完了。PG189/SSC070は仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/Web/Logout/QA045/実NKgateは未完了。固定加重約4割（35～50%）、残量65%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

051/PT221～232、SS343 §6.8/SSC-049/053/PG-D-144。実装・探索12 PT成功、正式全体gateは未実行。19:00:57 JSTのwrapper合同探索3は20件成功（12 DB＋8 OPS）。探索coverageはConfiguration/Invalid/Launcherのclass3・method14・line59・branch34すべてmissed0。正式source/run/各Test ID・coverage・証跡hashは全gate成功後のみ記録。親OS/実backupを未検証のまま合格にしない。

探索commandは固定JDK25/Maven、`-pl src/schubert-nk-api -am -Dtest=InspectorDeploymentTest,InspectorLaunchConfigurationTest,InspectorLauncherTest,FieldCodecTest,StorageAttributeGuardTest test`。Protocol/Storageの2 testは依存moduleの選択用で、新12/20の件数へ重複加算しない。raw logは`/tmp/pgpt-inspector-ops-explore-3.log`に一時保持、Gitへは採取しない。正式39予定。
