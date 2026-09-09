# NK-DAT-001 Log永続走査 実行結果

最新正式再試験: PT-WEB-20260909-38/sourcedfc17ae2、2026-09-09 18:20:11～18:27:07 JST、dev-foundation、exit0。全体1039件（Protocol80/Storage42/API606/Web241/Batch29/CHR41）、6 Java moduleのline/method/class/branch100%、Production5 moduleの静的解析PASS。対象Test ID・個別結果・coverageはevidence/log-cleanup-progress/manifest.json、SHA-256 `8b0602c1af69a37ae4e5925c3cccb07423e96fe55c9acbe337ab442947b59312`。全32scope/10collectorの同run/source/branch/hash/参照、017の1件・019の10件負canary成功。Current baseline不変、秘密pattern scan0hit。更新3参照は045/046、DB credential/接続は047/048、外側resource寿命は049/050で合格、通常writer/replay・main/oneshot・親OS/実backup/実NK CHRは未完了。以下は個別試験・過去の探索履歴（旧件数/hashを現在値に用いない）。

039/PT153～160、BUG-104/YKT-092、SSC-051/PG-D-136。探索3は2026-09-09 14:11:16 JST終了、52.781秒、dev-foundation/ae5690dd後の未commit実装、exit0。新SQL8＋旧SQL48＋DB15＋Protocol5＋Storage16=92件全成功。NullAway/Enforcer/Spotless PASS・SpotBugs0。SQLは039の条件matrixで評価し、JaCoCoへSQLが含まれるとはしない。正式全体回帰・証跡確定までは未合格。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,DatabaseMigrationTest,InboxInspectionBoundaryTest,InboxDeletionBoundaryTest,InboxMaintenanceBoundaryTest,OutboxCleanupBoundaryTest,InboxInspectionProgressBoundaryTest,CleanupSafetyBoundaryTest,LogCleanupProgressBoundaryTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。

作業log: `/tmp/pgpt-log-cleanup-progress-explore-3.log`。探索1のformat失敗はBUG-105/YKT-093、探索2の旧lock/count oracleと時刻literal失敗はBUG-106～108/YKT-094/095を修正前起票。診断runは失敗mutationを特定するための未合格実行。これらを成功件数へ含めない。

旧V013の先頭hold2件反復をrollback-onlyで再現し、新SQLは同runで2/0/2→1/1/0→0、累積3/1/2/END・held2件不変。未commit、savepoint、row/progress lock、100並行、overflow rollback、cutoff不一致、3timezoneでの90日同値拒否、400日±µs/調査中/未完了保護、23table/154CHECK/役割を照合した。親batchの累積読取・実backup/OS lock/専用mainは別未完了。SQL部分の成功でBUG-014/YKT-012や工程全体を完了にしない。
