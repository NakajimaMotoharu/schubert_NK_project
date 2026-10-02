# 308 API固定phase診断・唯一202世代保全仕様

NK-OPS-001、RD SYS002004/OPS009・UI212251253・SS321342343351/SSC161・PG-D336・BUG515。診断はenteredの前境界であり成功receiptでもauthorityでもない。Source995のPG423唯一失敗世代/202全14列を保持する。同owner実ready・Web・native coverage・CHRは未受入。

| Test ID | 入力/操作・fixture | 独立期待値/根拠 | 観点・結果 |
|---|---|---|---|
| MAIN003-STAGE | 既存opsApiMain003の同固定ENV/configと実Descriptor拒否、argv override、fake exception `UNTRUSTED` | stderr全byteは `API startup entered ADMISSION\nAPI process stopped\nAPI process stopped\nAPI process failed\n`。既存3終了literal/50・70/分類不変更、UNTRUSTEDなし。自己Productionでexpectedを生成しない | 正常/異常/null/拒否/redaction、選択v1は旧期待値差1Fで不合格、独立新stage期待値へ更新したv2は36PT（7/9/7/13）/FES0/static4zero。全scopeではない |
| READY004-CLOSED | 同ownerでReady.release callback中に管理server.closeし同portへ再bind | release1、IOException、ready false、再promoteでrelease増加0、同port再bindDOWN503/固定JSON | 実HTTP・境界・資源閉鎖。選択5管理PT PASS、original995 management class byte一致、4coverage missed0 |
| REC995202-001 | 独立captured full18/watch事前pin、Morning1157365/8c042ad2/ticks19753959、API1254139/ab8b4e5b/ticks19822896、epoch2f72c433、署名Source995 | 親30/API50正常退出の唯一世代だけ、欠落/null/未知/別inv/PIDは拒否。Root→同PID普通API/cap0実観測。未知過去phase/closeを成功にしない | 固定22namespace/全14列202row、独立工具negative/actual watch、86工具assert/current-pin actual watch正常 |
| REC995202-002 | M→全8stop→A→全kernel/manager二読/旧PID不存在/同boot/元run/activation/INVALID/専用DB+advisory、captured fullbyte private force/sync/readback | typed既存2intentだけ退役、旧permit/owner/launch/全202row/Backup/Asset全5metadata+SHA/private API/common byte不変。新permit/原本DONE/成功codeなし | 並行/資源所有/境界/保持、実Recovery exit0、202/Backup/Asset/config不変、safe PG424-signed-diagnostic参照。工具assert Production PT分母0 |
| NATIVEPHASE-001 | Source固定全6回帰→新pin署名/全BOM/trusted通常候補配備→一度のみ外部Morning→同PID普通API | closed14stage literalだけ、最後enteredから成功/最後phase完了を断定しない。actual UPは本人socket/同世代info/全31/resource/Ready.releaseの別事実を必要とする | 未実行。credential/password/token/session/path/DB/例外messageをログ/Gitへ出さない |

工具実行はJDK25.0.4 `javac -Xlint:all -Werror`、既存fixed tool/application/vendor classpath。Root-private capture/runと原本全byteはWork/VM私有だけ。正常exit0でもProduction gate/正式4coverage全scopeに算入しない。実source/command/時刻/exit/hashはsafe manifestへ保存する。
