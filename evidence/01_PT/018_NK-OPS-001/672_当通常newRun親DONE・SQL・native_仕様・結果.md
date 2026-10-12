# 当通常newRun親DONE・SQL・native 仕様・結果（暫定）

Program NK-OPS-001/MorningProcessMain、SS341/343/353・QA047/048/050・451、Production `4d6bcbddb417b76d27e52d5d9640752c300edccf`。Java25.0.4/PG18.6/Artemis2.56、guest boot3d69、隔離LAN VM/current PG1544。IT/STではない。

| Test ID | 独立期待値・操作 | 現結果 |
|---|---|---|
| PT-DEP-1601001 | 外部noargs一回でProduction生成run、独立PID1全journal field＋原本DONE/anchor/begin、元1800s以内・outcome0、GC zero単独不可 | actual0、1586.458658s、DONE06:48:58.973359Z |
| PT-DEP-1603001 | 新runを旧same-run十SKIP oracleで検査 | 不合格actual1、BUG1134、旧slot保全・合格加算0 |
| PT-DEP-1606001 | 正規Backup2SUCCESS＋八SKIP、HTTPの上限を親DONEとして検査 | 不合格actual1、BUG1135、旧slot保全・合格加算0 |
| PT-DEP-1608001 | SS341/DDL独立二BackupSUCCESS/八同日SKIP、旧24table row保持、全handle/day/run/attempt/zero/error、HTTP/Log/session匿名/暗号shape・SENT一対一。batch<=DONE、live HTTP<=固定独立UTC観測 | actual0、二SUCCESS/八SKIP、匿名HTTPLog222/OutboxSENT222/Session222 |
| PT-DEP-1609001 | 当四Unit PID/INV/ticks/argv/世代、全field・foreign/null拒否、固定八停止順/一回予約、元全seal/constructor/Ref-MA-RODB-advisoryを独立検査 | 工具独立2test成功、実compile/stop/post/native未実行 |

1601 command `PYTHONPATH=tools/quality:tools/quality/vm/050_s1 python3 -B tools/quality/pg1601_current_newrun_done_receipt.py`、operator d9f023002、終了0、script687ca389…/DONE SHAfca6916d04d5e37745841609bb0bd2b659fa4440a0a6b01925bc205adb85d957。watch1597 terminal0、API/Web同Root-parent-info/socket/CaddyTLS200、親backend保持。Root INV e4d891…/Job71184/start38365395523/end39951854181。

1608 command同prefix `pg1608_current_observation_full_seal_v3.py`、operator d634b1ed0、終了0、payloadbbc23b1bb296e64091a6fe74ae6d5c18a4e5137c3a5ab78f05951d42fc1fc3b5、private fullseal SHAa600bb706bbd48168cd59b7028ec39b1f16464620d7fe26c4680e8dc136d5e27。独立固定観測UTC07:58:44.700095、全三読/32field/187signedartifact/四actor正常metadataRef。証跡安全manifestは `/home/mini/codex/project1/work/pgpt-runs/PG379/pg1608-current-observation-full-seal-v3/manifest.safe.json`。raw DB/session/token/credential/Backup本体は私有、Git格納0。

新1605/1607の独立手書fixtureはBackupがSKIP、CleanupがSUCCESS、別run/day/attempt/count/error、batchがDONE後、HTTPが観測後、null/逆順日時を拒否。実生成payload static0、親工具static0。旧1602/1603/1606結果は現在正本資格に使用しない。Backup manifest/実archivehash/完全DB二handle/retention旧一世代5entry私有原byte保全は別pending、旧削除を保全済と推定しない。

当source native counterはまだ未取得。前resume八streamの残1184/219/11/767を当newRun測定へ流用しない。Java四100/global451/CHR/QA051final/trace/正式は未閉鎖、正式PT-WEB-20260925-24/1964PT/53scope・全leaf増分0。
