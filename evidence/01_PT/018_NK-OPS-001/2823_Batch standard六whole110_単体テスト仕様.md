# 2823 Batch standard六whole110仕様

event3217/P01809、source6b53/normal14216固定、着手見積2/6/10pp/cap10。原六whole110全Test3044行と六Main382行・default factories/initializer/closeを読了、既1209とのsuite/Source非重複・全12owner候補を事前照合した。

NORMAL_PT：新しく当工具が所有するchild JVM内だけで公式Micrometer SDKを初期化する。CPU数/自己runtime start/uptime/CPU time/FD上限/自己JVM gaugeをpublic MXBeanから読取り、GC listener handleはowner受領後登録・finally/try-with-resourcesでGC→registryの逆順close。強制GC/負荷/OOM/heap dump/target process/attach/外部VM/業務Root/DB/サービス/network/鍵/配置操作0。旧拒否graph/cohort/recovery chainとは無関係、外部UNOBSERVED_HOLDは保持する。自己JVMを測る元whole PTをfake値へ置換せず、実測とfake lifecycle vectorを区別する。

|原whole/Test ID|件数|独立期待値・主観点|
|---|---:|---|
|BatchMetricTextTest/BATCHTEXT001～024＋BATCHFULL001～013|37|固定HELP/TYPE/sample bytes・並び/全6family、NaN/Inf/signed-zero/MAX/min literal、closed-domain/null/重複/wrong type/各provider一回capture、失敗時partial無し・borrowed所有/並行64・custom→standard順序/自己CPU独立値|
|BatchStandardMetricSourceTest/BATCHHOST001～016|16|STANDARD遅延、単回bind/二重拒否、closed/null/factory/error/partialGc保持、GC→registry逆順/明示close失敗未確定/再試行、scrapeとclose競合の有限latch、既知CPU数/標準text|
|BatchJvmMetricsTest/BATCHJVM001～014|14|固定4binder/tag/namespace、MXBean独立start/uptime bracket、STANDARD無読取、port順序/immutable snapshot/null/数不足/各phase例外/borrowed owner/独立並行64|
|BatchSystemMetricsTest/BATCHSYS001～014|14|固定2binder/tag/namespace、Runtime CPU数・UnixMXBean FD max・CPU ns独立前後bracket、STANDARD無読取/順序/null/各phase失敗/独立並行64|
|BatchGcMetricRegistrationTest/BATCHGC001～016|16|FACTORY→OWNER→BIND順序/同一handle、default自己SDK/借用registry維持、null/unknown/closed/owner拒否・throwでactivate0、partial bind保持/明示close確認flag/失敗後のみ明示retry/独立並行64|
|BatchStandardMetricsTest/BATCHSTD001～013|13|JVM→SYSTEM→GC順序、GC→registryclose、STANDARD三phase0/各portnull/phase例外で後続0/owner拒否・throwで借用保持/別handle/並行64×3=192|

期待値はSS351の標準SDK採用・DEBUG/STANDARD・固定label制約、独立literalとJDK public APIの前後bracket、手計算の呼出し数/順序。Production methodでexpectedを生成しない。全六Source各一classの全Codeを当new single exec/session/CRCで測定、全counter100又は実不足/N/Aをそのまま保存し、別execから合算しない。manual除外0/公式generated filters不変更。実値変動を許すbracketは自己取得の前後のみで広い任意許容を置かない。

全poolは有限8以下/64task・待ち5/10秒/finally解放、親child180秒。独立counter/helper compile-onlyなし、原六whole全110を選択する。JDK25.0.4/JUnit/JaCoCo0.8.15、fresh javac proc:none/Werror、Main六Jarはnormal14216固定、empty Prometheus config固定で外部設定を読まない。checked entry pg15018_batch_standard_sdk_one_hundred_ten_pt.py。元環境/時刻/command/exit/全pin/XML/exec/四counter/反例/ownerを2824・15018～22へ。未達/例外/拒否をPASSへ変換せず、新規拒否なら再試行0。正式1964/53/17-190/工数null/QA051final/451-F03-G07/全HOLDと原本/stash7/Currentbaseline/二held/旧全証拠は保持する。
