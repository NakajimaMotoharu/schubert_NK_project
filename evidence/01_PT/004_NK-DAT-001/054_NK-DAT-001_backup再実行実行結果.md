# NK-DAT-001 backup再実行 実行結果

2026-09-20 最新確定: 正式PT-WEB-20260920-22/source4e942a7485899d262a6d8d4eab56aad8228f7291、08:25:04～08:36:55 JST/Maven11:49/exit0、全1633PT（Protocol80/Storage82/API689/Web374/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review継続・coverage除外追加なし、CHR SpotBugs未設定。JS1file全line/function/branch100%、18collector/41scope整合・71負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web15/133＝89部分成果843PT（全1633の内数）、今回再開比+218PT/+24部分成果。PG206通信共通化・Animation facade8PTを限定認定、BUG221/YKT177完了。PG207 HTTPは仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/残Web・本文controller-file/readiness/Logout/QA045/実NKgateは未完了。Animation HTTP未接続なので固定加重38.85～50.35%（中心45%、約39～50%）を維持。残量25%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

053/PT233～240、BUG-138/139・YKT-108/109・SSC-054/PG-D-145。V017/8 PT実装済み、探索2で関連103件全成功（2026-09-09 19:19:29 JST、exit0）。正式40は未実行、正式39の認定へ遡って加算しない。親の実backup生成/最新artifact照合は別未完了。

探索1（19:17:03 JST、exit1）は新8件とDatabaseMigration15件成功、CleanupSafetyのmigration文字列inventory1件が旧016のままで不一致。BUG-139/YKT-109をff31bb02で修正前起票し、count/連結文字列/List/resource名の全10箇所を確認した。探索2は固定JDK25/MavenでBackupRerunBoundaryTest/DatabaseMigrationTest/CleanupSafety/LogCleanupProgress/QuestionQuery/InboxInspectionProgress/InboxInspection/InboxDeletion/InboxMaintenance/OutboxCleanup/QuestionMutationの全103件を再試験。Protocol/Storageの選択用2件を新8件へ加算しない。

旧V004 indexのrollback-only再現は2回目SUCCESSの23505、新V017は旧成功を保持して2回目を保存。両backup/通常12step・類似名/全status・attempt/NULL・rollback・16並行/重複競合・全8cleanup gate/Inbox helper/ACLを確認。013件のPython証跡負canaryも探索PASS、正式40では017と合わせ14件・全35scope/12collectorを確認する。SQLのpredicate網羅とJava JaCoCo100%は混同しない。
