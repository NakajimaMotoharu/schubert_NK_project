# NK-OPS-001 RootServiceLauncher 実外部拒否限定PT結果（PG375）

仕様[260](260_NK-OPS-001_RootLauncher実外部拒否限定仕様書.md)。2026-09-29 JST、branch `dev-foundation`、Production source `12db53bb3`（PG375 Production source変更なし）。隔離VM kernel7.0.0-31-generic x86_64、JDK25.0.4。現行Production Batch/Storage/Bootstrap/Protocolの同byte classをprivate staging JARにまとめ、VMへhash一致転送。root外部JVMで`RootServiceLauncher WEB`、`API`、`OTHER`を各1回起動した。

| Test ID | 独立期待値 | 実測/判定 |
|---|---|---|
| PT-OPS-RMAIN007 | WEBの必須gate不足ではexit30、秘密出力0 | WEB_EXIT=30、stdout/stderr空。限定PASS |
| PT-OPS-RMAIN008 | APIの必須gate不足ではexit30、秘密出力0 | API_EXIT=30、stdout/stderr空。限定PASS |
| PT-OPS-RMAIN009 | OTHERはargv拒否exit70、秘密出力0 | OTHER_EXIT=70、stdout/stderr空。限定PASS |

前後とも元`schubert-nk-morning-controller.service` loaded/inactive/MainPID0、Web/API Unit not-found/inactive/MainPID0、Production `/run/schubert-nk/backup-request`内容空。起動JVMは各command終了後残存なし。VM stageの4 JARを個別削除し専用directoryをrmdirした。current/permit/DBのbefore-after内容hashや正規releaseの成功経路は今回採取しておらず、この3件は**拒否exitとUnit/markerの限定契約**だけの合格である。Unit起動・A/proof/余剰FD/同PID exec/業務readyやR2/R3/CHRは未実行。Production source不変更につき全6再run・coverage更新なし、PG372 2,509PT/369suiteは別の限定run。raw環境/credential/journalは保存しない。

Batch JAR SHA-256 `2c94c0383fe2bb288bb6a2e6a44f00073f20efd39ec5295ab5f2726dba7f6816`、Storage `52f5aa6061881ae8bd7205e936d5803a2006a23463e5c5eca8b700007b86a2b7`、Bootstrap `9e2fc45835a7bb0a0d97d8f72f9691eb6a2b19d824ff864afc3c96f279f4f291`、Protocol `de4e3c34c92767a4476a74c9141f17b9e4b118b15547efa5d893b91e3c651d57`。詳細command/input/exit/期待実際はmanifest。BUG322/SSC107とは別に、真正root Launcherの発行済permit/全root/Ops/schema/held ELF/FD/同PID置換がR1/D04/05の未達。
