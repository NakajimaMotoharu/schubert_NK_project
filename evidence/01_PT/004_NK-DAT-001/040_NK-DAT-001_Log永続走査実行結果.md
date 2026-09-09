# NK-DAT-001 Log永続走査 実行結果

最新正式判定: PT-WEB-20260909-30/source15cb454a、2026-09-09 14:30:10～14:36:41 JST、dev-foundation、exit0、全967件・6 Java module全4種coverage100%・静的解析0。当scope全Test ID成功、evidence/log-cleanup-progress/manifest.json SHA-256 `9f2555a2e8557dbf680a7f0292ba7ff3588aed0d42ddaa9b562eda7a35733bb2`。全27scope同時点性/hash/参照と017の1件・019の4件負canary成功。DB19部品160件＋batch repository17件確定。BUG-109～111/YKT-096/097再試験完了。BUG-104/SSC-051のSQL永続走査・親repository読取は成功、全件走査service/OS/main/backup gate/7参照/全Program完了は残件。本slice合格と工程全体の合格は区別する。以下は旧正式・探索履歴。

039/PT153～160、BUG-104/YKT-092、SSC-051/PG-D-136。探索3は2026-09-09 14:11:16 JST終了、52.781秒、dev-foundation/ae5690dd後の未commit実装、exit0。新SQL8＋旧SQL48＋DB15＋Protocol5＋Storage16=92件全成功。NullAway/Enforcer/Spotless PASS・SpotBugs0。SQLは039の条件matrixで評価し、JaCoCoへSQLが含まれるとはしない。正式全体回帰・証跡確定までは未合格。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,DatabaseMigrationTest,InboxInspectionBoundaryTest,InboxDeletionBoundaryTest,InboxMaintenanceBoundaryTest,OutboxCleanupBoundaryTest,InboxInspectionProgressBoundaryTest,CleanupSafetyBoundaryTest,LogCleanupProgressBoundaryTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。

作業log: `/tmp/pgpt-log-cleanup-progress-explore-3.log`。探索1のformat失敗はBUG-105/YKT-093、探索2の旧lock/count oracleと時刻literal失敗はBUG-106～108/YKT-094/095を修正前起票。診断runは失敗mutationを特定するための未合格実行。これらを成功件数へ含めない。

旧V013の先頭hold2件反復をrollback-onlyで再現し、新SQLは同runで2/0/2→1/1/0→0、累積3/1/2/END・held2件不変。未commit、savepoint、row/progress lock、100並行、overflow rollback、cutoff不一致、3timezoneでの90日同値拒否、400日±µs/調査中/未完了保護、23table/154CHECK/役割を照合した。親batchの累積読取・実backup/OS lock/専用mainは別未完了。SQL部分の成功でBUG-014/YKT-012や工程全体を完了にしない。
