# NK-DAT-001 backup再実行 実行結果

2026-09-20 最新確定: dev-foundation/source 1d5b44ad26736366950936653914f67e7e096fe2、正式PT-WEB-20260920-03（02:01:07～02:16:34 JST、Maven15:26/exit0）、全1463件（Protocol80/Storage74/API660/Web241/Batch367/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定path3method限定静的レビュー・coverage除外なし、CHR runnerのSpotBugsは未設定。15collector/38scopeの同run/source/branch/hashと48負canary成功。DB29部品266＋Batch25部品281＋OPS15部品126＝69部分成果673 PT（全1463の内数）。今回9月19日再開比+48 PT/+4部分成果、PG184のroot検証・全4file照合からDB両step原子確定caller8PTを追加認定しSSC067限定完了。PG178～183のSQL資源905複合は既存Test ID内で新件数増算0。BUG195/206・YKT154/162・SSC063の別境界分類は継続。PG185試験並列化/PG186・SSC068 private子生成は仕様のみ。実archive/7世代/親実子制御/全cleanup/通常Question/Web/Logout/QA045/実NK互換gateは未完了、固定加重約4割（35～50%、456）を維持。利用枠残76%で継続、元dev-web3file保全、IT/ST完了ではない。以下は履歴。

053/PT233～240、BUG-138/139・YKT-108/109・SSC-054/PG-D-145。V017/8 PT実装済み、探索2で関連103件全成功（2026-09-09 19:19:29 JST、exit0）。正式40は未実行、正式39の認定へ遡って加算しない。親の実backup生成/最新artifact照合は別未完了。

探索1（19:17:03 JST、exit1）は新8件とDatabaseMigration15件成功、CleanupSafetyのmigration文字列inventory1件が旧016のままで不一致。BUG-139/YKT-109をff31bb02で修正前起票し、count/連結文字列/List/resource名の全10箇所を確認した。探索2は固定JDK25/MavenでBackupRerunBoundaryTest/DatabaseMigrationTest/CleanupSafety/LogCleanupProgress/QuestionQuery/InboxInspectionProgress/InboxInspection/InboxDeletion/InboxMaintenance/OutboxCleanup/QuestionMutationの全103件を再試験。Protocol/Storageの選択用2件を新8件へ加算しない。

旧V004 indexのrollback-only再現は2回目SUCCESSの23505、新V017は旧成功を保持して2回目を保存。両backup/通常12step・類似名/全status・attempt/NULL・rollback・16並行/重複競合・全8cleanup gate/Inbox helper/ACLを確認。013件のPython証跡負canaryも探索PASS、正式40では017と合わせ14件・全35scope/12collectorを確認する。SQLのpredicate網羅とJava JaCoCo100%は混同しない。
