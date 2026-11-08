# 3951 API供給記録原24 有限owner仕様

G03.05主/P01809関連、REWORK開始前1/4/8pp cap10。既23952 syntax metadataは7415site/receiver型未確定、factory呼出は索引scope外で0を実executor不存在と解釈しない。API監視のresult.get候補から実source全912行/三Main全body/必要BrokerTopology全文を読み、invokeAll戻りFutureと実pool所有を確認した三原whole8ずつ24を対象。metadata名前だけでFuture/障害と認定0。canonical三Source owner/costOwnerは現23972でWBS-P018-09を確認、変更ownerと混同しない。

BUG2587を915へ修正前起票後、AsyncGauge007/OpMis007の複合registry+executor TWRをregistry内側単一finally.shutdownNow-await10へ、MQRedel007の内側pool TWRはstandalone単一finally10へ。三invokeAllは10秒、戻り終端Future.getの原body保持。三Source構造を区別して元24body/literal/fixture/レジストリ逆順/並行64を厳密逆復元、GJF後literal変化を先行観測する。

|原whole/Test ID|件数|独立期待/正常・境界・null・例外・並行|
|---|---:|---|
|AsyncJobMetricRecorderTest/ASYNCGAUGE001..008|8|固定5state/5gauge、1+2+3+4+5=15・入力変異後不変、NaN≠0/回復・STANDARD0、欠落各state/nullkey/nullvalue/負値拒否・LongMAX/overflow/固定double丸め、64入力二cohort同一性、partial登録2/残1/同例外/borrowed所有|
|MqRedeliveryMetricRecorderTest/MQREDEL001..008|8|SS321固定6queue×delivery2/3/4=18counter、初回1計数0・一巡18+1=19、STD0・MIN/-1/0/5/MAX/null拒否、partial登録/増分前後故障0/1・再試行/補償/文字化0、64同pair/別owner1・foreign gauge7保持|
|OperationMismatchMetricRecorderTest/OPMIS001..008|8|固定8operation/8counter、全各1+追加=9、STD0/null/unknown/alias拒否、provider同一性・partial2/残1・増分前後0/1、64/8=各8・別owner1000/1非共有|

NORMAL_PT: SimpleMeterRegistry所有・Async MockClock、他SDK内部通常Clockだけ、既core/commons/observation1.17.1三JarとJSpecify/Console、現normal api+protocol二Jarのみ。queue文字列enum/BrokerTopologyはJMS無し値catalog、Operation enumはtoken/HMAC/key/認証へ解決0。実Async worker/DB/MQ/JMS/再配送/待機backoff/OS収集/Root/VM/FFM/鍵/外部I/O0。synthetic OOMEは通常例外objectのみで実OOM誘発0。旧標準自己JVM37/73とは別scope、SDK/APIJar profileを実normal keyで固定して旧batchJarを転用しない。

対象完全Main3Source6physical Code（Async3/MQ1/Operation2）、protocol helper1は部分実行で新資格0。既Core/Main7aed/Static22086を同byteだけ再利用し全Main再compile/不要全回帰0、元24一JVM/一exec/一sourceで一回再試験。独立SS351 kind/key/state/purposeとSS321 queue、数値/同一性/exception oracle、source/XML/actualexit/全Source/class/hash/CRC/静的分類/held四initを照合、自然B0=N-A/未達を正直に保持。旧generated補足3017/18・旧8等成功を確認再演/coverage合算0。新unique/leaf/正式1964-53/工数null・全HOLD不変。PG25278/80/82/84/86/88と3952へ環境/command/対象commit/結果/hashを記録。
