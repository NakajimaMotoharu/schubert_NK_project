# NK-DAT-001 backup再実行 実行結果

正式PT-WEB-20260909-40/source2dfbaaf533012c4720d1626241ec6243b74d7fcd、dev-foundation、2026-09-09 19:22:08～19:29:08 JST、exit0。新8 PT・全1067件（Protocol80/Storage42/API634/Web241/Batch29/CHR41）PASS、failed/error/skipped0。6 Java moduleの4coverage100%/Production5静的解析PASS。35scope/12collector/14負canary同run/source/branch/hash/参照一致。evidence/backup-rerun/manifest.json SHA-256 934d9828629c3ec6f89eab7f2be780b9d93545a0a760c8f8ac87b02165cd3802、root manifest 5bf54aa70ad4e01eafc570202447c70ac19ee8c670396538b3449af405777dc6。BUG138/139・YKT108/109・SSC054の本制約/10 inventory class/全backup gate再試験完了。旧V001～016とCurrent baseline不変、既知秘密pattern0hit。SQLをJava coverageと混同せず、親実backup/OS/次flock部品は未合格。以下は探索履歴。

053/PT233～240、BUG-138/139・YKT-108/109・SSC-054/PG-D-145。V017/8 PT実装済み、探索2で関連103件全成功（2026-09-09 19:19:29 JST、exit0）。正式40は未実行、正式39の認定へ遡って加算しない。親の実backup生成/最新artifact照合は別未完了。

探索1（19:17:03 JST、exit1）は新8件とDatabaseMigration15件成功、CleanupSafetyのmigration文字列inventory1件が旧016のままで不一致。BUG-139/YKT-109をff31bb02で修正前起票し、count/連結文字列/List/resource名の全10箇所を確認した。探索2は固定JDK25/MavenでBackupRerunBoundaryTest/DatabaseMigrationTest/CleanupSafety/LogCleanupProgress/QuestionQuery/InboxInspectionProgress/InboxInspection/InboxDeletion/InboxMaintenance/OutboxCleanup/QuestionMutationの全103件を再試験。Protocol/Storageの選択用2件を新8件へ加算しない。

旧V004 indexのrollback-only再現は2回目SUCCESSの23505、新V017は旧成功を保持して2回目を保存。両backup/通常12step・類似名/全status・attempt/NULL・rollback・16並行/重複競合・全8cleanup gate/Inbox helper/ACLを確認。013件のPython証跡負canaryも探索PASS、正式40では017と合わせ14件・全35scope/12collectorを確認する。SQLのpredicate網羅とJava JaCoCo100%は混同しない。
