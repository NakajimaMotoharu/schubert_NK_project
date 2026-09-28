# 233 NK-OPS-001 Backup起動intent native限定PT仕様（PG356）

Program ID NK-OPS-001。対象は `BackupStartIntentFiles.requireClear/begin/retire` とPGPT専用 `NativeBackupStartIntentProbe`。関連RD OPS-009/BAK-001、UI251、SS341§5-6、SS343§6.15、SSC-105/106、BUG-315/YKT-248。真正Morning UnitのM/A・原本/DB・Backup Unit startには触れない。

| Test ID | 事前条件・入力/操作 | SSから独立に定める期待値 |
|---|---|---|
| PT-OPS-BFNATIVE001 | 隔離VM instance-id固定、実効UID0、`/run/schubert-nk/backup-request`既存root0700/tmpfs・内容空を先に読取確認。Production同byte classとPGPT専用probeを別classpathで実行 | 固定`backup-start.intent`空root0600 regular/link1/ACLなしを新規作成し、同bootの二度目`requireClear`は拒否。Probeの期待はSS343の固定名/属性でありProduction method出力をexpected生成へ使わない |
| PT-OPS-BFNATIVE002 | BFNATIVE001の同process・同retained directory内でtoken retire→再admission | 同一markerだけがunlink/dir forceされ、fixed directoryは再び空。実Backup Unitと既存Morning Unit、保留run/current/credential/DBは不変更 |

失敗時のmarkerは自動削除せず、安全停止とし、手動で別理由へ書き換えない。VM既存PG323 Morning test-only override・PG309 Backup計測overrideの上書き/起動はしない。日時、JDK/OS、branch/source/probe hash、実command/exit、前後root metadata、結果、coverageと限界、sanitized log/hashを234に記録する。Probe実行はProduction native classのfile IO限定実測であり、actor認証/親継続M/A/Unit receipt/backup artifact/30分・再boot、全4指標100%や正式R2/R3へ算入しない。
