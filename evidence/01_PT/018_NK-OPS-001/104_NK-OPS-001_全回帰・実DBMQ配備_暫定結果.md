# PG293横断回帰・実DB/MQ配備（正式不認定）

Source c4ec7d9b8/dev-foundation固定、2026-09-27 18:52:50 JSTまでにProduction6module 1985PT（80/141/71/734/555/404）、fail/error/skipped0、全module SpotBugs0/NullAway/Werror成功。triggerは441 PG-D-293の共通native security差分/D04・05。API/Web native main各9instruction/3line/1method未網羅、除外0、全起動gate未組立なので正式合格にしない。

最初のclean verifyはAPI coverage gateでexit1（18:43:19）。同sourceのcurrent jar/test-jarを固定Maven install-file3.1.2でcacheし、API静的解析とWeb/Batch clean test＋report＋静的解析を継続してexit0（18:52:50）。coverage checkを緩めず、最後のcommand成功を全gate成功へ読み替えない。source/test/config/toolsは全検証中固定、473の管理review記録だけ追加した。全scope収集/正式CHRは未実行。

## 独立native Test IDとoracle

| Test ID / 実行 | 独立期待値・実際値 / 未達 |
|---|---|
| PT-OPS-NATIVE-011 / NativeBrokerProbe | 固定loopback61616、generated Ops資格情報→実Core session。Production ArtemisStartupObservationの6 topology/管理実効/address設定/acceptor/roles/pressure検査成功、全6Queue NORMAL。Root/PID1/current permit/Expiry/journal recovery/fullgate未達 |
| PT-OPS-NATIVE-012 / ProvisionDatabase migrate | 固定専用schubert_migration/SET ROLE nk_owner、commit済V001～022を専用VM schubert_nkへ適用。SQL historyのversion001～022/success=true、validate成功/pending0、再実行applied0。FlywayのSCHEMA markerはversionなしとして除外し、SQL version期待値はliteral22個。appのschema admission/fullgateは未達 |

環境: Ubuntu26.04 VM/Linux7.0.0-31/JDK25.0.4/PG18.6/Artemis2.56.0/Flyway13.4.0/JDBC42.7.13。Caddyはapt resolute/universe2.6.2-14（runtime2.6.2）導入しdefault service停止、Production TLS/proxyは未配備。Artemis配布tar SHA256 df469079b6388c8c6276197388a0f5ee0d64d0ca42d7f0e2ca5e392e21b955de、既存421の配布をVM /opt/apache-artemis-2.56.0へ展開、instanceはSS343固定 /var/lib/schubert-nk/artemis/schubert-artemis0700。VM-only transient artemis.serviceで起動、正式hardening Unit受入ではない。

再現はtools/quality/vm/ProvisionBroker.java（CLI APIにrandom passwordをmemoryで供給しargv/stdoutへ出さない、Artemis hashprocessorでuser store）とNativeBrokerProbe、ProvisionDatabase.java、045 SQL。正式releaseコードではなく独立工具。systemd-run root probeはProtectSystem=strict/NoNewPrivileges/ProtectHome/PrivateTmp下で実行。5個app credential sourceはGit外root600、Ops/maintenance/migrationもroot私有でserviceへ増配しない。

失敗試行: CLI password Consoleのないstdin起動はthird-party NPEで未配備、CLI APIへ切替。最初の工具default /var/lib/artemis instanceは起動せず保存し、SS固定pathへ新規配備。初回Flyway toolのannotations未配布でClassNotFound、2.21追加後SQL適用成功だがSCHEMA markerを含むcount23の工具assertは不合格。marker/22SQLを独立DB historyで照合した再試験だけPASS。既存承認済Production違反ではなく初期未認定工具試行として保存する。raw journal/Invocation/password/SQL結果の業務row/DB dump/VMはGit外、hash/counter/公開合成結果だけ保存。

Native classesは各source ABIから選択反映したtest-only payloadで全release同一性を保証しない。正式run24/source858713c0b/1964PT/53scope、中心48.3%不変。次はcurrent root/A/permit→RootServiceLauncher→child admission→実業務runtimeを接続する。
