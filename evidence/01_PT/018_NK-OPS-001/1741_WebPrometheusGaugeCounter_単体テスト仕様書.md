# 1741 Web四Recorder 実Prometheus SDK in-memory単体テスト仕様書

NK-OPS-001/WBS-P018-09/C07/RD171 MON005010013/UI252/SS311333351/1728・1721・1702・1706、PG-D585。群1968/PG8176fresh19残81/reset1793382075、開始3/5/9pp/cap10。旧Src製造はe196d0816c8a4920696d4f601f8b4cf97e9e8b48で実装済み、今回省略するPGはなく、未検証の実SDK表現へ新規ordinary PTを追加する。元/v4/v5/実N-T/工数null維持。

## 着手前判定・source/所有

後続1739/1740は依存準備だけでtarget class init/製品PT0。実PrometheusMeterRegistryを使った当四Recorderの公開text証跡はまだ無い。PT_DEFAULT：自己所有のin-memory registry/既Codec閉型/固定数値・label/有限worker/宣言済例外だけ。socket/HTTP/DB/JMS/VM/Root/権限/配備/actualpool/sourceを使わない。SDKのscrape()は文字列化だけで、HTTP scrape/daemonとは区別する。Timer/HttpMetricRecorder/Valve/実collector/scheduler/actual owner/exposerは未受入HOLDを維持。

Production Main/既Test/POMはe196から現在まで同byteであり変更しない。PG8122正常六compileの元source e196/全Jar/入力hashを保全し、そのbyteが現在のJava/POMと一致することを当run前後に確認して使用する。新しい正常六compile成功と称さず、当測定は同Production byteに対する新しいJVM/execと新SDK input。旧114counterを合成/転用しない。新PT/helperはtools/qualityの試験source（Production sourceでない）に置き、既六Test source＋新8Testを同classpathへfresh javac25/-Xlint:all/-Werror/-proc:noneでcompileする。Src/POMへSDK依存を導入/配備したと記載しない。

SDK15Jarは8170原371004a7＋8173原a5a2bfbe、jsr3053.0.2（元M2 SHA766ad2a0783f2687962c8ad74ceecc38a28b9f72a2d085ee438b7813e928d0c7）をcompile annotation用として再利用し理由/実classpathを保存。既core1.17.1/SKD4/元Protocol176/正常内部六Jar・JUnit/agentは現物hashへ束縛、stale M2内部artifactを使わない。

## SDK初期化・設定副作用の隔離

公式tag1.7.0 PrometheusPropertiesLoaderはPropertiesを明示してもclasspath/file/system/envを先に読む。最小envだけを子JVMへ渡し、PROMETHEUS_CONFIG/IO_PROMETHEUS/JAVA_TOOL_OPTIONS/JDK_JAVA_OPTIONS等を継承しない。-Dprometheus.configは当new-only slotの空publicfileへ固定、最初のclasspath directoryに空prometheus.propertiesを置き、そのhash/byteを拘束する。実config/秘密を読まない。実collector/exporter/JMX/process binder・OpenTelemetry agentを登録せず、new PrometheusRegistryとMockClock/明示Properties/SpanContext無しだけを使用する。

公開のinclude_created_timestamps=false/exemplars_on_all_metric_types=falseを指定し、固定TEXT0.0.4で第三者trace/user識別値を混ぜない。これを本番config/全egress停止やvendor全機能合格にしない。SDKprovided/optional依存を解決済と偽装せず、対象経路の不明があれば実行前保留する。

## 独立oracleと新Test ID

四programはWebDbPoolMetricRecorder、WebOutboxMetricRecorder、MediaStreamsMetricRecorder、MediaBytesMetricRecorder。固定familyはnk_db_pool_connections/nk_outbox_rows/nk_outbox_oldest_seconds/nk_media_streams（gauge）とnk_media_bytes_total(counter)、全49sample（4＋6＋3＋36）。labelはserviceWEB/state4、storeWEB/status3、media_type=AUDIO/VIDEO/MUSIC、mode=INLINE/DOWNLOAD/RANGE、status=200/206/416/503だけ。expectedは独立literal/SS表で作りProductionの.values/getters/registriesから生成しない。formatterの順序/小数表記差を数値・閉label集合として解釈し、未知名/型/label/duplicate/余分timestamp/created等は許容しない。借用観測unknownはNaN、実0は0。

|ID|新SDK上の操作・期待値|
|---|---|
|PGPROM001|四DEBUG初期化で49sample/5family/typeと全有限label集合、13GaugeNaN/36Counter0、勝手なJVM/HTTP等追加0|
|PGPROM002|pool3/5/2/8→missing→0/0/0/1で各四text値、NaNと0を独立照合/tuple不変・2^63表現も確認|
|PGPROM003|outbox2/1/0とage7/3.5/0、missing/実0回復、六textと既tuple不変|
|PGPROM004|streams0/2/4・選択missing、36counterへ独立1..36delta/合計666、0追加不変/二MAXのdouble値・正規suffixを確認|
|PGPROM005|STANDARDは四供給後も登録/retention/sample0、SDKinstanceはcaller所有で勝手にcloseしない|
|PGPROM006|実Prometheus subclassの2件目counter登録Runtime/Errorで元identity/partial1/caller closeだけ、他owner不変|
|PGPROM007|64有限自己workerの記録/供給、counter64×7=448・finitecardinality49、非atomicな別Gauge scrape跨ぎをatomicと偽認しない|
|PGPROM008|二owner独立/1000供給後も49/固定label、禁止外部値/HTTPやTimerシリーズなし、explicit owner closeを照合|

必要既回帰は四Recorder各8=32、detailed modeの直接依存HttpMetricContractTest6＋生成閉型GeneratedWebValueContractTest4=10、計42。新8と同JVM **50/7suite**、全F/E/S/flaky/not-runを合格に算入しない。HTTP/Valve/Collector/Repositoryの未影響suiteや元4222/common44の成功確認再演はしない。

## 対象品質とエビデンス

当Main scopeは四Recorder/nested9＋直接HttpMetricContract/nested6の**実15class**。package-infoのmetadataは保持、他program/依存のcounterを合算せず全15のline/method/class/branch100、CRC不一致0/一execを独立検査する。他Web10class/全scope/whole451を受入にしない。既生成10type/36methodは当42＋新8のtyped契約へ追跡し、実Mainの除外を増やさない。空marker/他programは適用性と実byte・ownerを明示する。normalcompile/metaは履歴source原e196の同byteとして参照、新compileや現在wholebuild完了を捏造しない。

実command/OS/JDK/compiler/SDK/JUnit/agent/source-domain/qualificationHEAD/開始終端/実PID/終了・入力/expected/actual/XML/exec/coverage/静的適用/BUG/hashはPG8178以降/1742へ。元selected50の状態がunknownなら再発行せずbegin/process/exitを回収、JUnit失敗/compile/static/source不一致は修正前915/916。logは型・有限own frameのみ、Throwable message/cause/suppressedや秘密値を保存しない。全待機futureは有限、失敗を正常化しない。

正式1964PT53scope/原190新受入0/工数null/QA051final/PTALT0、root/live/source authentication/HTTP/Timer/retention/BOM/451同scope全体/CHR/nativeは未受入HOLD維持。群上限と通常継続/残10%保全を守る。

公式一次資料（2026-10-24）：Micrometer1.17.1 PrometheusMeterRegistry/PrometheusConfig、client_java1.7.0 PrometheusPropertiesLoader/ExporterProperties/PrometheusTextFormatWriter（1739/1740と参照URLを共有）。固定tag実装の設定読取/形式契約からの判断で、Production期待値をSDK実測へ追従変更しない。
