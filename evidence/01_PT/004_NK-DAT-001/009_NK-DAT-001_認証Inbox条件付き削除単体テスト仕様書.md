# NK-DAT-001 認証Inbox条件付き削除単体テスト仕様書

## 1. 対象・独立期待値

V009 `maintenance_delete_auth_inbox`、InboxDeletionBoundaryTest。RD OPS-009/DAT-009/MQ-008、UI212/241/251、SS324 §12.3/331 §3.5/332/341/343、QA-046/UIC-006/SSC-049、PG-D-122、BUG-014/YKT-012。SQL境界試験でありJavaの暗号検査接続を合格としない。

隔離PG18.6、synthetic Inbox/user/backup、テスト専用暗号文byteを使用。条件付きDELETEの同一性hashだけを独立JDK SHA-256で計算する（暗号整合のexpectedは生成しない）。期待行数/SQLSTATE/role/境界時刻はliteral。偽暗号でもSQL単体が認証結果を証明しないことを明記し、Java接続PTで必ず不整合保持を確認する。

## 2. Test ID・matrix（未実施）

| Test ID / method | 目的・入力/操作 | 期待値と根拠 |
|---|---|---|
| PT-DB-INBOX-025 / exactDeleteRollbackAndReplay | 同TXで候補と証跡取得、LGN/LOG・COMPLETED/ERROR、削除・rollback・再実行 | 対象1/他row不変、rollbackで復元、commit後0/再削除false。独立SQL count |
| PT-DB-INBOX-026 / argumentsAndTransactionIdentity | 各NULL、±infinity、transaction非数字/空/長過ぎ、hash0/31/33byte、別TX/stale ID | 22023またはfalse、削除0。commitしてから再利用不可 |
| PT-DB-INBOX-027 / retainedAndMalformedMetadata | expiry cutoff±1µs/等号、completed+168h±1µs、version/route/PROCESSING/非認証/不正ref/欠落snapshot | 正常境界のみ対象、全保護条件で0。DBが拒否する組合せはconstraint拒否を確認 |
| PT-DB-INBOX-028 / ciphertextAndMessageBinding | 異なるMessage、SHA不一致、同TXで暗号文変更、存在しないMessage | false、対象外の行不変。hashはJDK独立計算 |
| PT-DB-INBOX-029 / backupAndLockGate | backup無し/片方/別run/別日、別session advisory競合、解放後再実行 | 55000/55P03、行保持。正規両backupをlockしcommitまで更新不可 |
| PT-DB-INBOX-030 / leastPrivilegeIsUnchanged | function catalog/PUBLIC/app/batch/Web/backup/ops拒否、検査role任意DML拒否 | nk_owner/definer/fixedpath/UTC、EXECUTEだけ許可 |
| PT-DB-INBOX-031 / concurrentRowsCannotChangeDuringValidation | 候補row/auth参照/backupの別TX更新、削除後commit/rollback | 検証～削除～commitまで55P03、commit後解放、参照非更新 |
| PT-DB-INBOX-032 / migrationInventoryAndSqlScope | 新規V001～009、再適用0、同時migration、SQL/crypto責務境界 | 9件/再適用0、旧V001～008差分0、table21維持。偽暗号にSQLだけの合格は付けない |

5つの手続き判定（引数、transaction、advisory、backup、DELETE成否）とDELETEの全AND/OR/NULL条件を上表で検証する。SQLに架空JaCoCo100%を付けない。SQL制約で到達できない不正rowは制約の実拒否を証跡化し、安易な未試験除外にしない。

## 3. 実行と証跡

Java25.0.4/Maven3.9.12/Flyway13.4/JDBC42.7.13、既存421と007の再現環境。探索はAPI module＋DatabaseMigrationTest/InboxInspectionBoundaryTestを併走。正式はroot `./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress clean verify`。
実行日時/branch/source/command/exit/全結果/SQLmatrix/hash/関連BUGは010結果とsanitized manifestへ固定する。失敗・未実行・skip・flakyは合格にしない。正常削除の実装で実データを操作せず、隔離fixtureのみを使用する。
