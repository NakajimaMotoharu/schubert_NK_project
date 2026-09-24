# NK-DAT-001 Expiry段階監査DDL 単体テスト仕様書

2026-09-24 PG246/SSC-078/BUG-238/YKT-189。Program ID `NK-DAT-001`。対象は`V022__staged_expiry_batch_run_audit.sql`と`DatabaseMigrationTest.stagedExpiryAuditPreservesOldRowsAndUnknownAfter`（PT-DB-018）、既存PT-DB-001～017/Batchのmigration・step回帰。関連RD OPS-009/MQ-009、UI251 §8/11、SS331 §8.2・341 §9・343 §9。V001～021/Current baselineは変更しない。

| Test ID | 事前条件・fixture、入力/操作 | 独立期待値の根拠 | 観点 |
|---|---|---|---|
| PT-DB-018 | 隔離実PostgreSQL18/FlywayでV001～021を適用。`CLEAN_EXPIRY RUNNING`合成rowへcutoff/before/target/byteと`after=NULL`を設定し旧23514を再現。別の監査付き旧SUCCESSを作成してからV022を適用。同じ設定を新rowへ行いcommit/re-read、after欠落SUCCESS、target>before、成功値だけ先行を拒否。FAILED unknown-afterを残し、同日attempt2で実後countを確定、repeat migrate | SS341 §9の時系列を固定。V021ではpurge前のafter未知を保存不能、V022後はcutoff/before/target/byteのみdurableでafter NULL。UNKNOWNを0/前値へ補完しない。SUCCESSは実after必須、before-after=success=target/failure0。旧SUCCESSの`2/1/1`不変、V022後history22、再適用0。期待literalは本仕様から決め、Production SQLの戻りで作らない | 移行/正常/NULL/異常/23514/失敗/再実行/旧row不変 |

既存PT-DB-016は最終3値の型・制約、PT-DB-017はV021以前の旧SUCCESS安全停止を維持する。V022は既存の非Expiry3列NULL、155 CHECK/23 table/role/grant/index、V001～021 checksum、全22 migration inventoryを変えない。V022だけではArtemis削除前commit、借用親、OS lock、同run不確定commit、起動後条件は証明しない。

選択実行はrepo rootからJDK25.0.4/offline Mavenで`./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -Dtest=DatabaseMigrationTest,StepCleanupBoundaryTest,InspectionParentBoundaryTest test`。正式は421/451の`tools/quality/030_run_pgpt_verify.sh`と018全49scope/019負canary。失敗/エラー/skipped/not-run0、全Java moduleのline/method/class/branch100%、Production静的0、SQLの独立matrix全項目、秘密情報scan0、同source/run/hashが合格条件。結果の日時/OS/JDK/tool/branch/commit/command/exit/input・期待・実際/coverage/BUG/SSC/manifest SHAを対の067に記録する。
