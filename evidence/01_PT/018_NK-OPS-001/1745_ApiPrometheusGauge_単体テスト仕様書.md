# 1745 API四Gauge 実Prometheus SDK 単体テスト仕様書

NK-OPS-001/WBS-P018-09/C07/RD171 MON005010013/UI252/SS324331342351、1623/1635/1647/1660/PG-D587。group1972/PG8196fresh20残80/reset1793382075、開始1/3/6pp/cap10。後続索引と現codeを確認し、API四Recorderの実Prometheus表現未検証を新8IDで補完する。Web/MQ SDK成功をAPIの成功へ転用しない。

対象はOutboxRowsMetricRecorder/nested3、OutboxAgeMetricRecorder/nested2、AsyncJobMetricRecorder/nested3、DbPoolMetricRecorder/nested3の実11class。四familyのsample15（rows3＋age3＋jobs5＋pool4）、固定store/service=API、三status/五state/四pool state。新APIPROM001～008＋必要既四Test各8=32＋共有GeneratedMetricValueContractTest8=48/6suite。共有生成TestのOperation enum1件は共用suite内の依存確認で新成果/対象Mainに数えない。生成六type/25methodは新counterへ合算せず、同run独立typed契約に結合する。

|ID|fixture/期待値（Productionからexpected生成禁止）|
|---|---|
|APIPROM001|DEBUG初期四family全15sample/label閉集合、全NaN|
|APIPROM002|rows3/5/2・storeAPI、別family不変更|
|APIPROM003|age7/3.5/1ns、実zero/fullDuration.MAXの秒変換をliteral比較|
|APIPROM004|jobs RECEIVED11/PROCESSING23/COMPLETED37/ERROR41/CANCELLED53、固定五state|
|APIPROM005|pool3/5/2/8→実0/0/0/1、Long.MAX_VALUE表現・serviceAPI|
|APIPROM006|四family missingでNaN/別ownerと保持済tuple不変更|
|APIPROM007|STANDARD四供給/missing後も登録/retention/text0、caller所有close0|
|APIPROM008|64有限workers・1000供給後も15sample/二owner独立・同vector、finally停止|

Test/helper/共通fixtureはtools/quality/architectureの試験source。製品PGをsrc外に置かず、既製品Main/POMはe196d0816c8a4920696d4f601f8b4cf97e9e8b48同byte維持。元正常六compile8122/input/Jarと現在を前後照合し、既五Test＋新Test/fixture/launcherをfresh javac25/-Werror/-Xlint:all/-proc:none。SDK15Jar/元8170・8173/normalexternals/JUnit/agent/annotationは全hash束縛。共通runnerは自前slot、最小env/ownemptyconfig/最初classpath空resource。全Testを先行検索し、追加test resource無し（in-memory fixtureのみ）を固定する。

PG8198の真正48XML/exec/終了、PG8200独立11四100/CRC0/一session/生成metadata/静的scopeと全入力hashを1746へ。PMD/Checkstyle/SpotBugsは当4Main/11classで実行、処理/欠落とraw全件を保持し未分類を0へしない。Failed/skipped/aborted/notrun/flakyは合格へ算入しない。unknownslotは再起動しない。元4222/44や無関係wholeAPI確認再演0、製品変更なしを新正常compileと偽認0。

禁止・未受入=実DB/SQL/worker/pool/dispatcher/JMS/VM/Root/業務処理/権限/secret/socket/service等。SDKscrapeはメモリ文字列化で実endpointではない。formal1964-53/原190新受入0/工数null/QA051final/PTALT0/元-v4-v5・全actualHOLD維持。
