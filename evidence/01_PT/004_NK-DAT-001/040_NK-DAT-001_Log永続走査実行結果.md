# NK-DAT-001 Log永続走査 実行結果

2026-09-20 最新確定: dev-foundation/source53c2f7bf8fc6bb45851cd088a78e8f9c590fc45b、正式PT-WEB-20260920-07（03:37:38～03:49:28 JST、Maven11:48/exit0）、全1495件（Protocol80/Storage82/API684/Web241/Batch367/CHR41）PASS、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review/coverage除外なし、CHR SpotBugs未設定。16collector/39scope整合・53負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＝73部分成果705PT（全1495の内数）、今回再開比+80PT/+8部分成果。PG189質問入力境界を認定、BUG211/YKT167・SSC070限定完了。PG190空回答providerは仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/Web/Logout/QA045/実NKgateは未完了。固定加重約4割（35～50%）、残量62%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

039/PT153～160、BUG-104/YKT-092、SSC-051/PG-D-136。探索3は2026-09-09 14:11:16 JST終了、52.781秒、dev-foundation/ae5690dd後の未commit実装、exit0。新SQL8＋旧SQL48＋DB15＋Protocol5＋Storage16=92件全成功。NullAway/Enforcer/Spotless PASS・SpotBugs0。SQLは039の条件matrixで評価し、JaCoCoへSQLが含まれるとはしない。正式全体回帰・証跡確定までは未合格。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,DatabaseMigrationTest,InboxInspectionBoundaryTest,InboxDeletionBoundaryTest,InboxMaintenanceBoundaryTest,OutboxCleanupBoundaryTest,InboxInspectionProgressBoundaryTest,CleanupSafetyBoundaryTest,LogCleanupProgressBoundaryTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。

作業log: `/tmp/pgpt-log-cleanup-progress-explore-3.log`。探索1のformat失敗はBUG-105/YKT-093、探索2の旧lock/count oracleと時刻literal失敗はBUG-106～108/YKT-094/095を修正前起票。診断runは失敗mutationを特定するための未合格実行。これらを成功件数へ含めない。

旧V013の先頭hold2件反復をrollback-onlyで再現し、新SQLは同runで2/0/2→1/1/0→0、累積3/1/2/END・held2件不変。未commit、savepoint、row/progress lock、100並行、overflow rollback、cutoff不一致、3timezoneでの90日同値拒否、400日±µs/調査中/未完了保護、23table/154CHECK/役割を照合した。親batchの累積読取・実backup/OS lock/専用mainは別未完了。SQL部分の成功でBUG-014/YKT-012や工程全体を完了にしない。
