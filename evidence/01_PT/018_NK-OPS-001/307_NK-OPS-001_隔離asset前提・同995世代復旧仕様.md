# 307 隔離asset前提・同995世代復旧仕様

Program NK-OPS-001、SS333343/SSC150160、BUG512/YKT370。工具 `Pg423AssetFixtureRecovery` と独立Test。Source995のProduction期待値/既定59627/移行baselineは変更しない。工具assertはProduction PT分母0、非認定。

| Test ID | 前提・入力・操作 | 独立期待値 | 観点・結果 |
|---|---|---|---|
| FIXTURE1-001 | 捕捉full18/watch/全14列192rowの既定hash、唯一epoch058eaf2b、実M1060939/API1153910の三値/UID/GID/cap | 根拠byteは実操作前のWork私有観測。別世代/null/欠落/別ID/個数は拒否。親30/API50から過去phase/cleanupは推定しない | 正常/異常/null/未知、89工具assert PASS、実復旧v2 exit0 |
| FIXTURE1-002 | same-signed995/BOM/M→全8stop→A→専用DB/advisory、原本graph/INVALID/全kernel/旧PID不存在、private byte force/sync/readback | 当該既存2intentだけtyped退役、全192row/Backup/歴史permit等不変、原本DONE/許可発行なし | 実独立SQL/private物理証跡・並行lock、実v2 exit0、全192/Backup不変 |
| FIXTURE1-003 | 空asset root data975:read982/750、旧API設定SHA55fbc411…/0:986/640、mandatory manifest不存在 | 正常API準備の必要前提が欠落。既存asset/config漂移は修復せず拒否 | 実loader既定59627拒否は事前条件の確認、元API最終phase断定に使わない |
| FIXTURE1-004 | 48byteRIFF/WAVE・monoPCM16/8kHz・data4bytes zero。固定hexは工具source。SHAは独立xxd→sha256sumで算出 | `114448ce435018eda5f4a8df39689d79fb4ff3dbfb5cc521002a42e8a6f625bb`、LF manifestの唯一相対path `audio/pgpt-fixture.wav`、期待件数は事前literal1 | 正常/欠落/byte/metadata、工具golden PASS、実配置v2 exit0、同固定SHA/1件。真のmasterではない |
| FIXTURE1-005 | 配置前のAPI私有全byte保存、new-only dir/file・0余分・data:read750/640/link1、明示count1のflat YAML原子的置換 | その他raw YAML全byte/owner/group/mode保持、保持実manifest loader count1、再読SHA/署名/BOM/原本/Backup不変。本番template59627は不変更 | 独立append golden/欠落LF/既存key拒否PASS、実配置v2 exit0、metadata/raw byte読戻し正常 |
| NATIVE421-003 | 前提と復旧後、一度だけ通常外部Morning→正規issuer→Root→同PID/API、本人socket8091 | actual UP＋info5値のliteral一致、全31/Outbox/6consumer、制御TERM/全cleanup/manager/kernel終端。同世代で独立採取。client0/activeは代用不可 | 未実行、正式source/runtime coverage未達 |

工具検証：JDK25.0.4、javac `-Xlint:all -Werror`、既存固定tool/runtime依存classpath、`Pg423AssetFixtureRecoveryTest <pg422-api-watch-budget-private.jsonl>` exit0/89assert。Work `PG379/pg423-tool-compile.log`/`pg423-tool-test.log`、実観測/secret/master/DB実体はGitへ保存しない。次結果で非秘密hash/時刻/command/source/branch/exit/状態をmanifestへ反映する。
