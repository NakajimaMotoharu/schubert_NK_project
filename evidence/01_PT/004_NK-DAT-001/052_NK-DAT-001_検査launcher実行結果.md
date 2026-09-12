# NK-DAT-001 検査launcher 実行結果

2026-09-12 最新確定: dev-foundation/source d2d3a0809de9e9805c1907eeef74721e6b95e4bf、正式PT-WEB-20260912-01（21:00:14～21:07:39 JST）、全1117件（Protocol80/Storage50/API634/Web241/Batch71/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/runの限定静的レビュー1件は維持しcoverage除外なし、CHR runnerのSpotBugsは未設定。12collector/35scopeの同run/source/branch/hashと17負canary成功。DB26部品240＋batch3部品37＋OPS7部品50＝36部分成果327 PT（全1117の内数）、今回CFG6件を追加。BUG147/YKT115再試験完了。保持inode reader PG-D-152/EFILE8は仕様のみで未合格。親制御/backup artifact/設定publish/SSC055原本・全cleanup caller・通常Question writer/replay・Logout RERUN001・QA045は残る。進捗は456の固定加重約4割（35～50%）、残件は460を参照。実NK CHR/IT/ST完了とはしない。前回の停止を解除し利用枠残99%でPG/PT継続中、元dev-web3file保全。以下は履歴。

051/PT221～232、SS343 §6.8/SSC-049/053/PG-D-144。実装・探索12 PT成功、正式全体gateは未実行。19:00:57 JSTのwrapper合同探索3は20件成功（12 DB＋8 OPS）。探索coverageはConfiguration/Invalid/Launcherのclass3・method14・line59・branch34すべてmissed0。正式source/run/各Test ID・coverage・証跡hashは全gate成功後のみ記録。親OS/実backupを未検証のまま合格にしない。

探索commandは固定JDK25/Maven、`-pl src/schubert-nk-api -am -Dtest=InspectorDeploymentTest,InspectorLaunchConfigurationTest,InspectorLauncherTest,FieldCodecTest,StorageAttributeGuardTest test`。Protocol/Storageの2 testは依存moduleの選択用で、新12/20の件数へ重複加算しない。raw logは`/tmp/pgpt-inspector-ops-explore-3.log`に一時保持、Gitへは採取しない。正式39予定。
