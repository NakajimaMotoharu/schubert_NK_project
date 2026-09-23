# NK-WEB-002 MVC依存登録単体テスト仕様書

PG227、対象`WebHttpServer.start/checkedDependencies`・`WebApplication.start`。RD SYS-001/006・MQ-001/004、UI225/226、SS311/313/314/321/342。feature Controllerへcaller所有JMS/認証portを同一インスタンスで渡す。起動前に型/nullを検査し、immutable snapshotをTomcat/MVCへ登録する。独立fixtureはloopback Tomcat11、合成`InjectedPort("PG227-PORT")`、Spring `@Bean` Controller。秘密値/DB dumpは使用しない。

| Test ID | Program/class/method | 入力・操作と独立期待 |
|---|---|---|
| PT-SCR-120 | `WebHttpServerTest#scr120CallerOwnedPortReachesRealFeatureController` | caller-owned portとfeature configurationで実HTTP `GET /pt-port`。固定fixture文字列がHTTP bodyへそのまま出て200、Springは別portを生成しない |
| PT-SCR-121 | `WebHttpServerTest#scr121InvalidPortRegistrationFailsBeforeTomcatCreation` | map/key/value null・型不一致。NPE/IAE、Tomcat factory呼出0 |
| PT-SCR-122 | `WebApplicationTest#scr122InvalidMvcDependencyStopsBeforeDatabaseBorrow` | 誤型port登録、DB/JMS呼出禁止proxy。IAE、DB/JMS borrow0、HTTP bind0 |
| PT-SCR-123 | `WebHttpServerTest#scr123LegacyFactoryOverloadReturnsStartedServer` | 既存factory overloadから実Tomcat起動。HTTP `GET /login`は200、旧起動口の成功戻りを保持 |

期待値は固定fixture文字列、UI226のLogin status、SS311/342の起動順から独立算出する。選択commandはJava25/Maven `-pl src/schubert-nk-web -Dtest=WebHttpServerTest,WebApplicationTest clean test jacoco:report`。正式commandは`sh tools/quality/030_run_pgpt_verify.sh <Run ID>`。全4 Test ID成功、failed/error/skipped/flaky/not-run0、Java全moduleのinstruction/line/method/class/branch100%、静的0、同一source/runの全証跡・hashを認定条件とする。日時/OS/JDK/command/commit/coverage/期待・実際/関連障害/証跡hashは`evidence/manifest.json`・034を参照。実NK CHR-L01、Web reply/Log worker親起動は別未完了条件。
