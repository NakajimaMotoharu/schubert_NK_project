# 2833 Web pool・Context三whole56仕様

P01809/source6b53/normal14216、着手見積2/6/10pp/cap10。原三whole56全1624 Test行（Recorder289/Binding489/Context846）、Main Recorder/Binding/Context183とObservation/Collector・StandardSource/Payload等の必要body/initializer、Fixture getter実装を読了。既1367にsuite/完全Source非重複・全6owner candidateを照合、NORMAL_PT。

|原whole/TestID|件数|独立期待値・観点|
|---|---:|---|
|WebDbPoolMetricRecorderTest/WEBPOOLMET001～008|8|閉4系列/WEBタグ/state factories、固定3/5/2/8・IEEE2^63/immutable record hash94248、missingNaN≠true0、STANDARD非保持・null/未知/負/最大、並行64/独立owner・部分登録失敗とborrowed lifetime|
|WebDbPoolMetricBindingTest/WEBPOOLB001～015|15|偽getter active/idle/pending/max一回順、最大2147483647・未知→回復・各getter失敗同一性/再送0、constructor非sample、STANDARD getter0・deferred supplier順/各null/throw・owner捕捉前acquire0、Context render時だけrefresh・own worker二refresh直列化|
|WebMetricContextTest/WEBMCTX001～033|33|resource-free constructor・STANDARD factories/setup/refresh0、default自己SDKと7.5→9.5→11.5 golden、single initialize/partial owner/各null/runtime/error、標準→custom close順、close失敗未確認・競合/reentrant stopで新access拒否/初期化各phase stop、明示再renderだけ回復、30秒以内latchとfinally解放|

HikariPoolMXBean/HikariConfigMXBeanは既読WebDbPoolMetricObservationTest.FixtureのProxyでgetActive/getIdle/getThreadsAwaiting/getMaximumPoolSize以外をAssertionError、JMX lookup/接続/credential getter/設定制御/close0。外部VM/DB/サービス/Root/鍵/Graph/cohort操作0。Context defaultの標準SDKは当所有child JVM内だけを観測し、GC→standard registry→customの正規closeを維持、強制GC/OOM/dump/attach0。元Observation TestはFixtureのcompile-only依存、旧8methodを選択/再演/加算しない。

全三Source/五Code closure（Recorder/Counts/State、Binding、Context）を当new exec/session/CRCで測定。自然B0があれば実非空LMC100/N/Aと四100を区別、未達は未達で保存し、manual除外/旧exec合算0・公式record/enum filter不変更。独立期待値はSS351/311/342の固定field/domain・呼出し数/順序/明示状態とliteral wire、Production methodでexpected生成0。供給readyは真正readiness/外部所有の証明にはしない。

fresh javac proc:none/Werror/JDK25.0.4/JUnit/JaCoCo0.8.15、empty Prometheus config固定、親child180秒。原Main/Test/依存Jar/pinはnormal14216で一致を前後検査。checked entry pg15060_web_pool_context_fifty_six_pt.py、元ENV/command/時刻/exit/全pin/XML/exec・counter/独立反例・ownerを2834/15060～64へ保存。原本/Currentbaseline/stash7/二held/既成功失敗、正式1964-53/17-190/工数null/QA051final/451-F03-G07/全HOLD保持。
