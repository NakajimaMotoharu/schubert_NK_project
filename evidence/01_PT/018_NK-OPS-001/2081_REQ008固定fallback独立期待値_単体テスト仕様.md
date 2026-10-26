# 2081 REQ008固定fallback独立期待値 単体テスト仕様

Program NK-WEB-001、WebRequestTraceTest#req008OutOfOrderNestedCloseCannotPublishAClosedTrace、既REQ008。source主責/cost主責は元registry10512のWBS-P006-03を保持、変更目的G03.01参照追加予算0。群開始1/3/7pp、cap10、BUG1841/YKT1592。RD MON/AUT、UI235/252、SS312 §4.21（origin/main8b91944dfの295行：MQなしはCorrelation ID=event ID、nested scope終了後に別requestへ継承しない）/351、PG-D354。上位仕様の変更なし。

fixture trace(request,id)はTest-local supplierが一回目UUID(0,id)、二回目UUID(1,id)を供給する。first id90/second id91。独立期待はsame=trueなら最初のbusiness UUID(2,91)、same=falseならfirstにbusiness発行がないため元入力event UUID(1,90)。この固定値はProduction ensure/correlationId/eventIdを呼んで生成しない。

操作は既methodのまま、same=false/true両条件。outer→innerでscopeを開始し、outer先行closeは固定IllegalStateException、inner business UUIDを保持、finallyでinner→outerを逆順close。両scope終了後のUUID(9,92)発行が閉じたtraceを書き換えず、secondはUUID(2,91)を保持する。null/NPE/並行の別既methodはこの一件へ混ぜず未選択、当caseはscopeの順序例外/同一・別trace境界/終了後条件を検証する。

着手前判定PT_DEFAULT。全Test source、選択method/helper、WebRequestTrace/Scope、WebRequestContext.identifyを読取。classに@BeforeAll/BeforeEachや独自constructorなし、static初期化は閉じたroute集合のみ。選択methodはSpring MockHttpServletRequestのメモリ属性とUUID/ThreadLocal/JDK atomicだけ。全Test sourceには別methodのsource inventory読取/transport filterがあるが選択しない。実HTTP/socket、Spring context、DB、Caddy、JMS、VM、Root、鍵、permit/intent、cohort復旧を起動しない。プロセスは自己所有のJVMと新規専用出力のみ。未特定/拒否操作や元八enum Testの再演ではない。

実装は一期待式のみ、他全source token/assertion/Mainを保持する。メタデータ反例で元SUT getter/誤fallback UUIDを拒否。前置static PMD/Checkstyle、正常六module compile(package -DskipTests=true)、当sourceの一method固定catalog JUnit、同run XML/JaCoCo session/CRC/完全Main class counters・全Main/他Test byte不変を独立照合。未網羅は残値で示し、counter100や正式451へ補完しない。実行command/環境/source/exit/hash/coverage/関連BUGは2082と公開manifestに保存する。

## 追加発見と同source選択範囲（修正前追記）

BUG1842/YKT1593：元static10532の三duplicate literalをTest-local同値定数化する。原一式plan10530/元raw八行は保存し、新planで元一期待式＋三literalだけを逆展開照合する。元段落の「一式のみ」は初期scope履歴であり、現在は追加三定数/十二参照も含む。群開始1/3/7/cap10は不変更、費用追加発見を分離する。

全十@Testと全helper/初期化を読取り、当Test classのDB/network/process/service接続なしを確認した。追加九methodも同sourceの明示catalogとして通常PTへ含める。これにより当一式の確認だけでなく関連null/境界/所有/並行も同runで照合する。全class discoveryは使わない。

|既REQ/ゼロ引数method|独立期待・対象操作|
|REQ004 req004ActualInventoryAndEveryClosedRouteRejectUnknown|snapshot内の公開controller sourceだけをread、固定37annotation/閉じたroute集合/未知は固定/**|
|REQ004 req004ReceiptProjectionUsesRegisteredPatternAndNeverRawLocator|Mock requestと固定handler pattern、canary locatorがrouteへ出ない|
|REQ006 req006ServerIdentityIsStableAndDoesNotGrantTransport|固定UUID(0,3)/(1,3)。MockHttpServletRequestのloopback/予約IP/https headerを通常filterへ渡す。InetAddress.ofLiteralだけでDNS/socketなし、既id再利用と異物metadata拒否|
|REQ007 req007ActorIsSafeDisplaySnapshotNotPrincipalAndMissingTraceIsNoOp|synthetic USER/ADMIN表示snapshot/NFC/empty/null/固定redaction、認証やsession/key操作なし|
|REQ008 req008NestedScopesRestoreOnlyFirstBusinessMessageAndDoNotInherit|固定UUID列、nested順序/二重close/別thread owner拒否/非継承/null supplier|
|REQ008 req008HundredConcurrentRequestsDoNotCrossContaminate|自己所有executor/100独立入力/5秒待ち、固定UUID(2,owner)/(0,owner)、全future終了|
|REQ004 req004InterceptorAcceptsOnlyRegisteredStringAndNeverErrorOverwrite|Mock ERROR/ASYNCと固定route、null、plain InterceptorRegistryだけ。Spring context起動なし|
|REQ006 req006AllNullAndMistypedMetadataAreRejected|null/未知型/欠落、固定例外型と属性境界|
|REQ006 req006AllFourAttributeBoundariesRedactFrameworkFaults|Mock get/setの明示IllegalArgument/State、固定安全message/cause無し/suppressed0。実SQL/障害cohortでない|
|REQ008 req008OutOfOrderNestedCloseCannotPublishAClosedTrace|上記1841の固定UUID fallback・same両条件・scope終了後の非再公開|

追加dependencyのCaddyTransportContextFilter/Resolver、LoginClientAddress、WebSecurityAudit、RequestLogMvcConfiguration/RouteInterceptorもsourceを読取。filterはMock request/responseに対する通常メモリ処理だけで、実Caddy/HTTPを起動しない。監査constructorのversion検証は固定pt、当正常transport経路はrecordを呼ばない。classには自動起動annotation/lifecycleがない。read対象はnormal snapshotの公開srcのみ、私有raw/現process/DB/鍵にはアクセスしない。coverageは完全Main五class（Trace/Scope/Context/RouteInterceptor/RequestLogMvcConfiguration）を同runで測り、他実行classや全moduleの100%を主張しない。
