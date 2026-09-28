# 219 NK-OPS-001 Morning backup request root公開・単体テスト仕様書

Program ID NK-OPS-001、PG348。対象`MorningBackupRequestPublication`、関連RD OPS-009/BAK-001、UI251、SS341 §6.2、SS343 §6.15、SSC-092/094/104。PG347でcommit後に作った非秘密requestを固定root tmpfs `/run/schubert-nk/backup-request` の既存700 directoryへ入場し、既存`BackupWorkerRequestFiles.prepare`のnew-only/0600/force/readback契約で公開する。親M/A/原本/専用DB所有とbackup Unit全終端はcallerの前提であり、このclass単独で証明しない。

| Test ID | fixture・入力 | 独立期待値 |
|---|---|---|
| PT-OPS-MBPUB001 | fake root gate/owner、固定request/part | gate→open→gate→prepare→gate→close→gate。raw requestを任意pathへ出さない |
| PT-OPS-MBPUB002 | 最初のroot拒否 | open/publish/close0。固定診断で非成功 |
| PT-OPS-MBPUB003 | open失敗/owner null | prepare0・非成功。callerが所有しなかったものを閉じない |
| PT-OPS-MBPUB004 | prepare失敗、post-gate失敗、close失敗 | ownerは必ずclose試行、成功を返さない。異常時にもnew-only requestを旧fileへ上書きしない |
| PT-OPS-MBPUB005 | 同part再送・既存file | 既存`BackupWorkerRequestFilesTest`のnew-only拒否を併走、publisher自身は再作成/削除で補修しない |
| PT-OPS-MBPUB006 | null request/part/gate/open、割込 | IO前NPEまたは固定拒否。NPEをcatchして正常化しない |

独立期待値はSSの固定path/手書きevent列および既存File PTのinode後条件から作成。production methodを期待値生成に利用しない。実rootのURL/ACL/mount・caller内M/A保持・full backup Unit start/terminalは外部受入で別に確認。coverage除外なし。実行command/環境/commit/結果/4指標/証跡hashは220へ記録する。
