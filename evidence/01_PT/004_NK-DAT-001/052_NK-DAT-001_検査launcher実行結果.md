# NK-DAT-001 検査launcher 実行結果

2026-09-20 最新確定: dev-foundation/sourcefa490cdf8f8e36adf550082bf025b31a5c232220、正式PT-WEB-20260920-09（04:12:23～04:24:05 JST、Maven11:40/exit0）、全1508件（Protocol80/Storage82/API689/Web249/Batch367/CHR41）PASS、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review/coverage除外なし、CHR SpotBugs未設定。17collector/40scope整合・56負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web1/8＝75部分成果718PT（全1508の内数）、今回再開比+93PT/+10部分成果。PG190空回答providerを限定認定、workerは未実装。PG191 Scenario通信8PTを限定認定、PG192 Page表示モデルは仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/Web/Logout/QA045/実NKgateは未完了。固定加重約4割（35～50%）、残量57%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

051/PT221～232、SS343 §6.8/SSC-049/053/PG-D-144。実装・探索12 PT成功、正式全体gateは未実行。19:00:57 JSTのwrapper合同探索3は20件成功（12 DB＋8 OPS）。探索coverageはConfiguration/Invalid/Launcherのclass3・method14・line59・branch34すべてmissed0。正式source/run/各Test ID・coverage・証跡hashは全gate成功後のみ記録。親OS/実backupを未検証のまま合格にしない。

探索commandは固定JDK25/Maven、`-pl src/schubert-nk-api -am -Dtest=InspectorDeploymentTest,InspectorLaunchConfigurationTest,InspectorLauncherTest,FieldCodecTest,StorageAttributeGuardTest test`。Protocol/Storageの2 testは依存moduleの選択用で、新12/20の件数へ重複加算しない。raw logは`/tmp/pgpt-inspector-ops-explore-3.log`に一時保持、Gitへは採取しない。正式39予定。
