# Web/Batch標準SDK text所有source PG/PT

NK-OPS-001/RD171 MON010～013/UI252/SS311351/PG-D615、主P018-09/C07追加費0。group2039開始fresh41残59/reset1793382075/2-4-8pp/cap10、着手前431/1799/既二StandardMetricsと1809を照合しWeb/Batchの標準text owner未実装を確認。API既16は再演/転用しない。

Program=web.monitoring.WebStandardMetricSourceとbatch.monitoring.BatchStandardMetricSource。各ctor/bind/scrape/detailed/close/factory-registration-retain lambda。各private official registryへ固定role helperだけを登録しmutable getterを公開しない。modeはWeb既HttpMetricContract・Batch既MonitoringModePolicy、STDは取得/scrape0、DEBUG単回取得・GC保持先行、部分失敗の再bind/success偽装0、明示GC先close・private ReentrantLock直列化。新Main2/Unit2、既prepared SDK座標/親を再利用し取得/上書き0、外部POM依存各一件のみ。既custom Batch codecやAPI/共用Bootstrapを変更しない。

Web WEBHOST001～016 / Batch BATCHHOST001～016、各実16の独立fixtureはdefault own fresh JVM標準SDKとpackage内記録port。16観点は1808と同じ責務を各roleで独立実行し、APIのexpected/結果生成を呼ばない。以下各行が両programの同末尾IDへ一意対応する。

|末尾ID|入力・操作|独立期待・根拠|
|---|---|---|
|001|STD bind/scrape、close後STD|factory/registrar0・空text・DEBUG閉鎖拒否|
|002|default DEBUG bind→scrape→caller close|system_cpu_countのRuntime.availableProcessors独立値、固定WEB/BATCH tag・公式JVM名、custom名混入0・以後拒否|
|003|未bind DEBUG/STD|DEBUG拒否/STD空、factory0|
|004|null/unknown/空mode|nonnull/既mode診断で取得前拒否、Web invalid monitoring mode・Batch CONFIG_INVALID|
|005|null constructor ports|NPE契約違反を拒否|
|006|factory Runtimeと再bind|元identity/一回・成功scrape0/再bind不可|
|007|factory Error|元identity・自動再試行0|
|008|factory null|NPE契約違反/成功偽装0|
|009|closed factory candidate|registrar0、明示closeのみ|
|010|GC前registrar Runtime|partial registry保持/元identity、caller close一回|
|011|GC保持後registrar Error|callback ack先行/元identity、GC→registry close一回|
|012|GC close Runtime|新scrape拒否・registry未close、caller明示再closeで残資源解放|
|013|registry close Runtime|未確認をclosed扱い0/新scrape拒否、明示再close/以後冪等|
|014|null GC callback|NPE契約違反/partial registry保持・明示close|
|015|DEBUG再bindとSTD/close二回|bind一回/二重close0|
|016|latch付きscrapeとclose二worker|同owner直列化・scrape完了前close0、有限join後closeと後続拒否|

固定入力/配列/count/order/元例外identity/Runtime値からexpectedを作り、productionの変換をexpectedへ使用しない。元8702正常six→8704新32/2・原XML/log/exec→8706当2Mainのline/method/class/branch100・静的PMD/CS/SB・nullnegative/七metadata反例→8708全1828Main/旧1826同byte/原1669同byte/213ownerと五edge0/field責務→1811/公開scan/commit-push。除外追加/品質緩和/旧exec union0、failed/skipped/notrun合格化0。既source成功を当sourceへ合算しない。

全command/環境/OS-JDK/branch/source/日時/exit/input期待実際/coverage/BUG/hashは各manifestと1811。着手時32 UNRUN、発見障害は修正前915/916。実VM/Root/DB/Backup/鍵/既GC/HTTP/socket/配置/サービス/target通信0、標準text部品は正式endpoint/health authorityではない。正式1964-53/原190新受入0/工数null/QA051final/PTALT0/whole451/CHR/native/全actualHOLD・元-v4-v5/原本stash/Currentbaseline保持、通常小区切りで停止しない。
