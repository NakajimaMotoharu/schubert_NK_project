# NK-DAT-001 原子cleanup_step実行結果

PG164/SSC057、PT-DB-INBOX-259～266。探索成功・正式認定待ち。SQL8、17predicate代替×3境界・全7kind/10table/typed7列/NULL/FK/rollback/20inventory。

選択結合実行: 2026-09-13 05:44:46 JST終了、39.764秒、exit0。/tmp/pgpt-atomic-cleanup-combined-explore1.log、API31（本SQL8/既存parent8/DDL15）・Batch48（新24/PG163既存24）＋Protocol/Storage選択PT、failed/error/skipped0。sourceはdev-foundation/HEAD231b948f上の未commit candidateであり正式sourceの証跡へ流用しない。JDK25.0.4/Maven3.9.12、PostgreSQL18.6/pgJDBC42.7.13/Flyway13.4.0、Ubuntu26.04.1。421と017/032参照。

実行command:
```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api,src/schubert-nk-batch -am -Dtest=StepCleanupBoundaryTest,DatabaseMigrationTest,InspectionParentBoundaryTest,CleanupStepRepositoryTest,CleanupStepValuesTest,StepCleanupServiceTest,BatchRunRepositoryTest,BatchStepValuesTest,LinuxFileLockTest,MessageCodecTest test
```

BUG179/YKT140の実trace起点、BUG180/YKT141の共有module25class所有漏れは先行起票後に是正。PG164/PG163全8 actual traceは独立literalと一致、30負canary成功。詳細対象・非該当根拠・初回非合格は017/032に保存。新Java5class/19method/148line/102branchは探索で4coverage100%、全moduleの正式結果ではない。SQLcoverageは仕様のpredicate/状態/境界表で確認しJaCoCoと混同しない。

正式全reactor・static・38scope同source/run/hashの再収集はこれから。正式run/targetCommit/環境/日時/command/終了code/coverage/BUG・SSC/全input-output SHA256をmanifestへ確定するまで未完了。親OS/実子/backup/全step・実NK CHR、PGPT/IT/STは完了にしない。
