# NK-DAT-001 検査launcher 実行結果

正式PT-WEB-20260909-40/source2dfbaaf533012c4720d1626241ec6243b74d7fcd、dev-foundation、2026-09-09 19:22:08～19:29:08 JST、exit0。新12 PT/全1067件（Protocol80/Storage42/API634/Web241/Batch29/CHR41）PASS、failed/error/skipped0。6 Java moduleの4coverage100%、Production5 module静的解析PASS。Configuration/Invalid/Launcher合計class3/method14/line59/branch34 missed0。35scope/12collector/14負canary同run・source・hash一致。evidence/inspector-launch/manifest.json SHA-256 `15a10c956dc1e967f60aad6dca6d3223512bb09d85db5f75b21a02592a5cafb3`、root manifest `5bf54aa70ad4e01eafc570202447c70ac19ee8c670396538b3449af405777dc6`。以下は探索履歴。

051/PT221～232、SS343 §6.8/SSC-049/053/PG-D-144。実装・探索12 PT成功、正式全体gateは未実行。19:00:57 JSTのwrapper合同探索3は20件成功（12 DB＋8 OPS）。探索coverageはConfiguration/Invalid/Launcherのclass3・method14・line59・branch34すべてmissed0。正式source/run/各Test ID・coverage・証跡hashは全gate成功後のみ記録。親OS/実backupを未検証のまま合格にしない。

探索commandは固定JDK25/Maven、`-pl src/schubert-nk-api -am -Dtest=InspectorDeploymentTest,InspectorLaunchConfigurationTest,InspectorLauncherTest,FieldCodecTest,StorageAttributeGuardTest test`。Protocol/Storageの2 testは依存moduleの選択用で、新12/20の件数へ重複加算しない。raw logは`/tmp/pgpt-inspector-ops-explore-3.log`に一時保持、Gitへは採取しない。正式39予定。
