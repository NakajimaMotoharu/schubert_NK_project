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

## 当owned停止・native実結果追記（2026-10-12 17時台JST）

上段「native未取得」は初回保存時の履歴。1610 operator992fa84b6 Werror/constructor全4phase0、1612別fullseal0/SHAa600同値、1611 immutable stage0→当四explicit正常stop/完了oneshot含む八receipt・全scope正常actual0（08:05:55.591913→08:07:27.351883UTC、91.759970s）。log SHA00c13146499c745a0d8cf5593e4ad09216b8511321141644e9b90a1542444f4a。元Root/DONEを保持し、API/Web TERM143と元Root成功0を混同しない。

1613 operator131eb9df0、独立全postactual0（08:08:23.099849→08:08:29.605003UTC）、24DB三読/全32/187署名/原本Backup/startup/runtime/全十kernel空/actor消失/client-advisory-flock0/newmetadata正常、native physical14。safe path `/home/mini/codex/project1/work/pgpt-runs/PG379/pg1613-current-ordinary-terminal-post-v1.safe.json`。

1614旧catalogはsize-vs当bytes schemaでactual1（BUG1136/YKT904）、旧payload/slotを保全。1616新strict schema/原十native byte照合/static0/当BackupPID1 generation・八stream qualification0、旧API/Web四stream＋旧Inspector二streamは保全・当結果へ非採用。1617analysisは複数server.info区画parserで認証前拒否（BUG1137/YKT905）、新ee32080af/9独立test/static0/1618新slot実LAN分析0。

1618同source host1532のexec/XML/JAR hashを再利用、current native8各single-session/時刻/CRC0・独立XML counter一致。server manifest63a6d3e05dda3d537187a5cf6f4050893118800cfd07b0ccb7c1fbd1b4271a12。host/native union追加L2866/M452/C28/B370、残L918/M178/C12/B716。module残はprotocol/storage/web各0、api46/2/0/1、bootstrap4/3/0/0、batch868/173/12/715。coverage100false/global未合格、前resume結果との単純gain加算0。旧Source769native/Current baseline変更0。

新macro Test PT-DEP-1613001（全後条件）、PT-DEP-1616001（strict archive/Backup PID1/window/旧世代保全）、PT-DEP-1618001（同source/sessionCRC/XML/全counter）。実commandは同prefix＋pyflakes runtimeで各該当pyを一回実行、全終了0。host manifestは `/home/mini/codex/project1/work/pgpt-runs/PG379/pg1618-current-ordinary-native-qualified-v3/manifest.safe.json`。原ログ/全private native/DB/Backupは非公開、秘密値保存0。Bootstrap/Inspector/故障枝/Backupmanifest-retention/CHR/正式451未完は継続する。

## Backup・正規retention原byte保全追記（2026-10-12 17時台JST）

PT-DEP-1621001：SS341固定3archive/独立canonicalmanifest/2完全14列DBhandle/countbyte、固定8configtar/host exactbyte/所有、署名default59627とSSC150160承認fixture Asset件数1の唯一override、公開recipient fingerprint、ordinary `pg_restore --list`終了0。1621 actual0/operator8068c783c/payload ea509c97ee747c00e6580809bd1f7f9fdb9f558bdffea5d5231da22916e19dba、manifest0780ac111bdf1c5db1e9b07014424c745f2855ba07a7fd4b976b08222ce57b85、dump17,838,358/config20,480/暗号credential41,160B・合計17,899,998B。list SHA6ec9644480e964302152f988996ba046c606338677aa25a840523bd6949dc880。fresh十Ref全post/原値正常。1620独立negative1test/生成static0、旧1619不合格はBUG1138/YKT906として保持。

PT-DEP-1623001：正常当1596/1613全postに束縛した唯一五entry退役/当五entry追加/他旧Backup不変と七世代を独立検証。固定dissect6package（既導入版を約1MB専用runtimeへ再利用、global変更0）、認定済standaloneLAN QCOWをrb/hash/identity/原inode・uid/gid/mode/nlink/size/mtime/ctime・全四filehashで照合し、旧四file13,740,808Bをserver専用privateへ保全。七manifestの開始時刻から最古退役を独立照合、activeQCOW・RAM・DB・現Backup変異0。1623actual0/operator d16bbc7c9、scriptdac0a3ab7c7e2dd2ecb1526a13f9ea255fb0cf9dc26d5bca582bed10eff0e495、private manifestb80b8187776eb8b1efc3329ba9298b7c8956088ca269cdb706a26dc87d98b7ad。独立retentionreplacement/unknown/null/他entry/root変異1test/全生成static0、旧1622copy発行前TypeError/空servernamespaceはBUG1139/YKT907で保持・再利用0。

再現commandは同prefix/pyflakes runtimeで `pg1621_current_ordinary_backup_qualification_v2.py`、`pg1623_retired_backup_readonly_preservation_v2.py`、各一回・終了0。安全manifestは `/home/mini/codex/project1/work/pgpt-runs/PG379/pg1621-current-ordinary-backup-qualified-v2/manifest.safe.json` と `/home/mini/codex/project1/work/pgpt-runs/PG379/pg1623-retired-backup-readonly-v2/manifest.safe.json`。raw旧Backup四fileは `/home/mini/schubert-nk-pgpt/runs/PG1623-retired-backup-v2/bundle/`（LAN server private）、Git/通常ログに実体格納0、private復旧/署名key・server.info移送0。

BUG1134/YKT902の通常newrun Backup SQL・実体・retention保全横展開は限定範囲完了。上段pendingはその時点の履歴。全PGPT/全native/Backup restore実行/IT-STは未受入として維持し、後続へ継続する。
