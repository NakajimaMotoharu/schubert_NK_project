# 680 NK-OPS-001 生成済みBackup原本・七世代保持（限定PT）

WBS-N02（主）、P017-03/04/06（参照費0）、SS341/312/351/353、QA047。Production2741/PG1638、普通親run02e941b9・679真正DONE/正常owned停止/全資源後条件を前提とする。旧4d6の1621/1623はreader論理の参照だけで成功結果を流用しない。新Backup・退役・DB復元・VM起動・稼働diskコピーは発行0。

| Test ID | 独立期待値と入力・操作 | 結果 |
|---|---|---|
| PT-OPS-BACKUP-1711-001 | 当runのBackup MANIFESTと三archive実byte/hash、二DB handle14column・件数/byte、8設定のallowlist・所有mode/署名template・既承認api fixture1だけの差、public recipient、pg_restore --list。全24/32/187・原本/native/資源0を新十Ref内で再照合 | actual0、三archive18,583,623B（dump18,521,983/config20,480/encryptedcredentials41,160）、設定総byte61,640、2handle、8allowlist、list exit0。manifestSHA6b74fdcee…、listSHA6a247674… |
| PT-OPS-RETENTION-1712-001 | 当起動beforeef9d→正常post after3d5cから、完成7→7、追加一世代/退役最古一世代・四file、残全entry原metadata/hash不変を独立選定。certified standalone pg1431/guest.qcow2をrbだけで読む。旧inode/owner/mode/nlink/size/timestamp/xattrと全bytehashを一致させ、現七startedAtより旧が最小と検証、base前後同identity/hash | actual0、退役四原本14,237,699B私有保全。exact旧inode/byte一致、base不変、七世代/最古順確認。private manifestSHA0c6a426f503697c4787da019e71d2d8f17611c30d28d609ff794cee749f23fd3 |

実行Source1711=7388e64f7、1712=9e1ae1bd5。固定JDK25.0.4/PG18.6、guest3d69及び専用LAN rb保存点、dissect固定runtimeの全相対hash、OS/byte/所有sourceは各対応manifest/payload/sourceを参照。commands=`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<fixed pyflakes runtime> python3 -B tools/quality/pg1711_new_source_backup_readonly.py`／`pg1712_new_source_retired_backup_preservation.py`。工具unittest：1711独立config/null/未知/変異拒否、1712 exact七→七/余剰/欠落/保持行差拒否が成功、生成全Python静的0。これらはProduction coverageへ加算しない。

実証：Source=同2741、全二readeractual0、dump-listは一覧のみでrestore0、rawBackupはguest/LAN privateだけ、server.info/host秘密keyの複製0、currentVM/DB/Backupへの変異0。新Native counter904/171/9/716は679実測を維持し、当読取でcoverage改善や正式受入を計上しない。PGPT/ITST完了、故障/競合/失敗/skip全matrix、正式451は別未完。

私有証跡：WorkPG379/pg1711-new-source-backup-readonly-v1及びpg1712-new-source-retired-backup-v1、LAN `/home/mini/schubert-nk-pgpt/runs/PG1712-retired-backup-v1`（raw原本・manifestのみ私有、Git格納0）。公開[680_manifest.json](evidence/output/680_manifest.json)は三actual recordのpath/hash・safe件数だけ、SHA256621268f32c2967d7ded47b42feed6fc47232c786a8bfcb736bf54c0aec61d489。状態=当生成済みBackup byte・保持限定確認済、formalAccepted=false/wholeleafdelta0。
