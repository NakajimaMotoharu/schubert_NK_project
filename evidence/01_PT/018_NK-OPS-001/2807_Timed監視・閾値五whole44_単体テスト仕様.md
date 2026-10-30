# 2807 Timed監視・閾値五whole44仕様

event3201/primary P018-09、着手見積1/4/8pp/cap8、source6b53/normal14216固定。原5whole44、全Test1185行と必要Main/helper/initializerを読了、既989のsuite/Sourceと非重複を実照合した。NORMAL_PT、供給済みpercent/count/time/booleanだけで実監視・収集・制御をしない。

対象全SourceはTimedFilesystemMonitor/TimedJvmHeapMonitor/TimedDbPoolMonitor/TimedSyncLatencyMonitor/AlertThresholds（5Source/outer5+Evaluation4=9Code）。関連NK-OPS-001/RD171/UI252/SS351§7・P018-09、正本ownerは承認ruleのcandidate-not-acceptedを保持する。

|原suite/Test ID|件数|独立期待値・観点|
|---|---:|---|
|TimedFilesystemMonitorTest/TIMEDFS001～006|6|80%5分/90%1分の厳密境界、warning5分/critical10分＋cause回復、欠測/gap不連結、null/不正/逆行状態不変、並行64と固定local status文字列|
|TimedJvmHeapMonitorTest/HEAPTIME001～008|8|75%10分/90即時、供給OOM報告は実OOMでない、欠測と報告を分離、critical sticky/null/不正/逆行/gap/並行64/別owner|
|TimedDbPoolMonitorTest/DBTIME001～008|8|80%5分/pending-timeout即時、UNKNOWNを0にしない、cause/回復/null/負・maxcount/逆行/gap/並行64/別owner|
|TimedSyncLatencyMonitorTest/SYNCTIME001～008|8|strict >2.0/>2.5秒×5分、nano手前/同時点、欠測/gap不連結、null/NaN/infinity/負/Double.MAX/並行64/別owner|
|AlertThresholdsTest/PT-OPS-THRESH001～014|14|SS351全12alertの独立数値/OR条件/byte・count比/overflow回避/時間・percent境界、null/不正・全negative、stateless並行64|

期待値はTest内固定literal/SS351 tableから独立作成、production呼出でexpected生成0。MonitoringStatusText helper全bodyも読了し固定SUPPLIED状態文字列だけ検証、helper親Source資格化はしない。ObservationContext/AlertLifecycle/ContinuousWindow/Mode等既helperは必要Main読了・旧proof保持、新五Sourceへcounter合算0。

原5wholeを除外・分割せずfresh javac proc:none/Werror/own一JVM180秒、各pool/finallyの終了を保持。実FileStore/MXBean/DB/percentile/OS/clock/network/service/VM/Root/鍵/Graph操作0、実OOMを生成しない。fixtureは公開Test内値だけ、XML/exec以外の製品I/O0。

command checked entry pg14946_timed_threshold_pure_forty_four_pt.py。全Test hashはrunner PINS・normalと同一、JDK25.0.4/JUnit/JaCoCo0.8.15。実環境/source/run/command/exit/時刻/XML44/CRC/全9class/四counter/障害は2808・PG14946～50へ。実不足/N/Aは保持し100%へ補完せず、451/F03/G07/QA051final/正式1964/53/工数null/全HOLDを維持する。

Generated取扱いは451のJaCoCo0.8.15標準filterを変更せず、4 Evaluation recordのcompiler生成equals/hashCode/toString/accessor等だけが公式解析対象外となる場合がある。独自分岐を持つconstructor/observe/snapshot/閾値等の手書きlogicはすべて含める。全9class/全Code methodのinventoryを保存し、手動除外0。各recordの供給値/optional/accessor/null契約を原44で明示assertし、generated値契約の原55も別証跡として保持するがexec counterを合算しない。これにより要求business logicの四counter分母を削らない。
