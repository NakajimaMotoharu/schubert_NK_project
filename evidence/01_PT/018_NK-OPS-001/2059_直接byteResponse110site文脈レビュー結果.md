# 直接byte/response helper110site文脈レビュー結果

G03.01、群2370、開始見積り0.5/2/6pp・上限10pp、source b120eebab4bbe1f8d02c245a06e51e0783a616c5。PG10252非共有expected selectorの`h.golden`、`BackupArtifactFixture.golden`、`response`、`bytes`を含む110site/23sourceを公開sourceだけで文脈確認した。syntaxの第一引数は常にsemantic expectedとは限らず、actual先置きのassertArrayEqualsもあり、機械索引を独立性判定にしない。

|分類|source/site|確認結果|
|---|---|---|
|MediaApplicationServiceTest h.golden|1/17|MediaStageFixture.goldenがProduction MediaRequest.decodeを呼び、wireがそのheader IDだけを利用。不要なSUT前処理依存をBUG1822/YKT1573へ修正前起票。byte profile選択はTest prefix/固定表で、Production classifier使用とは区別する。|
|質問受付/worker response|3/23|QuestionSubmissionServiceTestの320byte固定QSBRSP header/payload。codeは明示0000/0200、固定offset256/282/294、Test元UUID/日時/receipt/IDを使用。Boundary/Workerは同Test helperをstatic import。Production encoderは使わない。|
|JdbcScenarioSnapshotReplacement/OutboxModel bytes|2/3|前者は29byteをTest指定byteでfill、後者は固定{1,2,3}。暗号/DB処理の再実行・資格は扱わない。|
|BackupBundlePublisher/BackupManifestPublisher|2/13|固定resource artifact-manifest.json由来。2058で既確認したhelperは再発見/新受入に算入しない。|
|Batch file/platformのbytes|9/32|DurableRecordFiles6/InspectorEnvironmentReader10/StartupLaunchRecord1/StartupPermitRecords4/BackupWorkerRequest3/CleanupFailedBackupRequest1/InspectorRunEnvironment5/InspectorStaticEnvironment1/RootStartupContext1。bytesはTest固定原文のUS_ASCII変換だけで、実fixture/環境/所有/実行の証明ではない。|
|Bootstrap bytes|4/12|FixedServiceIdentity1/MaintenanceOwnerFrame2/ReleaseApproval3/StartupProofFrame6。Test固定原文をUS_ASCII又はUTF-8変換。実actor/署名/起動/権限を検証したとはしない。|
|Web session bytes|2/10|SessionAttributeCodec5/SessionOperationTokenV2 5。Test明示JSON、独自quote・token整形と固定日時/UUID、v1入力とv2出力oracleを分離。actual側だけProduction codec。|

全体は1+3+2+2+9+4+2=23source、17+23+3+13+32+12+10=110site。件数をPT PASSや受入へ換算しない。PG10364は実索引からこれを再導出して保存する。

## 2058の軽微な追記訂正

2058の「fixture四sourceとJSON二resource」は、実manifest PG10362.companionHashesでは**fixture三source/JSON二resource**。元2058/10362を保持し、本追記で文章の内訳だけ訂正する。11対象source/65site、元SHA照合、新欠陥0/製品実行0/受入0に変更はない。

## 実施範囲

全対象11+23sourceの元PTを再演せず、実DB/Backup/鍵/Root/VM/native/graph/permit/intent等の操作0、新ハーネス0。今回の新指摘はMediaのoracle独立性一件で、製品誤動作ではない。正式1964PT/53scope、個別17/190、工数null、QA051 final、安全HOLDを維持する。次は別群の開始見積りを凍結し、三Test sourceの最小是正と許可されたstatic/正常compile/source postを行う。元実PT/coverageの未確認は未確認のまま残す。
