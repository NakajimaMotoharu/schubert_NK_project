# NK-DAT-001 原子cleanup_step実行結果

正式認定: PT-WEB-20260913-08、source fbc121e2ddad645e876d659dff7dd1d0db86c7ee/dev-foundation、2026-09-13 05:50:30～06:06:17 JST、exit0。全1327件（Protocol80/Storage58/API660/Web241/Batch247/CHR41）failed/error/skipped0、6 Java moduleのline/method/class/branch100%、5 Production static未解決0・新除外なし。15collector/38scope/30負canary成功。PG164新5classは19method/145line/102branch、共有CleanupKindは5method/22line/6branch、各missed0。SQLは17predicate×3境界/全7kind、Repository53・Service115 JDBC故障位置、18時刻/18例外組、全8実traceを独立期待値で確認。BUG179～181/YKT140～142・SSC057完了。

正式commandは sh /home/mini/codex/project1/work/pgpt_foundation_verify.sh PT-WEB-20260913-08（内部clean verify）。環境・全ファイルSHA256・input/expected/actual・実XML・coverage・staticはevidence/atomic-cleanup/manifest.jsonとchecksums.sha256へ格納。対象Test ID: PT-DB-INBOX-259～266。親実子/backup/全cleanup/実NK CHR・PGPT/IT/STは未完了。以下は探索履歴であり現在の認定値ではない。

PG164/SSC057、PT-DB-INBOX-259～266。探索成功・正式認定待ち。SQL8、17predicate代替×3境界・全7kind/10table/typed7列/NULL/FK/rollback/20inventory。

選択結合実行: 2026-09-13 05:44:46 JST終了、39.764秒、exit0。/tmp/pgpt-atomic-cleanup-combined-explore1.log、API31（本SQL8/既存parent8/DDL15）・Batch48（新24/PG163既存24）＋Protocol/Storage選択PT、failed/error/skipped0。sourceはdev-foundation/HEAD231b948f上の未commit candidateであり正式sourceの証跡へ流用しない。JDK25.0.4/Maven3.9.12、PostgreSQL18.6/pgJDBC42.7.13/Flyway13.4.0、Ubuntu26.04.1。421と017/032参照。

実行command:
```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api,src/schubert-nk-batch -am -Dtest=StepCleanupBoundaryTest,DatabaseMigrationTest,InspectionParentBoundaryTest,CleanupStepRepositoryTest,CleanupStepValuesTest,StepCleanupServiceTest,BatchRunRepositoryTest,BatchStepValuesTest,LinuxFileLockTest,MessageCodecTest test
```

BUG179/YKT140の実trace起点、BUG180/YKT141の共有module25class所有漏れは先行起票後に是正。PG164/PG163全8 actual traceは独立literalと一致、30負canary成功。詳細対象・非該当根拠・初回非合格は017/032に保存。新Java5class/19method/148line/102branchは探索で4coverage100%、全moduleの正式結果ではない。SQLcoverageは仕様のpredicate/状態/境界表で確認しJaCoCoと混同しない。

正式全reactor・static・38scope同source/run/hashの再収集はこれから。正式run/targetCommit/環境/日時/command/終了code/coverage/BUG・SSC/全input-output SHA256をmanifestへ確定するまで未完了。親OS/実子/backup/全step・実NK CHR、PGPT/IT/STは完了にしない。
