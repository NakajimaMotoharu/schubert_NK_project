# NK-DAT-001 Expiry batch監査DDL 単体テスト仕様書

2026-09-24作成。PG245/SSC-077/BUG-237/YKT-188。対象は`V021__expiry_batch_run_audit.sql`、`MigrationInventory`、`DatabaseMigrationTest.expiryBatchRunAuditIsCompleteAndOtherStepsRemainUnchanged`/`legacySuccessfulExpiryAuditIsNotGuessedOrPartiallyMigrated`。RD OPS-009/MQ-009、UI251 §8/11、SS331 §8.2・341 §9・343 §9へ追跡する。PG244のbroker側削除、後続の親transaction/再実行永続記録は本DDL単位の合格に含めない。

| Test ID | 事前条件・fixture / 入力・操作 | 独立期待値と算出根拠 | 観点 |
|---|---|---|---|
| PT-DB-016 | PostgreSQL18隔離clusterへV001～021を適用。合成`CLEAN_EXPIRY` RUNNINGと`BACKUP_DB` RUNNINGを挿入し、監査列の部分設定、SUCCESS、infinity、前後逆転、成功数の不整合、他step列設定を操作 | SS331 §8.2・341 §9の3列型`timestamp with time zone/bigint/bigint`、Expiry3列は全NULLまたは全非NULL、SUCCESSには監査必須、`before-after=success=target`/failure0、他stepは全NULL。各不整合はSQLSTATE23514、正常行だけ保存。`schubert_batch`参照可能、Web session role拒否。Production SQLの結果から期待値を生成しない | 正常・境界・異常・NULL・例外・role |
| PT-DB-017 | 別隔離DBでV001～020を適用し、旧`CLEAN_EXPIRY` SUCCESSを合成挿入した後V021を適用 | 旧SUCCESSのrun cutoff/前後countは既存列から計算不能。SS331 §8.2に従いmigrationは非成功、historyは20件、追加監査列0件（DDL transaction rollback） | 移行・欠落・安全停止・再実行 |

共通回帰は`DatabaseMigrationTest`全17 case、`StepCleanupBoundaryTest`、`InspectionParentBoundaryTest`を対象とする。既存V001～020のhashと全21 inventory、他stepのNULL、権限既存grant不変を確認する。V005の既存app table-level DMLは追加列に及ぶため、「新規grantなし」を「app拒否」と読み替えない。

選択実行command（repo root）:
```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 \
./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository \
-Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node \
--no-transfer-progress -pl src/schubert-nk-api \
-Dtest=DatabaseMigrationTest,StepCleanupBoundaryTest,InspectionParentBoundaryTest test
```

合格は失敗/エラー/skipped/not-run0、Java全moduleのline/method/class/branch100%、SQLは上記独立制約・移行・権限matrix全条件、Production静的解析0、秘密情報scan0、全49正式evidence scope/hash整合（本Program専用`evidence/expiry-audit/manifest.json`を含む）。実行日時・OS/JDK/PostgreSQL/Flyway/pgJDBC・branch/source commit/exit code/coverage/manifest hashは対の065結果と正式manifestへ記録する。初回失敗は合格に算入しない。
