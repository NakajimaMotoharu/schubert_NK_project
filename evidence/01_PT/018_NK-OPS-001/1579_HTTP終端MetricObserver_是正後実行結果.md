# 1579 HTTP終端MetricObserver 是正後実行結果

source `19c777bf3dbe3ddd0286d4c356a00ca8a47c99c5`、PG7136六Main/Test通常compile・classpaths取得0/PT0（UNRUN、原a6643c4e）、PG7138真正0/23PT/3suite/FES0（原1a37984d）。1577の新8 Test IDと既15は同sourceの必要回帰であり、新規23件の実装や旧source成功の算術加算ではない。BUG1654のmetadata owner失敗は固定診断を返し、HTTPTERM005で一回通知・診断literal一致を独立assert。006は実Micrometer Counter/Timer各Runtime/Error/非formatable失敗、Timer側counter1/timer0のpartialを明示し再試行0、007はordinary/fatal/同一/循環/抑制無効の全fixtureを追加して元fatal/ordinary同一性を確認した。

PG7140-micrometerではなく **PG7140-http-terminal-post-v2** のmanifest SHA256 `1e66707fc37eef6842dda56ff945635b64f0d8ce0cab6a197b0b4ac0ed4a8653`。原23XML/新source/全normal sixJar/SDK/runtime classpathを結合し、実監視9class＋metadata1・単一session/CRC差0、**L207/M42/C9/B53すべてmiss0**。全9scope executableを含め、既Web helper/全Webや全体451の100%を主張しない。実行は自己所有未起動Tomcat Request/Response/ConnectorとSimpleMeterRegistryのみ、actual network/HTTP/DB/VM/Root/鍵/配備操作0。原本・旧失敗/成功/Currentbaseline保全。

通常親Enforcer/Spotless/lint/Werror/NullAway合格、当component Checkstyle0/SpotBugs MaxLow0・Missing0。PMD7.28 raw5/exit4/processing0を抑制せず次の全行へ分類する。

| class/method/指摘 | 個別判定と根拠 | 再発防止・残リスク |
|---|---|---|
| HttpMetricContract.Route/INDEX・AvoidFieldNameMatchingMethodName | CONTEXT_NOT_APPLICABLE：既閉35literalのimmutable Map.copyOf一回factory、外部setter/可変indexなし。旧1571分類を同byteに照合。 | HTTPMETRIC002003/閉1750・unknown10000・immutable・並行。 |
| HttpMetricValve.log/RuntimeException・AvoidCatchingGenericException | CONTRACT_REQUIRED：SDKのunchecked provider故障でもowner通知を試み元故障を再throwする。NPEを正常値としてcatchしない。 | HTTPTERM006 Counter/Timer/ordinary/非formatable、部分計上は成功化0・再送0。 |
| HttpMetricValve.log/Error・同rule | CONTRACT_REQUIRED：owner信号試行後に同一fatalを保存、ErrorをHTTP成功やmetric再送へ変換しない。 | HTTPTERM006007のError/複合/循環。actual HTTP停止順は未受入。 |
| HttpMetricValve.signalFailure/RuntimeException・同rule | CONTRACT_REQUIRED：callback失敗と成功をbooleanで分離、metadata側は固定診断・provider側は元故障優先、既graph helperがfatalを検査。 | HTTPTERM005007 ordinary/同一/抑制無効/循環、旧不可視のBUG1654を再現する経路を強化。 |
| HttpMetricValve.signalFailure/Error・同rule | CONTRACT_REQUIRED：既attachSecondary/preserveFatalで元fatal・二次fatalを失わない。原文のformat/copy/logなし。 | HTTPTERM007 fatal/抑制無効、所有callback自身は当componentが資源closeしない。 |

未分類0/新suppression0/実違反を偽0化0。当分析用POMのsystem座標は元JVM classpathの全実byteへの一意aliasで、production依存変更や代替runtimeではない。正常六compile/実行/staticの四SDK pin一致。静的解析をPT代替にせず、通常23件を実行した。

BUG1652/1653/1654・YKT1405/1406/1407は実Jar/trace接続確認後に閉鎖予定。旧7130/7134source884・元7128/PT0・原4222/common44を新sourceへ流用0。正式1964/53・工数null・歴史17/別source新7/QA051final/PTALT0は不変更、実owner assembly/exporter/HTTP/native/CHR/全体451は未受入。実行command/開始終了/OS/JDK/tool/source/hash/全input/actual XML/counters/staticは原7136/7138/7140 manifestに保持する。
