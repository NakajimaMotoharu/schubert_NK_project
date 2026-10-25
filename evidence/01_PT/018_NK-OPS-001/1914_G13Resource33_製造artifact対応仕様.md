# G13.07・Main CP参照なし33 sourceの製造artifact担当対応

2026-10-25 14:22 JST、G13_RESOURCE33_SOURCE_OWNERS_V1/source64446不変更、開始.5/2/5pp/cap10。fresh66残34/reset1793382075（05:20:43UTC）、現在窓残10以下/取得不能で保全。旧累計停止なし。

残256のうちMain CPなし51から、製造artifactを明示できる33 sourceだけを扱う。SQL16、systemd6、PostgreSQL設定1、Artemis設定3、運用script1、Maven依存2、JavaScript4。汎用JDBC/実fixture所有等18は今回未割当のまま。resource/Main/実行所有は別であり、sourceを読むだけでSQL/broker/service/JS/DBの試験合格やPT免除を作らない。

表のsourceは各module `src/test/java/dev/codex/schubert/nk/`以下。primary/cost候補は原485の製造artifact owner、Maven二つのみ481 F02「JDK/Maven/toolchain・6module build・依存境界」の明示scope。F01は規約/方針なのでbuild担当へ誤用しない。

|module/source|primary/cost|製造artifact証拠|
|---|---|---|
|api/api/database/DatabaseMigrationTest|WBS-P004-01|migration全28/roles SQL|
|api/api/database/MigrationInventory|WBS-P004-01|SS331/DB258の独立expected catalogとmigration全28|
|api/api/database/NotificationStateMigrationTest|WBS-P004-01|V024 notification state|
|api/api/database/QuestionDlqMigrationTest|WBS-P004-01|V025 question DLQ metadata|
|api/api/database/StartupSchemaProjectionTest|WBS-P004-01|V023 schema history projection|
|api/api/logging/MessageStoreCleanupTest|WBS-P004-01|V006 cleanup bounds/retention|
|api/api/maintenance/BackupRerunBoundaryTest|WBS-P004-01|V017 backup rerun history|
|api/api/maintenance/CleanupSafetyBoundaryTest|WBS-P004-01|V013 backup/retention guards|
|api/api/maintenance/InboxInspectionProgressBoundaryTest|WBS-P004-01|V012 durable inbox progress|
|api/api/maintenance/InboxMaintenanceBoundaryTest|WBS-P004-01|V010 full inbox scan/deletion|
|api/api/maintenance/InspectionParentBoundaryTest|WBS-P004-01|V019 inspection summary|
|api/api/maintenance/LogCleanupProgressBoundaryTest|WBS-P004-01|V014 log cleanup progress|
|api/api/maintenance/OutboxCleanupBoundaryTest|WBS-P004-01|V011 outbox only cleanup|
|api/api/maintenance/RunReferenceBoundaryTest|WBS-P004-01|V018 maintenance run references|
|api/api/maintenance/StepCleanupBoundaryTest|WBS-P004-01|V020 atomic cleanup step counts|
|batch/batch/repository/SuccessProgressSealTest|WBS-P004-01|V028 retained success progress seals|
|api/api/database/PostgresDeploymentTest|WBS-C03|postgresql.conf/pg_hba.conf templates|
|api/api/maintenance/ApplicationServiceUnitTest|WBS-C02|API/Web Unit templates|
|api/api/maintenance/UnitSyntaxFixture|WBS-C02|全C02 Unitのsyntax-only補助|
|batch/batch/platform/ArtemisServiceUnitTest|WBS-C02|artemis.service|
|batch/batch/platform/CleanupServiceUnitTest|WBS-C02|cleanup.service.template|
|batch/batch/platform/MorningServiceUnitTest|WBS-C02|morning-controller/target templates|
|batch/batch/platform/RootServiceUnitTest|WBS-C02|API/Web UnitのRoot入口|
|api/api/maintenance/InspectorDeploymentTest|WBS-C08|inbox-inspector.sh.template（関連Unit C02/env C06）|
|api/api/messaging/config/ArtemisBrokerConfigurationTest|WBS-C04|broker.xml|
|api/api/messaging/config/ArtemisSecurityTest|WBS-C04|broker.xml ACL、実broker未操作|
|batch/batch/mq/ArtemisExpiryManagementAuthorizationTest|WBS-C04|broker.xml Expiry role、実broker未操作|
|batch/batch/bootstrap/BatchRuntimeDependencyTest|WBS-F02|batch/pom.xml runtime JDBC依存|
|web/web/bootstrap/WebRuntimeDependencyTest|WBS-F02|web/pom.xml runtime JDBC依存|
|web/web/view/LogSearchScriptTest|WBS-P016-25|log-search-validation.js|
|web/web/view/OperationPostScriptTest|WBS-P016-25|operation-post-submit.js|
|web/web/view/QuestionInputScriptTest|WBS-P016-25|question-input-validation.js|
|web/web/view/ScenarioSearchScriptTest|WBS-P016-25|search-speaker-submit.js|

上記はprimary責任を示すreview済みartifact witness集合であり、Testの全依存resourceを網羅したと主張しない。SQLの業務的関連責務も消したと扱わず、原WBS/原Program PTへの既traceを保持する。共有SQL/JS/Unitの費用を利用側へ重複配賦せず、作業費はG13.07一回のみ。

元9386v3未登録/zeroMain51、9402/9414現register、原485/481、正常9246 input hashを固定。各source/証拠resourceのcurrent/snapshot/正常input hash一致と原resource ownerを照合し、別JDKでTest class SourceFile/CPを静的確認。Mavenだけ既F02 scopeとactual POMのJDBC runtime宣言をsourceとして確認する。sourceからSQL/ProcessBuilder/Node/Artemis/JUnit/VM/DB/service/鍵/native/権限操作を一切実行しない。raw fixture/秘密情報を保存せずhash/path/宣言metadataのみ。

独立literal table/wholepath選択、誤resource owner・source差替え・hash・cost単field・関連/保留捏造・受入偽装・隣接/既owner優先を反証し、根拠が揃ったsourceだけ登録。見込1533→1566/1789/Test568→601/824・残256→223・限定708→741だが検証後だけ計上。原941943/481484/予算/受入/正式1964-53/17-190/工数null/QA051final/全actualHOLD/全WBS scope guardHOLDを維持し、通常群/commit/報告/PMO返答待ちで終了せず継続する。
