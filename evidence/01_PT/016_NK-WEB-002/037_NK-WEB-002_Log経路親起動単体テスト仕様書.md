# NK-WEB-002 Log経路親起動単体テスト仕様書

PG231。対象`WebLogApplicationRuntime.start/port/ready/terminalFailureObserved/close/closeAfterFailure`、RD MQ-003～008/AUT-002/MON-003/SYS-001、UI225/226/231/232/235、SS311/313/314/321/324/342/352。Log経路のWeb返信consumer1・Web Log再送worker・security/MVC HTTPを一つの所有者で起動する。Log検索、Login、Login context probeは同一`JmsRequestReplyClient`を受け、返信listenerもそれを参照する。`ApiSessionInvalidHandler`はsecurityと同一session repositoryを受ける。DB/JMS factory、codec、dispatcher、auditはcaller所有で親は閉じない。実API dispatcher/credential loading/broker-management readiness/実NK CHR-L01は別条件。

| Test ID | JUnit method | 事前条件・入力/操作 | 独立期待・根拠 |
|---|---|---|---|
| PT-SCR-127 | `WebLogApplicationRuntimeTest#scr127RealReplyWorkerAndSecuredLogMvcStartAndClose` | 隔離PostgreSQL18/Flyway・Artemis2.56、worker、GET `/login` | SS321のWeb返信consumer count1、Log workerとHTTP起動、UI226/QA045の固定title・HTTP200。closeでconsumer0、ready false、port再取得拒否 |
| PT-SCR-128 | `WebLogApplicationRuntimeTest#scr128InvalidReplyDlqMakesWholeRuntimeNotReady` | 起動後に合成不正TextをWeb reply Queueへ送る | SS321の恒久不正隔離、DLQ1、terminal通知1、全体ready false。業務応答は行わない |
| PT-SCR-129 | `WebLogApplicationRuntimeTest#scr129PartialStartupClosesReplyConsumer` | worker ID不正とDB transport不達を別実行 | worker起動拒否/DB readiness拒否でも先行Web返信consumerをcloseしQueue count0、HTTP bindしない |
| PT-SCR-130 | `WebLogApplicationRuntimeTest#scr130LifecycleAggregatesCloseFailuresAndReadinessBoundaries` | synthetic AutoCloseable 3件の故障、各ready predicate | HTTP→worker→replyの順に全closeを試み、二次故障をsuppressed、二重close無作用。reply/worker/terminal/closedの各not-ready境界 |
| PT-SCR-131 | `WebLogApplicationRuntimeTest#scr131StartupNullContractsAndSuppressedCleanup` | DB/JMS禁止fixtureで10依存のnull、合成cleanup故障 | 全nullをresource borrow前に拒否しDB借用0、cleanup故障2件を元の起動失敗にsuppressed、null未生成handleは無視 |

期待consumer数はSS321のWeb専用返信Queue1から、HTTP/タイトルはUI226・QA045から、停止順とterminalはSS321/342から独立算出する。production methodやencoderをexpected生成に用いない。選択commandはJava25 Maven `-pl src/schubert-nk-web -Dtest=WebLogApplicationRuntimeTest test jacoco:report`。正式commandは`sh tools/quality/030_run_pgpt_verify.sh <Run ID>`。追加class instruction/line/method/class/branch各100%、全reactor・静的0、failed/flaky/skipped/not-run0、同一source/runの全scope/hashを認定条件とする。実行日時・OS/JDK/tool・commit/branch・command・終了code・input/expected/actual・coverage・関連BUG/SSC・証跡path/hashは正式runの`evidence/manifest.json`と038を正とする。秘密値、raw token/cookie/session IDは保存しない。
