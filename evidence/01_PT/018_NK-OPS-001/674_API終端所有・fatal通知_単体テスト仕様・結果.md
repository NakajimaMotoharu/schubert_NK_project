# API終端所有・fatal通知 単体テスト仕様／結果（PG-D412）

## 限定build経過（PG1630/1631未実行PTを成功に数えない）

PG1630 source2ff5/PG1631 ac38、Production2741、共にMaven1/actual1・API PT0/全static未完null。protocolのliteralfailIfNoTests=trueで空選択を拒否、BUG1141/YKT909として旧二slot保全。CLI propertyfalseでgate緩和したとは認定せず、正式POM/全6品質は不変更。

新PG1634は依存protocol/storage/bootstrapのcompile/test-compile/test-jar/static/jarを実行（test-goal無し、PT合格非加算）、専用複製Maven repositoryへinstall後にAPIだけmandatory selected13。元cacheは全filehash照合、不変更、容量copyBytes＋10GiB保全余力を検査、追加version取得0/offline。四suite13/freshXML/FES0/static4zero/source不変が必要、empty/missing/skipped/stale/旧source/static未完を独立負例で拒否。後続1632は全JAR/Class scopeと元三依存Mainbyte同値/当API追加六・変更三を別照合する。新run未実行、保全済み失敗を合格にしない。

Program NK-OPS-001/API、RD SYS002004/OPS009/MQ008010、UI212243251253、SS311312321342343/SSC158161193194。P018-05主担当、実native終了依存N15.01は参照費0。package-only capture/Owner境界、内部callbackの結線であり、admission/argv/env/定数診断/所有順序/元期限/固定TERMINAL点は変えない。

| Test ID / class.method | 独立期待値・事前条件・操作・後条件 |
|---|---|
| PT-OPS-API-TAIL-005 / ApiTerminalCaptureTest.rem005OwnerPreservesEveryOperationIdentityAndNullInvariants | fixed owner object同一、verify→close、constructor/open null拒否、IO/Runtime/Error同objectを維持。plain JVMのcurrentJvm(null)はemptyであり、native owner認定ではない。 |
| PT-OPS-API-TAIL-006A / rem006CaptureMainEnforcesEveryBoundaryAndNeverTerminatesAfterFailure | literal argv override→native run自身70/IO0。find/open/verify1/TERMINAL/verify2/close/exitの固定順。open/verify1/capture/verify2/close各独立IO/Runtime/Errorでは同primary、exit0。verify＋close同時失敗はsecondary suppressed。stderr固定/原handler・err復元、追加Factory=null拒否。 |
| PT-OPS-API-TAIL-006B / rem006NoCaptureAndLookupFailureNeverOpenAnOwner | Factory.emptyは正常停止固定stderr/70/一回exit。lookup IOは同object/owner未取得/exit0。capture/owner fakeは実Unit/本番native証明ではない。 |
| PT-OPS-API-FATAL-BIND-001 / ApiCommittedFatalBindingTest.fatalBinding001CommittedEventStopsOwnerAndAwaitRemainsSanitizedNonSuccess | literal committed fatal event/PRIVATE_CANARY causeを同owner callbackへ渡す、stopping=true、再通知でもawait固定IOException/non-success/cause-suppressed0/health再poll0。expectedをproduction callbackから算出0。 |
| PT-OPS-API-FATAL-BIND-002 / fatalBinding002CallbackRemainsBoundToItsOwnerAndNeverReadsFailurePayload | 元ignored callbackのnull負例もfail-closed、別lifetimeは未停止。failed await拒否、別owner正常stopは正常await、追加JVM全体停止・raw causeログ0。 |

新5PT＋既API main4/lifetime4の影響13PTを同source隔離選択。残moduleはcompile/staticだけでPT合格に数えない。Main変更triggerによりこの限定成功だけでは全体認定0、次にfresh全6の3596PT/532suite/1643Main（旧3583/524/1637＋batch独立8/sixsuite＋API独立5/twosuite/newMain6）を一度実行し資格する。計数は見積りであり実XML/JAR inventoryで確認、未実行は合格0。旧4d6/1532/Root/native/coverageを新sourceへ正式流用0。

実行予定PG1630: `python3 -B tools/quality/pg1630_api_terminal_selected.py`、JDK25.0.4/Maven3.9.12/Jupiter5.13.4/Jacoco0.8.15/worker1、新target/source/fixture/coverage/cache namespace。全6の実run/command/source/日時/終了code/XML/coverage/static/hashと、source同一の署名release/実API終了条件/native/CHR/451は実行後追記する。関連BUG無し（新境界TDD）、PG-D412、群0472 .75/2/5pp凍結。工数率へのcounter/件数換算0、正式1964/53据置。
