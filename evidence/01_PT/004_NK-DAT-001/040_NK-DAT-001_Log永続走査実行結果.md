# NK-DAT-001 Log永続走査 実行結果

2026-09-12 最新確定: dev-foundation/source 3eb3712e1b1827154a27fc6bcfe6c47c987e0e32、正式PT-WEB-20260912-05（23:01:26～23:09:05 JST）、全1161件（Protocol80/Storage58/API634/Web241/Batch107/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/etc・/runの2 method限定静的レビューを記録しcoverage除外なし、CHR runnerのSpotBugsは未設定。12collector/35scopeの同run/source/branch/hashと18負canary成功。DB26部品240＋batch3部品37＋OPS11部品94＝40部分成果371 PT（全1161の内数）、PG155の固定account・namespace/環境寿命16件を追加しBUG154～156/YKT120～121再試験完了。R002の環境file部品は確定したが、親実子制御/backup artifact/SSC055原本・全cleanup caller・通常Question writer/replay・Logout RERUN001・QA045は残る。既存停止照会の別障害BUG157/YKT122は先行起票・未修正で次に対応する。固定加重約4割（35～50%、456）を維持、残件は460。実NK CHR/IT/ST完了とはしない。利用枠残86%でPG/PT継続中、元dev-web3file保全。以下は履歴。

039/PT153～160、BUG-104/YKT-092、SSC-051/PG-D-136。探索3は2026-09-09 14:11:16 JST終了、52.781秒、dev-foundation/ae5690dd後の未commit実装、exit0。新SQL8＋旧SQL48＋DB15＋Protocol5＋Storage16=92件全成功。NullAway/Enforcer/Spotless PASS・SpotBugs0。SQLは039の条件matrixで評価し、JaCoCoへSQLが含まれるとはしない。正式全体回帰・証跡確定までは未合格。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,DatabaseMigrationTest,InboxInspectionBoundaryTest,InboxDeletionBoundaryTest,InboxMaintenanceBoundaryTest,OutboxCleanupBoundaryTest,InboxInspectionProgressBoundaryTest,CleanupSafetyBoundaryTest,LogCleanupProgressBoundaryTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。

作業log: `/tmp/pgpt-log-cleanup-progress-explore-3.log`。探索1のformat失敗はBUG-105/YKT-093、探索2の旧lock/count oracleと時刻literal失敗はBUG-106～108/YKT-094/095を修正前起票。診断runは失敗mutationを特定するための未合格実行。これらを成功件数へ含めない。

旧V013の先頭hold2件反復をrollback-onlyで再現し、新SQLは同runで2/0/2→1/1/0→0、累積3/1/2/END・held2件不変。未commit、savepoint、row/progress lock、100並行、overflow rollback、cutoff不一致、3timezoneでの90日同値拒否、400日±µs/調査中/未完了保護、23table/154CHECK/役割を照合した。親batchの累積読取・実backup/OS lock/専用mainは別未完了。SQL部分の成功でBUG-014/YKT-012や工程全体を完了にしない。
