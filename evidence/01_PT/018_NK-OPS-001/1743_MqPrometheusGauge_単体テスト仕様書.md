# 1743 MQ供給圧力 実Prometheus SDK 単体テスト仕様書

NK-OPS-001/WBS-P018-09/C07/RD171 MON005010013/UI252/SS321351/1693～1694/PG-D586。group1970/PG8188fresh20残80/reset1793382075、開始1/2/4pp/cap10。製品はe196d0816c8a4920696d4f601f8b4cf97e9e8b48同byte、MQPressure Recorderが新backendで正規公開表現を持つかの未実施PTを追加する。後続成果索引は当class1693のみ、元Simple成功を実Prometheus成功へ転用しない。

対象MainはAPI MqPressureMetricRecorderとnested Snapshotの実2class、package-infoを保持。他API/Protocol classは依存で当四counterへ含めず、全API/whole451と称さない。実JMS/Artemis管理/DB/VM/Root/network/外部file/secret/observer/部署を操作せず、own memory registry・固定供給tuple・有限workerのみ。6name×6固定address/queue=36sample、余分label/series無しをliteral oracleで検証する。

|Test ID|独立期待値|
|---|---|
|MQPROM001|DEBUG初期の36sample/6Gauge family・未知NaN、six address/queueはSS321固定literal|
|MQPROM002|全6destinationの数値vectorを個別供給、messages/queueBytes/memory/paged/paging/pageFilesを全36比較、余分sample0|
|MQPROM003|truezero/missing/Long.MAX_VALUEの区別、missingが他destination/元Snapshotを変えない|
|MQPROM004|STANDARD supply/missing後もregistry/text/retention0、caller registryは自動closeされない|
|MQPROM005|二ownerの1000回供給もcardinality36/owner独立、既tupleの値不変|
|MQPROM006|64有限own workerの同tuple供給後36sample/期待vector、finally停止、unknownや非atomic観測を成功補正しない|

既必要回帰はMqPressureMetricRecorderTest8だけ、新6と同JVM14/2。collector/Root/他既成功4222/44は再演しない。Testはtools/quality/architectureの試験source、新製品実装をsrc外へ置かない。原正常六compilePG8122/input/Jar/SOURCE hashと現在Java/POMの全byteを前後照合、既Testと新Test/helperをfresh javac25/-proc:none/-Xlint:all/-Werrorでcompile、一exec append=falseへ。Production依存のSDK導入と偽認しない。

SDK15Jar/元8170原371004a7・8173原a5a2bfbe、JUnit/agent/JSR305の全現物hash。最小env/own空prometheus.config/最初classpath空prometheus.propertiesにより外部設定を読まない。SDKscrapeはメモリ内文字列化、socket/HTTP/daemon開始ではない。Snapshotは6値への独立literal/既Test固定hash/文字列/型契約で生成methodも検証、Production getterでexpectedを作らない。

PG8190元JVM/PG8192独立postへcommand/OS/JDK/sourceDomain/qualificationHead/actualExit/XML/exec/input/dependency hash、2class四100/CRC0/一session、静的適用・generated method・BUG情報を保存。Failed/skipped/notrun/flakyを合格へ算入しない。未確定時は元receiptを回収し再起動しない。PG8178のresource漏れ対策として全二Testのresource依存を先行検索し、必要resourceの閉集合を明示する（当二Testはin-memoryだけ）。正式1964-53/原190新受入0/工数null/QA051final/全actualHOLD・元/v4/v5見積不変更。
