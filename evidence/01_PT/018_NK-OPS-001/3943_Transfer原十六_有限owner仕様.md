# 3943 Transfer supplied原16 有限owner仕様

G03.05主/P01809関連、REWORK見積1/3/6pp cap8。2815原81のTransferMetricRecorderTest8/TransferHealthMonitorTest8（whole2/16）を全原body/fixture読了、Main Recorder/Counts/Usage/Suffix とHealth/Evaluationの2Source6Codeを対象とする。SDKは25148/25153固定1.17.1 core/commons/observation所有registry/MockClockのみ、helperは既読AlertLifecycle/Threshold/Poller/Clock/Context/MetricContract/Mode。実walk/transfer/FS/JMX/DB/Root/VM/native/permit/鍵/networkは無関係・実行0。原whole先行成功の確認再演をしない。

BUG2577を915へ修正前起票。実装済み原Met007/Conn008の2invokeAllと2ExecutorTWR.closeが無期限で411§10違反。各poolをregistry内側単一finally.shutdownNow/await10へ・invokeAll10へ。get()はtimed invokeAllから返るterminalFutureだけを取得する原bodyを保持。全期待/literal/固定入力を逆復元で照合、registryはworker後に閉じる。

|TestID|件数|独立期待・境界/null/例外/並行|
|---|---:|---|
|TRANSFERMET001..008|8|固定2names×2suffix=4gauges、NaN≠0/回復、2+3=5・1024+2048=3072、longMax加算/overflow・double固定9_223_372_036_854_776_000.0、immutable snapshot/64workers二固定Usage、partialfactory1/同例外・registryborrowed|
|TRANSFERCONN001..008|8|3.5G/4.5G bytes・5000/9000files各直前と境界、part+ready合算、WARNING300/CRITICAL600供給経過、gap/欠測で再起算・UNKNOWN≠normal、cause未確認保持/confirm後close、null/backward保全・provider同一性、初回1+64=65/旧snapshot1|

NORMAL_PT: actualin-memoryregistryと固定供給値/MockClockのみ、原16一JVM/一session、必要Mainは固定Jarから対象6classだけcoverage用抽出、Main再compile0、held4 compile/init/probe0。元Test2を全source compile、SDK3既Jar+必要annotation/Consoleのみ。source固定/push後一度実行し独立XML/case/command/exit/CRC/Source四counter/静的個別分類/SS351独立goldenで検証。SDKidentity再利用は実Jar/class一致時だけ、旧成功coverage合算0。新unique/leaf/正式1964-53・工数nullは不変。PG25164/66/68/70/72と3944に証跡。全HOLD/477継続/残10%保全維持。
