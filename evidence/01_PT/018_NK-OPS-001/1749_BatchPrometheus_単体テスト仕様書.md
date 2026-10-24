# 1749 Batch供給metric 実Prometheus SDK 単体テスト仕様書

NK-OPS-001/WBS-P018-09/C07/RD171 MON005010013/UI252/SS341351、1611/1615/1708/1710・PG-D590。group1976/PG8224fresh21残79/reset1793382075、開始1/3/6pp/cap10。後続索引/現code/既Simple試験を確認し、Batch四Recorderの実backend未検証を補完する。

対象はTransferMetricRecorder/nested4、IntegrityFailureMetricRecorder/nested2、BatchMetricRecorder1、ProcessRestartMetricRecorder/nested2、および直接BatchMetricContract/nested3、計実12class。六family/108sample（transfer4、integrity30、batch runs40/lastsuccess10、restart24）。他policy/catalog/AlertLifecycle.Service/既BatchStepは別program依存、当counterへ合算せずbyte・既契約を参照する。新BATCHPROM8＋必要既四Test各8=32＋共有fixtureを持つBatchMetricContractTest5=45/6suite、fresh Testcompile/一JVM/exec。直接contractを単にnot-runで済ませず必要5も実行する。

|ID|独立fixture/oracle|
|---|---|
|BATCHPROM001|六family/type/全108閉label集合、14Gauge NaN・94Counter0|
|BATCHPROM002|transfer.part3file/11byte・.ready5/13、zero/missing/MAXの数値を個別比較、実fileなし|
|BATCHPROM003|HASH/PATH/CONFIG×十stepへ供給1、30counter各1、実hash/修復なし|
|BATCHPROM004|十step×四terminal各1、各SUCCESS時刻7.5秒、非SUCCESS/古いSUCCESSでは時刻不変、µsと0001/9999境界|
|BATCHPROM005|六service×四reason各1、24counter各1、UNKNOWNは供給された原因不明、実再起動なし|
|BATCHPROM006|STANDARD全供給/missing後も登録/retention/text0、caller close0|
|BATCHPROM007|64有限own workerの供給で三counter対象各64/known Gauge、二owner独立・cardinality108/finally停止|
|BATCHPROM008|Transfer.Countsの全component/self/null/other/固定hash104/文字列、Suffix/Step/Status全typed factory/clone/null/unknown|

期待name/label/step/status/service/reasonはSS literal、値は固定整数/UTC epochとして独立作成。Product methodからexpectedを生成せず、実Instant変換をexpectedへ流用しない。生成六type/15methodは四counterへ加算せず、同runBATCHPROM008と既integrityMetric003/restartMetric003へ結合する。全record/enumは削除/到達不能扱いをしない。

製品source6246c954d6d0ac7171bf009663bb2e6539d8be32同byte、元正常六compile8212全input/Jar/現在を前後束縛。SDK15/JUnit/agent/annotation全byte、最小env・own空config/最初classpath空resource、NoBinder。別packageの純TestfixtureはBatch tools namespaceへ置きAPI artifactへ依存しない。追加fixture resource0/全Test依存を先行検索、旧4222/44確認再演0。通常java25.0.4/-Xlint:all/-Werror/-proc:none・formatter1.36.1、PG8226→8228実12四100/CRC0/一session/static/generated→1750へ。

静的は当5Main/12classの実PMD/CS/SB/processing/missingを保存。BatchMetricRecorder private lockの既PMD raw1は隠さず、PG7816/7824の元raw/位置/同source byteと個別理由を厳密再結合し、未知指摘は拒否。raw1を0指摘と称さず、抑制/ルール除外で消さない。失敗・未実行・flakyはPASSに算入しない。

実Backup/DB/filewalk/削除/再起動/VM/Root/service/intent/permit/鍵・拒否未特定操作HOLD。供給時刻やstatusを真正完了/実成功の権限へ読み替えない。正式1964-53/原190新受入0/工数null/QA051final/PTALT0/原-v4-v5・停止条件不変更。
