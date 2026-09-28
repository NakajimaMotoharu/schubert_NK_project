# 223 NK-OPS-001 Morning backup request native限定・単体テスト仕様書

Program ID NK-OPS-001、PG350。対象`MorningBackupRequestPublication.openNative`と既存`BackupWorkerRequestFiles`、PGPT専用`NativeMorningBackupRequestProbe`。関連RD OPS-009/BAK-001、UI251、SS341 §6.2、SS343 §6.15、SSC-092/094/104。隔離Linux VMの実root tmpfs、固定`/run/schubert-nk/backup-request`で失敗閉鎖とnew-only/読戻し/retireを確認する。既存Morning PG323 test-only Unit、保留run/current、backup Unit、credentialは変更しない。

| Test ID | 事前条件・入力・操作 | 独立期待値 |
|---|---|---|
| PT-OPS-MBNATIVE001 | 固定directory不存在、root probeのmissing mode | `openNative`拒否、公開0。pathを自動修復しない。SS343 §6.15 |
| PT-OPS-MBNATIVE002 | `/run` tmpfs、親`/run/schubert-nk` root0755 ACLなし、固定childをroot0700新規作成、present mode | root600 requestをnew-only公開→同byte読戻し→元identity retire。probeは完了codeだけ表示しraw run/credentialを出さない。SS341 §6.2 |
| PT-OPS-MBNATIVE003 | 同part/旧requestの再送 | 既存`BackupWorkerRequestFilesTest`の上書き拒否を併走。native probeの成功から実parent/worker成功を推定しない |

固定requestは非秘密の手書きUUID/時刻vector。OS/JDK、branch/commit、固定probe command/exit、前後directory metadata/ACL、request消去後条件、関連BUG/SSC、sanitized log/hashを224へ記録する。実Unit actor認証/M/A/DB/保留run・backup現物/cleanup/permitはこの限定probeの対象外で、全体正式PT/coverage100%への算入は禁止。
