# 1604 DBPool時系列警報 実行結果

source `e9c0ba2a180262f8410ae16c46f5909787b5132b`、1603/PG-D534/group1850。PG7224-db-pool-host-v1原SHA `9270760d220275f0728fc84b8e8ae8a0faf7b6f2e8082acdb05144b825b3d71f` は真正verify0/132PT18suite/FES・rerun/flaky0/六format0。新8と既124の当source必要回帰を分離し、旧sourceの合格は算術加算しない。期待値はSS351の80%/5分、pending/timeout1件、warning5分・critical10分正常＋原因確認から固定し、productionをexpected算出に使わない。

PG7226-db-pool-post-v1原SHA `bd2cc87daab25d573fad196fcaff81c2f7d7fa63d8ccfea2ba850779729956d4` は全38Java source/実30class＋metadata1・単一sessionCRC0、**L550/M125/C30/B255全miss0**。親Enforcer/lint/Werror/NullAway/六format・SpotBugs/Checkstyle0、PMD raw25/exit4/processing0。旧23は全指摘対象Main同byteの理由のみ継承、新TimedDbPoolMonitor.observe/snapshotのprivate final lock二行はwindow/elapsed/lifecycleを直列化する契約必須、外部this/class monitor露出/逆向きcallbackなし、DBTIME007の64並行とimmutable snapshotで検証。全行機械結合は1606、抑制/未知0。

DBTIME001～008全成功：80%継続299.999999999秒直前/300秒丁度、pending/timeout個別critical、未知percent＋既知critical、未知/gapの違反・回復中断、invalid/null/逆行で状態不変、critical sticky、Long.MAX_VALUE既知件数、二owner独立/64並行count65。pending/timeoutは既知観測入力であり、実poolのcounter意味/観測期間/actual timeout成功を認定しない。

新障害/上位変更0。実JDBC/DB/Hikari/provider操作・Root/finite期限・owned停止/制御/exporter/native/CHR/全scope同source451は未受入HOLD。正式1964/53・歴史17/別source新7・原190新受入0/工数null/QA051final/PTALT0不変更、原本/鍵/native/stash/Currentbaseline保全。OS/JDK/tool・branch/source・command・日時・終了/XML/coverage/static/hashは原7224/7226manifestへ一意対応。
