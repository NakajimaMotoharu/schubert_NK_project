# NK-DAT-001 backup再実行 実行結果

2026-09-20 最新確定: 正式PT-WEB-20260920-12/source0d0abbb80e91d016f961042e9b9e09cb07b5f7a9、05:24:36～05:36:26 JST/Maven11:48/exit0、全1544PT（Protocol80/Storage82/API689/Web285/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review継続・coverage除外追加なし、CHR SpotBugs未設定。18collector/41scope整合・60負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web4/44＝78部分成果754PT（全1544の内数）、今回再開比+129PT/+13部分成果。PG194階層3画面16PTを限定認定、BUG213～216/YKT169～172/SSC071限定範囲完了。PG195本文モデルは仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/残Web/Logout/QA045/実NKgateは未完了。固定加重38.25～49.75%（中心44%、約38～50%）、3画面接続で前回から+1 point。残量49%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

053/PT233～240、BUG-138/139・YKT-108/109・SSC-054/PG-D-145。V017/8 PT実装済み、探索2で関連103件全成功（2026-09-09 19:19:29 JST、exit0）。正式40は未実行、正式39の認定へ遡って加算しない。親の実backup生成/最新artifact照合は別未完了。

探索1（19:17:03 JST、exit1）は新8件とDatabaseMigration15件成功、CleanupSafetyのmigration文字列inventory1件が旧016のままで不一致。BUG-139/YKT-109をff31bb02で修正前起票し、count/連結文字列/List/resource名の全10箇所を確認した。探索2は固定JDK25/MavenでBackupRerunBoundaryTest/DatabaseMigrationTest/CleanupSafety/LogCleanupProgress/QuestionQuery/InboxInspectionProgress/InboxInspection/InboxDeletion/InboxMaintenance/OutboxCleanup/QuestionMutationの全103件を再試験。Protocol/Storageの選択用2件を新8件へ加算しない。

旧V004 indexのrollback-only再現は2回目SUCCESSの23505、新V017は旧成功を保持して2回目を保存。両backup/通常12step・類似名/全status・attempt/NULL・rollback・16並行/重複競合・全8cleanup gate/Inbox helper/ACLを確認。013件のPython証跡負canaryも探索PASS、正式40では017と合わせ14件・全35scope/12collectorを確認する。SQLのpredicate網羅とJava JaCoCo100%は混同しない。
