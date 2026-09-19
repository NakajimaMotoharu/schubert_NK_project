# NK-DAT-001 検査launcher 実行結果

2026-09-20 最新確定: 正式PT-WEB-20260920-12/source0d0abbb80e91d016f961042e9b9e09cb07b5f7a9、05:24:36～05:36:26 JST/Maven11:48/exit0、全1544PT（Protocol80/Storage82/API689/Web285/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review継続・coverage除外追加なし、CHR SpotBugs未設定。18collector/41scope整合・60負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web4/44＝78部分成果754PT（全1544の内数）、今回再開比+129PT/+13部分成果。PG194階層3画面16PTを限定認定、BUG213～216/YKT169～172/SSC071限定範囲完了。PG195本文モデルは仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/残Web/Logout/QA045/実NKgateは未完了。固定加重38.25～49.75%（中心44%、約38～50%）、3画面接続で前回から+1 point。残量49%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

051/PT221～232、SS343 §6.8/SSC-049/053/PG-D-144。実装・探索12 PT成功、正式全体gateは未実行。19:00:57 JSTのwrapper合同探索3は20件成功（12 DB＋8 OPS）。探索coverageはConfiguration/Invalid/Launcherのclass3・method14・line59・branch34すべてmissed0。正式source/run/各Test ID・coverage・証跡hashは全gate成功後のみ記録。親OS/実backupを未検証のまま合格にしない。

探索commandは固定JDK25/Maven、`-pl src/schubert-nk-api -am -Dtest=InspectorDeploymentTest,InspectorLaunchConfigurationTest,InspectorLauncherTest,FieldCodecTest,StorageAttributeGuardTest test`。Protocol/Storageの2 testは依存moduleの選択用で、新12/20の件数へ重複加算しない。raw logは`/tmp/pgpt-inspector-ops-explore-3.log`に一時保持、Gitへは採取しない。正式39予定。
