# NK-DAT-001 backup再実行 実行結果

2026-09-12 最新確定: dev-foundation/source e8bb5731c57bd5c03526202fc51c9009ffe3e2b5、正式PT-WEB-20260912-04（22:15:42～22:23:07 JST）、全1145件（Protocol80/Storage58/API634/Web241/Batch91/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/runの限定静的レビュー1件は維持しcoverage除外なし、CHR runnerのSpotBugsは未設定。12collector/35scopeの同run/source/branch/hashと18負canary成功。DB26部品240＋batch3部品37＋OPS10部品78＝39部分成果355 PT（全1145の内数）、今回run環境publisher12件を追加しBUG151～153/YKT117～119再試験完了。PG155/固定account・namespace接続16件は仕様のみで未合格。親実子制御/backup artifact/固定namespace/SSC055原本・全cleanup caller・通常Question writer/replay・Logout RERUN001・QA045は残る。固定加重約4割（35～50%、456）を維持、残件は460。実NK CHR/IT/ST完了とはしない。利用枠残91%でPG/PT継続中、元dev-web3file保全。以下は履歴。

053/PT233～240、BUG-138/139・YKT-108/109・SSC-054/PG-D-145。V017/8 PT実装済み、探索2で関連103件全成功（2026-09-09 19:19:29 JST、exit0）。正式40は未実行、正式39の認定へ遡って加算しない。親の実backup生成/最新artifact照合は別未完了。

探索1（19:17:03 JST、exit1）は新8件とDatabaseMigration15件成功、CleanupSafetyのmigration文字列inventory1件が旧016のままで不一致。BUG-139/YKT-109をff31bb02で修正前起票し、count/連結文字列/List/resource名の全10箇所を確認した。探索2は固定JDK25/MavenでBackupRerunBoundaryTest/DatabaseMigrationTest/CleanupSafety/LogCleanupProgress/QuestionQuery/InboxInspectionProgress/InboxInspection/InboxDeletion/InboxMaintenance/OutboxCleanup/QuestionMutationの全103件を再試験。Protocol/Storageの選択用2件を新8件へ加算しない。

旧V004 indexのrollback-only再現は2回目SUCCESSの23505、新V017は旧成功を保持して2回目を保存。両backup/通常12step・類似名/全status・attempt/NULL・rollback・16並行/重複競合・全8cleanup gate/Inbox helper/ACLを確認。013件のPython証跡負canaryも探索PASS、正式40では017と合わせ14件・全35scope/12collectorを確認する。SQLのpredicate網羅とJava JaCoCo100%は混同しない。
