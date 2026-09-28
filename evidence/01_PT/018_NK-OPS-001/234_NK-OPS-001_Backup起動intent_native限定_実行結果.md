# 234 NK-OPS-001 Backup起動intent native限定PT結果（PG356）

状態: PT-OPS-BFNATIVE001/002は隔離VMの固定tmpfs rootで2回実測しPASS。真正Morning親M/A、Backup Unit起動、実Backup、R2/R3、全coverage100%の受入ではない。仕様・独立期待は[233](233_NK-OPS-001_Backup起動intent_native限定_単体テスト仕様書.md)。関連RD OPS-009/BAK-001、UI251、SS341§5-6/343§6.15、SSC-105/106、BUG-315/YKT-248。

2026-09-28 20:34～20:40 JST、`dev-foundation`、Production source `4005d6704fac645267aedcce53c2a413f9eae95a`、probe/spec `368d8712c5c1c1be233e8fc44aa91ea83ff2fca4`。Ubuntu VM kernel `7.0.0-31-generic`/x86_64、JDK25.0.4、JaCoCo0.8.15、instance-id固定`pgpt-r2-20260927-01`。PGPT-only probeはProduction JARに入れず、同byte Batch classを別classpathから呼んだ。probeを`--release 25 -Xlint:all -Werror`でcompileして配備し、最初は通常のroot Java実行、次にJaCoCo agentを付けて同じ試験を再実行した。いずれもexit0、出力は固定状態語`INTENT_CREATED_RESIDUAL_REJECTED_RETIRED`のみ。2回目はnative coverage採取のためであり、成功件数を重複して加算しない。

実行前後に`/run/schubert-nk/backup-request`はroot:root/0700のdirectory・内容空を確認。probeが空root0600の固定markerをCREATE_NEWし、残留時の`requireClear`を拒否し、同じ保持root/tokenでretire後に再admission可能な空directoryへ戻した。Morning/Backup両Unitは前後ともinactive/PID0で、既存PG323/PG309 test-only Unit、DB/原本/current/credentialは変更していない。終了時markerなし。生token・session・credentialはGit証跡に保存していない。

HostのPG355 clean Production6 `2440PT/357suite/F/E/S0/静的0`のBatch JaCoCo execとVM native execを暫定mergeし、同一Batch classからreport生成。`BackupStartIntentFiles` missed branch/line/method/class はhost `6/16/4/0`→merge `6/14/3/0`。Native file IOの一部だけが新規実測で、branch6/line14/method3は未網羅。全Module coverage gateは未達のまま。Maven `jacoco:report`が指定出力先を採用せずhost XMLを一時的に再生成したため、事前退避したhost XMLを直ちに復元しSHA一致確認した。merge exec/XMLはGit外privateに保存し、Gitにはhash・sanitized結果のみ置く。PG355正式認定を再計算しない。

Raw evidence hashes SHA-256: Batch JAR `72613cc1d0a67be7c12646c88ee4e904e83981b0fecf7af962882371708b7114`、VM probe class `44028af57c0e3d74c936761b43e5980d680bd67466bc50f3d40747ab6cdf76dd`、native exec `22b008f0d71a9e93420ab15fc754a55ab9c0565ca1a9f13f01471ced0845d95d`、merged exec `ac7e7b9758ecce59b1a7119e652c093495c81336376bf285af8e425fac298cd4`、merged XML `ffd0f8689f95ae7198e30e6ba45015731defeec6baa6120e07b5715550e22fb2`、復元host XML `42cc11cfc54a238772bb0445f69b66240342c694e86b1addabcf31350fafce4c`。Git外場所は`/home/mini/codex/project1/work/pgpt-vm/private/PG356/`、Git内sanitized manifestは`evidence/provisional/PG356-backup-intent-native/manifest.json`。

未解決: Production `BackupUnitStartClient.create`はmarker owner/tokenを`intent.begin()`後にclose/discardしており、通常のfresh receipt・明示stop・全Unit終端後に同tokenでretireする親結線が存在しない。未知送達/親hard-timeout中のM/A・原本保持も未証明。SSC-106/BUG-315/YKT-248を閉じず、R1下位だけ前進、正式source/run・全体中心48.3%は据置。
