# NK-DAT-001 共通cleanup安全境界単体テスト仕様書

2026-09-09 V016回帰追補（SSC-049/PG-D-141、BUG-127/129・YKT-102）: 現在の独立catalog期待値はversion付きmigration001～016の16件、業務/technical計23table・PK23/FK23/UK constraint30/CHECK154/constraint trigger1。QWK partial unique indexはconstraint数へ混同せず045/PT192で別照合する。後述の初回V005～015等の値は当時の履歴であり、現在の回帰期待値には使わない。全31route・更新3成功のQUESTION/JOB、ERROR/NONE、168hと6種参照matrixは045/PT177～192および015/PT051～056へ追跡。各Programの実行結果・manifestにある正式sourceを正とし、未実行を合格へ含めない。

Program NK-DAT-001、CleanupSafetyBoundaryTest各method/V013、RD DAT-009/OPS-009、UI251 §6、SS331 §3.3.1/332 §11/341 §7、SSC-050、PG-D-129、BUG-092/093、YKT-083/084/012。

## 1. 独立fixture・期待値

実PostgreSQL18/Flyway/JDBCの隔離DB。run=public UUID、開始2026-09-17T00:00:00Z、JST日2026-09-17。90日前=2026-06-19T00:00:00Z、400日前=2025-08-13T00:00:00Z。日時は独立calendar確認とliteralで固定、production計算をexpectedに使わない。backup2行の同run/当日/終了SUCCESSを正常fixtureとする。正常/境界/異常/null/例外/並行/再実行を次表へ対応させる。

| Test ID | Method・目的/操作 | 独立期待値 |
|---|---|---|
| PT-DB-INBOX-089 | backupMatrixAndLegacyCounterexample: 全7関数×backup状態/日/run/終了/欠落、旧V006再現 | 正常OK、不正BACKUP_GATE/0変更。旧5では前日SUCCESSを許す反例を隔離TXで検出、rollbackで現行DDL復元 |
| PT-DB-INBOX-090 | backupLocksAndSnapshotRace: 別connectionのadvisory、backup NOWAIT、更新中状態交替 | LOCK_BUSY/0、検査中backup更新55P03。競合後の実snapshotが不成立ならBACKUP_GATE。成功flagを再読してすり抜けない |
| PT-DB-INBOX-091 | invalidInputsAndTimezone: NULL/±infinity/limit0・max+1/int端/異なるsession zone | 22023/0変更、UTC固定で同じ閾値・当日判定。limit1/maxを許可 |
| PT-DB-INBOX-092 | rolesInventoryAndImmutableHistory: 実role/owner/PUBLIC/config/13履歴/旧hash | batchのみ7 EXECUTE、他role42501、固定UTC exact、余分設定/UTC変更negative、再適用0、V001～012不変 |
| PT-DB-INBOX-093 | rollbackAndRowLocks: 実chunk rollback、candidate SKIP LOCKED、delete trigger failure | 全更新rollback、lock中row保持/解除後削除、SQL障害をOKへ変換しない |
| PT-DB-INBOX-094 | businessAndSessionBoundaries: 通知5状態24h/cancel・question FK・3 session期限/共有limit | SS332 literal候補だけ削除、関連notification存続/active保持、transaction復元と再実行0 |
| PT-DB-INBOX-095 | logRetentionAndHold: 90日±1μs/同値/未来、holdNULL/±1μs/同値、limit/lock/rollback、旧V006 | 90日超かつholdなし/期限到達だけ削除。保護件数をskipへ。旧run anchor誤用の最近log削除反例を検出 |
| PT-DB-INBOX-096 | batchCompletionRetention: 完了400日±1μs/同値/NULL、開始古い終了最近、同run/RUNNING/FAILED調査、順序/limit/rollback | ended_atが400日超の完了・非調査runのみ削除。現在/調査中全row保持。旧started_at基準の誤削除反例検出 |

SQL例外fixtureはSAVEPOINTで隔離可能だが、本番の暗号検査transaction証明へ流用しない。row lock/並行はlatch・実pg_stat_activity観測で同期しsleepに依存しない。実credential/secret/wire/dumpは保存しない。

## 2. 実行・gate

探索: JDK25/Maven固定toolchainでAPI moduleと依存module、当class/DatabaseMigrationTest/全旧SQL境界を実行。正式: work/pgpt_foundation_verify.shのclean verify、8collectorと新cleanup-safetyを含む19scope、hash/trace/負canary/秘密scan/Current baseline不変。Test IDごとの結果とSQL後条件は026とmanifestへ記録する。Java全module line/method/class/branch100%、NullAway/Spotless/SpotBugsを維持し、SQLはこの条件matrixで確認する。失敗/skip/未実施を成功に含めない。

対象source/日時/OS/tool/command/終了code/coverage/BUG/SSC/証跡path/hashは026とevidence/cleanup-safety/manifest.jsonに実行後確定する。親process/実backup gate/OS lock/全域完了はこの仕様の合格範囲外。
