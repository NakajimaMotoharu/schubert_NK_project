# NK-DAT-001 backup再実行・成功制約 単体テスト仕様書

RD BAK/OPS-009/DAT-009、UI251 §11、SS331 §8.2/341 §11、SSC-054/BUG-138/YKT-108/PG-D-145。V017 index predicateの部分PT。BatchRunRepository/main/実backup作成・最新artifact照合は未実装。

## 1. 期待値・fixture

BackupRerunBoundaryTest、隔離PG18.6へ正式Flywayを適用。公開run/date/step/count fixtureのみ。UI251のbackup再実行規則から、2 backup stepは同日別attemptのSUCCESSを保存可能。通常step同日SUCCESSは1件、同日step attempt重複は全stepで拒否、1～99以外拒否。旧V004成功indexをrollback-only transactionへ復元し2回目23505を再現する。Production methodでexpectedを生成せず、履歴/件数/status/SQLSTATE/catalog/権限を独立assertする。

## 2. Test IDと操作・期待結果

| Test ID | Method | 入力・操作・独立期待値 |
|---|---|---|
| PT-DB-INBOX-233 | sameDayBackupReruns | 同日2 backup step、attempt1/2、同run/別run。各SUCCESSを保持し2回目も保存、既存行更新なし |
| PT-DB-INBOX-234 | ordinarySuccessStillUnique | 通常step一覧/類似名の別attempt SUCCESSは同日23505。WARNING/FAILED/SKIPPED/RUNNINGは成功UK対象外 |
| PT-DB-INBOX-235 | attemptAndDateBoundaries | attempt1/99許可、0/100は23514、同日重複23505、別日同attempt許可、必須NULLは23502 |
| PT-DB-INBOX-236 | failureAndLatestSuccessHistory | 複数成功後に新attempt失敗。旧成功は全て残り、終了時刻/id順の最新成功を独立SQLで判別。実artifact選択の合格ではない |
| PT-DB-INBOX-237 | transactionRollbackAndMigration | 旧V004 indexを一時復元すると2回目23505、新は保存。rollbackで行/index元へ戻る。旧migration hash不変、Flyway validate |
| PT-DB-INBOX-238 | concurrentSuccessAndAttemptConflicts | 独立session同時16backupは別attemptで全保存。同attempt/通常成功2件競合は各1成功/1拒否 |
| PT-DB-INBOX-239 | cleanupGatesWithRepeatedBackups | 同run複数成功でも8 cleanup/Inbox gateは同run/当日/両step/終了を検査。欠落/別runは拒否、既存snapshot/lock回帰維持 |
| PT-DB-INBOX-240 | catalogAndPrivileges | backup例外以外のindex/UK/check/所有者/権限不変、migration最新版17、通常成功UK維持 |

## 3. 実行・coverage・証跡

Java test8件。DDLはJaCoCo分母ではなく、predicate両backup/通常/非SUCCESS/NULL・境界・並行をSQL後条件で網羅する。6 Java moduleの4coverage100%は別gateで維持。正式run/source/日時/tool/command・exit/各ID/coverage/sanitized evidence・manifest/hashを054へ記録。failed/flaky/skipped/not-runを合格に含めない。正式39とは別source/run40以降で実施。
