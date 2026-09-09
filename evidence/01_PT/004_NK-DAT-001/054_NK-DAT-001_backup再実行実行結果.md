# NK-DAT-001 backup再実行 実行結果

2026-09-09 最新確定: dev-foundation/source20af737d、正式PT-WEB-20260909-42（19:47:16～19:54:18 JST）、全1075件（Protocol80/Storage50/API634/Web241/Batch29/CHR41）PASS、failed/error/skipped0。6 Java moduleのline/method/class/branch100%、Production5 moduleのSpotBugs0/NullAway・Enforcer・Spotless PASS（CHR runnerのSpotBugsは未設定）。12collector・35証跡scopeの同run/source/branch/hash/参照、017の1件・019の14件負canary成功。DB26部品240 PT＋batch2部品29 PT＋OPS2部品16 PT＝30部分成果285件確定。PG-D-146の実Linux flock8 PT（実コマンド双方向競合、32並行、FD/例外回収、inode差替え）を追加し、BUG140/YKT110を再試験完了。正式41はbranch1不足で不合格・後続3module未実行として保存。親root lockfile検証PG-D-147はSS/PT仕様のみ未合格。親inactive/実backup/DB引渡し/root設定publish・全cleanup監査・通常Question writer/replay・RERUN-001は残る。BUG-014/UIC-006/SSC-049/052継続、加重見積約4割（35～50%、456）、試験件数だけで加点しない。週間残18%。元dev-web Scenario3fileは保全・不算入、CHR41はrunner PTであり実NK互換gateではない。以下は履歴。

053/PT233～240、BUG-138/139・YKT-108/109・SSC-054/PG-D-145。V017/8 PT実装済み、探索2で関連103件全成功（2026-09-09 19:19:29 JST、exit0）。正式40は未実行、正式39の認定へ遡って加算しない。親の実backup生成/最新artifact照合は別未完了。

探索1（19:17:03 JST、exit1）は新8件とDatabaseMigration15件成功、CleanupSafetyのmigration文字列inventory1件が旧016のままで不一致。BUG-139/YKT-109をff31bb02で修正前起票し、count/連結文字列/List/resource名の全10箇所を確認した。探索2は固定JDK25/MavenでBackupRerunBoundaryTest/DatabaseMigrationTest/CleanupSafety/LogCleanupProgress/QuestionQuery/InboxInspectionProgress/InboxInspection/InboxDeletion/InboxMaintenance/OutboxCleanup/QuestionMutationの全103件を再試験。Protocol/Storageの選択用2件を新8件へ加算しない。

旧V004 indexのrollback-only再現は2回目SUCCESSの23505、新V017は旧成功を保持して2回目を保存。両backup/通常12step・類似名/全status・attempt/NULL・rollback・16並行/重複競合・全8cleanup gate/Inbox helper/ACLを確認。013件のPython証跡負canaryも探索PASS、正式40では017と合わせ14件・全35scope/12collectorを確認する。SQLのpredicate網羅とJava JaCoCo100%は混同しない。
