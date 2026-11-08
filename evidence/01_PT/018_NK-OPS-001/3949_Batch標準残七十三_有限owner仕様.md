# 3949 Batch標準残73 有限owner仕様

G03.05主/P01809関連、REWORK着手前見積1/4/8pp cap10。2823/2824の原六whole110から25226/28で修正再試験済みText37を除き、残五whole73を対象。全Test2210行とMain五Source全bodyを確認。旧110/新37の成功確認再演0。SDKは既8170/8173/25234と同byte11Jar、既2823の自己child JVM public CPU/runtime/FD/heap・GC listener所有/finally範囲を保持、強制GC/OOM/負荷/dump/attach/外部target/VM/Root/DB/network/鍵/permit/サービス操作0、四held compile/init/probe0。

|原whole/TestID|件数|独立oracle/正常/境界/null/例外/並行|
|---|---:|---|
|BatchStandardMetricSourceTest/BATCHHOST001..016|16|STANDARD遅延/単回bind/owner保持、null/未知/factory/error/partialGC、GC→registry逆順・close失敗は未確認/明示retry、有限latch scrape/close競合、自己CPU Runtime独立値|
|BatchJvmMetricsTest/BATCHJVM001..014|14|固定4binder/tag、独立RuntimeMXBean start秒/uptime前後±1ms、STANDARD0・4順序/immutable copy/null/数0,1,3,5不正/各phase例外、64×4=256|
|BatchSystemMetricsTest/BATCHSYS001..014|14|固定2binder/tag、Runtime CPU/UnixMXBean FDmax・自己CPU ns前後、STANDARD0・2順序/null/数0,1,3,4不正/各phase例外、64×2=128|
|BatchGcMetricRegistrationTest/BATCHGC001..016|16|FACTORY→OWNER→BIND、受領前activate0、null/unknown/closed/owner拒否/throw/partialbind、close未確認は保留・明示retry/成功guard重複close0、64×1=64|
|BatchStandardMetricsTest/BATCHSTD001..013|13|JVM→SYSTEM→GC、GC→registry終了・STANDARD3phase0/null/phase失敗後続0・owner拒否/throwでも借用保持、別GC handle、64×3=192|

BUG2585を915修正前起票後に是正。Host016は既内側finally.release.countDown/shutdownNow/await10/owner.closeがあるため、外TWRによる無期限再closeだけ除去（既body/finallyは一字も変えない）。他四Testの各workers TWRを単一finally.shutdownNow-await10へ。全5 owner・既Futureget10六site/latch wait10/元73body/literal/fixture/呼出順を保持、invokeAll追加0。Test相互参照は全body検索0で追加補助Test不要、compileは元五source全文のみ。

対象MainはStandardMetricSource/JvmMetrics/SystemMetrics/GcMetricRegistration/StandardMetricsの全五Source五Code。必要helperはMonitoringModePolicyのみ、現normal/index全実在/SourceSHA/physical名を出力前に照合。元formatter差分を先に観測し定数分割があればexact値一致以外許容しない。raw token/decoded oracle役割を先に確認し新汎用parserを増やさない。source固定・push後一new JVM/一exec/sessionで原73を一度実行、独立XML/case/全Sourcecounter/Main+SDKCRC/held四/静的分類/独立順序と件数・自己JDK別観測を照合。未達/N-A/失敗を保持、旧exec/別run合算0。SDK identityはProduct coverageへ加算0。実command/環境/対象commit/hash/結果はPG25252/54/56/58/60/62と3950、正式1964/53・520uniqueJava416・工数null/QA051final/外部HOLD不変。

実行前差分観測：全五元Testのstring literal inventoryは完全一致、formatter連結変化0。PMD45=CloseResource23/Thread22は各class/method/variable/lineごとに25258分類、Host helperのinterrupt復元と既明示close済み/GC caller-owned finallyも個別確認。BUG2586はstandalone inverseがtry閉じ括弧まで除去して25268終了1/製品前・出力前。正しい閉じ括弧復元一式へ是正、全四programの実before誤inverseを拒否し元Gitへ完全一致、Host別branchは非該当保持。8仮想括弧変異案を完了実績にせず、実before四target失敗vectorと全五正常逆復元を再発防止証拠とする。元失敗/見積/期待/HOLD保持。
