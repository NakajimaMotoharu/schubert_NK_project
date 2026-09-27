# PG311 root morning DB session PT（暫定）

Program NK-BAT-001/NK-OPS-001 / MorningDatabaseSession.execute・Session.requireUnused/beginBackup。RD DAT009/OPS009/BAK/BKO、UI251、SS341/3436.15、SSC094。固定loopback/schubert_nk・effective/login schubert_batch・非recovery/RW/ReadCommitted/session71419602。M/原本/A/child/schema/releaseBOMは別Assembly必須であり本成功で省略しない。

| Test ID | 入力・操作/fixture | 独立期待値・根拠 |
|---|---|---|
| PT-OPS-MDB001 | URL/port/db/query変更、null全port/credential/operation/record、誤root主体 | literal allowlist以外接続0、password owner必ず消去、root自己gate必須 |
| MDB002 | role/lock固定行、requireUnused、callback終了後Session使用、null callback値 | literal user/db/props照合、全close、終了後JDBC0/非成功 |
| MDB003 | 両role/DB/recovery/null/row0/2、autocommit/readonly/isolation、lock/held false、nullconn/stmt/row | 不明を補完しない、callback0、資源漏れ0 |
| MDB004 | 全実到達pointへSQL/IO/runtime/Error、既存run参照あり | fixed既知診断/未知identity、全close、原本不存在確認不可 |
| MDB005 | unknown body＋row/stmt/conn close compounds、null各Session引数、backup query失敗 | 未知primary維持・固定secondary、SQLprimary＋unknown closeはunknown、begin失敗でhandleなし |
| MDB006 | 開始前/途中割込、別threadのSession使用 | 割込保持・開始JDBC0/他threadJDBC0 |
| MDB007 | isolated PG18＋Production migration、fixedrole/DB、両begin | SQL後条件literal `BACKUP_CONFIG:RUNNING:1,BACKUP_DB:RUNNING:1`、同run・異ID・commit後他接続で2row可視 |
| MDB008 | 実connection commit前失敗/commit直後成功不明 | handle返却0、connection閉鎖、独立DB後条件0/2rowを確認、不明commitを成功にしない |

synthetic Gateはroot admission実証ではない。actual role/transactionは隔離DB、trustworthy root/LoadCredentialは隔離VM限定接続へ追加する。coverage4指標100%と独立expected/全資源contractを要求、未達を除外しない。実行/環境/対象source/hash/coverage/BUGは146/manifestへ後記。schema/BOM/global morning未達、本PTはformalrun/R2/R3認定ではない。
