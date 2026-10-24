# 1747 API四Counter 実Prometheus SDK 単体テスト仕様書

2026-10-24 BUG1691/YKT1442是正：元e196/PG8206は40中7失敗・終了1で保持、PG8207原60bdfffeが単位指定によるnk_mq_messages_total_messages_total変形を実証。PG-D589の最小修正source6246c954d6d0ac7171bf009663bb2e6539d8be32ではMQ CounterのbaseUnitのみ除去、MQEVENT001の内部metadataを未指定へ訂正した。外部正名/type/label/増分と新APICNT oracleは不変更。次PG8212当sourceの正常六compile/NullAway/PT0→新PG8214当40/5→8216独立6四100/static→8218全physical/traceと1748。旧e196正常compile/counter成功を当sourceへ流用しない。元群開始1/3/6/cap10は維持し、追加発見/修正・再認証を分離する。

NK-OPS-001/WBS-P018-09/C07/RD171 MON005010013/UI252/SS321323351、1643/1691/1695/1718、PG-D588。group1974/PG8204fresh20残80/reset1793382075、開始1/3/6pp/cap10。既Simpleと後続索引/current sourceを照合し、実backend未検証だけを追加する。

四対象はInboxReplayMetricRecorder、OperationMismatchMetricRecorder＋Operation、MqRedeliveryMetricRecorder、MqMessageMetricRecorder＋Stage＝実6Main。四family/801sample（Inbox64×12=768、operation8、queue6×delivery3=18、一固定layout/addressのMQstage7）。新APICNT001～008＋必要既四Test各8=40/5、一execで当6のline/method/class/branch100・CRC0/session1、生成二enum四factorymethodも同runtyped契約に結合。業務Inbox/再送/認可/鍵/発行権限を操作する試験でなく、own memoryへの供給済event観測のみ。

|ID|固定独立oracle|
|---|---|
|APICNT001|四TYPE counter/全801sample/SS321323351閉label集合・初期全0、_total名はSS351そのまま|
|APICNT002|独立SS323表の64layout×SS351の12resultへ各1回供給、各768は1/他family0|
|APICNT003|operation固定8値へ1..8回、個別値1..8/合計36、token実体は使わない|
|APICNT004|全六queueでinitial1は増分0、delivery2/3/4は各1・計18、実再送/時刻制御なし|
|APICNT005|一WLGEVT01/nk.web.log namespaceの七stageへ1..7、direction/outcomeと個別値/合計28|
|APICNT006|STANDARD全供給後もcounter/series/registry0・caller close0|
|APICNT007|64有限own workerで四固定seriesへ各64、二owner独立・cardinality801/finally停止|
|APICNT008|全8Operationのtyped factory/unknown/null/defensive array・borrowed lifetime、生成Stageは同run既mqEvent003|

expectedは固定literalのSS表/counter名/label/valueで、Production Registry/parse/values/getterから生成しない。入力のtyped enum化は期待値生成と区別する。固定catalog全64は既独立TestのSS323転記から同じliteralを再掲、実raw電文・credential・token・Throwable graph無し。実SDK Counter名のbaseUnit/_total変換も仕様名に対して検証し、実測に期待値を合わせない。

Test/fixture/helperは工具試験source、既Production Main/POMはe196d0816c8a4920696d4f601f8b4cf97e9e8b48同byte。元8122正常六compile/input/Jar/現在byteを前後束縛してfresh javac25/-Xlint:all/-Werror/-proc:none。一slot/一JVM/一exec、SDK15/JUnit/agent/annotation全hash、最小env/ownemptyfile/最初classpath空resource。全五Testの追加resource依存0を先行検索。actual parserのlabel文法へ仕様の数字/underscoreを追加するがexpected全Key集合を弱めない。

PG8206元40/5→PG8208独立6四counter/static/source/生成→1748、unknown時は元job回収・再起動禁止。失敗は既Main仕様違反なら修正前915/916、oracle/SS改変で回避しない。元4222/44や無関係全APIの確認再演0、Failed/skipped/notrun/flakyは合格へ算入しない。

実JMS/DB/Root/VM/intent/permit/配置/サービス/権限/秘密/拒否未特定操作はHOLD、ネットワーク呼出し無し。正式1964-53/原190新受入0/工数null/QA051final/PTALT0/原-v4-v5/共有上限・停止条件不変更。
