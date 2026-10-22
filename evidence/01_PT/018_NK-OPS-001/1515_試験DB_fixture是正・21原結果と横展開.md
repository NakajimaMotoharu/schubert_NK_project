# 試験DB fixture是正・21原結果と横展開

1513/1514/PG-D514・BUG1633/YKT1386、F02開始枠.4/1.2/3pp不変。修正commit e7d64fda2453e906ee6ccc5fe718e5c29841e4aa。BatchDatabaseFixture/ApiLogDatabaseFixtureだけknown-start0後のsetupへcatch/当fixture stop/元Throwable再送を追加。close異常はsuppressed（自己同一抑止）、割込は再設定。開始結果未確認/既存/未所有clusterへ停止を広げない。Production Main/旧Test期待値/新red Test bytes/Current/gates不変更。内部Test基盤依存でSS変更不要。

## 同oracleのgreen

command=full PYTHONPATH下 python3 -B tools/quality/pg6922_db_fixture_selected.py green。新only pg6924-db-fixture-green-v1/session13629、09:59:02.049105～10:02:06.513483 UTC、184.464378秒。元Maven/三phase全部0、実21件10suite、失敗/スキップ/flaky/notRun0、六module静的0。archive f1b6979b01ee41483a2b8390d5ac426eff2aeb1edf02e9f56bcb59f9b4344dd6。observer終了を元結果と混同せず、元manifest真正0を確認。

read-green/session90593は元XML/全851Main・1669物理Main差0/実21/10/raw静的1409/CS0を独立照合し終了0。公開 `evidence/provisional/PG6928-db-fixture-green-original-v1/manifest.json` SHA256=7a60d8e3ebf2acad4bc4f80bf24a38ba2272c77b07e9e79f1b03ff59d083035c、私有元資格manifest dd519cef67ba5d4bfe38d142b06ccb07f3df1c79849bc938ff283638996d17fe。実行済み21は新6＋旧Web3＋guard12。Production対象counter無し=空/nullであり100%ではない。

redの新六methodを一byteも変更せず、両SQLSTATE22012/元例外suppressed0と、constructor退出時のpostmaster.pid不存在が成功。元green XMLはA SHA256=3d6cec11531fcf972fde470979119f3d68c5df2fe8301e933040178cd075d4c0、B=472c4ab166f94ffcc6cf4e95d0b41119981e1601db7b05dbfb10b0f149849a85。各safe markerはownedResidualStop=false。redのtrueと異なりfinallyが残存DBを停止した成功ではなく、constructor自身の停止を実証。null/empty/blankは外部owner0、正常24表/所定roleと明示stopも両方PASS。旧失敗は1514/6926へ保持、取り消さない。

## YKT1386全六targetの適用性

|target|修正・確認と非該当根拠|
|---|---|
|BatchDatabaseFixture|是正e7d64、独立B01～03・green実三PASS・red失敗原本保持|
|ApiLogDatabaseFixture|同上A01～03、bootstrap三PASS|
|WebLogDatabaseFixture|旧BUG552で同型known-start後catch/stop済み。既WebLogDatabaseFixtureTest三件を当sourceで再試験PASS、新しい一括変更無し|
|DatabaseMigrationTest|api/database、static dataDirectoryをBeforeAllのstart前96行で公開、AfterAll135～137で当path PID存在時だけstop。constructor未公開ownerの不具合とは非該当|
|JdbcInboxCoordinatorTest|api/idempotency、BeforeAll71～73でstatic owner公開、AfterAll122～124で同path限定stop。同じ非該当根拠|
|OutboxDispatcherTest|api/messaging/outbound、BeforeAll87～88でstatic owner公開、AfterAll137～139で同path限定stop。同じ非該当根拠|

最後三classのJupiter5.13.4 lifecycleをローカル実依存のjavap -c -p ClassBasedTestDescriptorで確認：beforeはbeforeAllMethodsExecuted(true)をinvokeBeforeAllMethodsより前に立て、afterは同flagでinvokeAfterAllMethodsを呼ぶ。単なる検索だけで非該当としない。engine JAR SHA256=027404a92fe618b72465792a257951495c503a7d5751e2791e0f51c87f67f5bc、POM固定5.13.4・読取終了0。これは静的適用性であり、三classのsetup故障を動的実施したとの主張ではない。通常全suiteは次の必要全体で当source確認する。

BUG1634/YKT1387（reader corpus）は65f439706へ修正保存、管理五/pyflakes0・元二job全archive/8511669照合97db1cbbで工具scope再検証済み。初回exit1/manifest無しを維持、PT加点0。

正式1964/53、canonical17/190、工数null、QA051final、PTALT代替完了0は不変。実配備/VM/Root/cohort/原本DBBackup/鍵/permit/native操作0。BUG1633/YKT1386は新依存全体回帰の後までOPEN、選択21の合格を全体合格へ変換しない。次1516の必要束全体と同source品質/trace、通常小群で停止しない。
