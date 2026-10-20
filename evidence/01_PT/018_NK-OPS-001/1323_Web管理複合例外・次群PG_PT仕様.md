# 1323 Web管理複合例外・次群PG/PT仕様（未着手source）

1320～1322/BUG1561/YKT1318の横展開。現Production551/元PG6212全体はMain/Test固定を維持し、真正終端・原資格確認後だけ次群を製造する。現在は仕様・工具定義準備だけでWeb修正済/PT成功とはしない。別source成功流用/旧全体再発行0。

対象Program NK-WEB-002/NK-OPS-001、WebManagementServer.open四引数。RD SYS-002/004/MON-005、UI212/243/253、SS342316317/354・411例外/redaction。既openはcomponent entry、実nativeは既bind→捕捉→start経路のまま。既Web READY003のchecked IOException cleanup suppressed契約は維持し、unchecked cleanupだけを補完する内部PG（上位業務/画面/電文/権限/期限変更0）。APIの固定ISEをそのままWebへ転記しない。

PG方針：固定IOException診断をbind前に準備、startup RTE/Error後のcloseでは既IOException処理を残す。追加RTE/Error secondaryは、primary非Errorかつsecondary Errorならそのfatal secondaryを維持し、他は元primary維持。同一Throwableへのsuppression0、distinct secondaryを公開する場合もraw cause/messageを付けず事前の固定IOExceptionだけとする。固定文言は既Web management stop unconfirmed、compile-time constantで重複定義しない。nativeのUNKNOWN保持/親30分・既Unit期限に変更なし。

新Test ID PT-WEB-READY007、WebManagementServerTest.ready007CompoundStartupCleanupKeepsPrimaryAndFixedDiagnostic（予定）。既同Test class内へ一つ追加、八入力を一JUnitへ内包し8PTへ加点しない。primary={IllegalStateException,AssertionError}、secondary={なし,別IllegalStateException,別AssertionError,primaryと同一instance}。自分のprepared管理executorを受け取る未接続HttpServer fixtureでsetExecutor時にprimaryをthrow、stopはcount一回/所定secondaryをthrow又はreturn。実socket/VM/Root/DB/鍵/業務配備には接続せず、fixture finallyで捕捉した自前executorだけshutdown/実joinする。

独立期待値表：

| primary | secondary | actualとして要求するidentity | suppressed |
|---|---|---|---|
| RTE | なし | primary | 1、既未start契約の固定IOException |
| Error | なし | primary | 1、既未start契約の固定IOException |
| RTE | 別RTE | primary | 1、固定IOException/原因なし/raw secondaryとは別物 |
| Error | 別RTE | primary | 同上 |
| RTE | 別Error | secondary | primary側0（fatalを非fatalへ降格しない） |
| Error | 別Error | primary | 1、固定IOException/原因なし |
| RTE | 同一primary | primary | 0（self suppression禁止） |
| Error | 同一primary | primary | 0 |

期待値は上表/元SS契約から固定し、Productionを呼んでexpectedを生成しない。setup/stop countは各1、fixture executor actual terminationは必須、fixtureの例外を正常closeや実native成功へ変換しない。既READY003のactual HTTP/uncooperative callback/checked cleanup、全Web正常HTTP/境界/null/並行とAPI比較Testを合わせて検証する。正常start/未startの違いは既317を維持する。

同じkeeper接続経路の可読性PGとしてServiceProcessResources.waitUnknownIntervalのwhile条件内assignment（raw AssignmentInOperand一件）を、loop内の明示left計算→期限判定→同一park/IRQ再確認へ整理する予定。1e9ns/monotonic/pre IRQ/途中IRQ/非正常return/再close禁止は不変更。既独立診断/tick/fallback/IRQ Testで検証し、code都合でoracleを変更しない。

次sourceの宣言予定は選択64/20（元63＋同class一@Test）・全4028/605/1667であり、実source inventoryが一致するまで確定数/PASSではない。元6212 genuine0/原全XML六Jar資格→Main二/Test一をまとめて製造・正規format→commit/push固定→new-only選択全六gate→当原資格/PG/JVM→必要全体一回の順。source追加変更が必要なら開始見積/差分/依存を追記、旧成功の加算をしない。

PTPRE041/PT_DEFAULT：通常の自前有限fixture、固定class/method/権限・副作用を上記へ限定。プラットフォーム拒否範囲を探る実行ではない。実Root/VM/current/cohort/intent/permit等HOLDに依存する安全確認を代替しない。未確定な三consumer ordinary retry catch六spanは別に未判定保持し、このPGで解決済へ混ぜない。
