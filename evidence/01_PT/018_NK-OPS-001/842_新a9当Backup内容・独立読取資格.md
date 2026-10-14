# 新a9当Backup内容・独立読取資格

PT-OPS-2910-001、SS331/341/343/355・451/487、WBS-N09。2026-10-15JST、sourcea9/PG2802/BOM37bf/newboot79a/run0dcは839～841同値。9e79602c8の工具純二試験（完成graph/新run/cutoff/config・欠落oracle/空seals拒否）PASS。

`python3 -B tools/quality/pg2910_network_current_backup_content.py`（PYTHONPATH838同値）、session88121 actual0、20:45:05.950088Z～20:45:15.384969Z。正規停止後、署名187/全24二読/全十Unit空・全actor/client-advisory-flock0/native10安定を再認証し、原Backupを読取だけで独立確認。Backup/Root/restore/prune/reload/DB write再発行0。

独立canonical manifest・三archive hash・二つのcomplete DB handleと件数/byteを照合。設定61640byte、全archive15829723byte、固定config allowlist8・public recipient fingerprint正常。通常pg_restore list終了0、dumpList SHA256 d39c65ee4d9ce5b0473f0d17af747b1704c17de66d6e1be1c56a3a4cfa9da331。

| 原archive | byte | SHA256 |
|---|---:|---|
| schubert_nk.dump | 15768083 | 56e044337c0ffd6ecd3f1267c0c266a116f992b1f65ff9865b638b537076cf16 |
| config.tar | 20480 | 801e21d16624a481a6d8cc9c2d662282abd946c84b62a5a188123fc3f63bf0a4 |
| credentials.tar.age | 41160 | f72bf4d5e1e0cb87ad6c9839cba45577b81c752a6d3a018e6c5ab40254cd370c |

WorkPG379 `pg2910-network-current-backup-content-v1/manifest.safe.json`/payload7a81ac94294a1a7864dd9882a8d36de4c6945e09ea79f9f3a0b5b56f7147fd3c、command/source/OS/JDK/時刻/退出条件/入力結果hash保存。manifest ad82b1ce79baa959d7a3f27d5c34baf1cb9cff59e273ea1799a2d2153b2560d0。raw DB/credential/key/archive内容はGit保存0。restorePruneAccepted=false/全体scope正式false、元成功Backupの再発行不要。正式1964/53・受入leaf差0/effortnull。
