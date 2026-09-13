# NK-DAT-001 backup再実行 実行結果

2026-09-13 最新確定: dev-foundation/source 820554603bca7e5ddd358139f33dee27c9ae87c3、正式PT-WEB-20260913-13（09:48:33～10:04:44 JST）、全1415件（Protocol80/Storage66/API660/Web241/Batch327/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/etc・/run・/varの3 method限定静的レビューを維持しcoverage除外なし、CHR runnerのSpotBugsは未設定。15collector/38scopeの同run/source/branch/hashと41負canary成功。DB29部品266＋batch22部品241＋OPS14部品118＝65部分成果625 PT（全1415の内数）。PG169 root manifest reader16 PTとPG170共通資源scope8 PT、実保持inode/排他/Probeの複合故障回帰を認定。BUG196～197/YKT155～156完了、BUG195/SSC063の直接対象は修正済みだがYKT154の広域残候補は未完了。SSC062のreader範囲は完了。root manifest生成/実dump・tar・age/7世代・親実子制御/全cleanup接続/通常Question writer/replay/Logout RERUN001/QA045は残る。固定加重約4割（35～50%、456）を維持、残件460。実NK CHR/IT/ST完了とはしない。利用枠残19%で継続中、元dev-web3file保全。以下は履歴。

053/PT233～240、BUG-138/139・YKT-108/109・SSC-054/PG-D-145。V017/8 PT実装済み、探索2で関連103件全成功（2026-09-09 19:19:29 JST、exit0）。正式40は未実行、正式39の認定へ遡って加算しない。親の実backup生成/最新artifact照合は別未完了。

探索1（19:17:03 JST、exit1）は新8件とDatabaseMigration15件成功、CleanupSafetyのmigration文字列inventory1件が旧016のままで不一致。BUG-139/YKT-109をff31bb02で修正前起票し、count/連結文字列/List/resource名の全10箇所を確認した。探索2は固定JDK25/MavenでBackupRerunBoundaryTest/DatabaseMigrationTest/CleanupSafety/LogCleanupProgress/QuestionQuery/InboxInspectionProgress/InboxInspection/InboxDeletion/InboxMaintenance/OutboxCleanup/QuestionMutationの全103件を再試験。Protocol/Storageの選択用2件を新8件へ加算しない。

旧V004 indexのrollback-only再現は2回目SUCCESSの23505、新V017は旧成功を保持して2回目を保存。両backup/通常12step・類似名/全status・attempt/NULL・rollback・16並行/重複競合・全8cleanup gate/Inbox helper/ACLを確認。013件のPython証跡負canaryも探索PASS、正式40では017と合わせ14件・全35scope/12collectorを確認する。SQLのpredicate網羅とJava JaCoCo100%は混同しない。
