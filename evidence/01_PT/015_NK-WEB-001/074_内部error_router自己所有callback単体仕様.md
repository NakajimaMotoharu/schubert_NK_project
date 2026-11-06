# 内部error router 自己所有callback単体仕様

Program NK-WEB-001 InternalErrorDispatchRouter constructor/init/destroy/doFilter、RD AUT/TST/UI221222226/SS313314352、主WBS-P015-02。開始4086原1/3/5 cap8、Main全review変更不要。seed未登録/strict pin無し/followup0。既SSのHTTP ERROR＋完全一致/errorだけを内部error callbackへ、他はbusiness callbackへ渡す。

業務/errorsのFilter.init/destroy/doFilterはTestの小さなcallbackだけで、実サービスの起動停止ではない。全Request/Response/FilterConfigはJDK interface proxy、getDispatcherType/getRequestURI/内部context読取以外はfail、body/header/session/HTTP/DB/Root/VM/held四へ触れない。固定UUID000…007/数値192.0.2.1で既request contextを供給するだけ、identify/bind/ID生成無し。SDK7.1.1の既PG21250固定bytecodeとjarhashを再利用し、child起動arg -Dspring.security.strategy=MODE_THREADLOCAL・元XML・実init・Test自身のstrategy classassertをfresh結合。空contextのみchild/Test threadでset/clear、既app/userの認証を読まず変えない。実session/認証/権限/実error dispatchを受け入れない。

|Test ID|method|
|---|---|
|PT-WEB-ERRROUTE001|constructorRequiresBothIndependentCallbackPorts|
|PT-WEB-ERRROUTE002|initializationIsBusinessThenErrorsAndBusinessFailureStopsImmediately|
|PT-WEB-ERRROUTE003|errorInitializationFailureCleansBothInReverseOrderEvenIfCleanupThrows|
|PT-WEB-ERRROUTE004|destructionAlwaysInvokesBusinessAfterErrorsAndPreservesFinallyPrecedence|
|PT-WEB-ERRROUTE005|nullAndNonHttpBoundaryRejectBeforeRoutingOrContextCleanup|
|PT-WEB-ERRROUTE006|onlyExactInternalErrorWithSuppliedContextRoutesToErrorCallback|
|PT-WEB-ERRROUTE007|missingContextAndAllCallbackFailuresClearOnlyOwnThreadAndNeverRetry|
|PT-WEB-ERRROUTE008|concurrentRoutesKeepEightSuppliedContextsAndCallbacksThreadLocal|

期待は明示順序とJava finally/例外同一性から独立に作成。001 二dependency null拒否・callback0、002 config null、business→errors init、business initのServlet/Runtime/Errorはその時点で同一例外・errors未実行、003 errors initのServlet/Runtime失敗はerrors.destroy→business.destroy、cleanup自体のRuntime失敗はJava finally規則に従いそちらが返るがbusiness cleanupは必ず実行、004 destroyは逆順、error cleanup失敗中もbusiness実行・最後finally失敗が優先、005 null/非HTTPはrouting前拒否・contextにまだ触れない、006 全Dispatcher×両URI/ERROR-nullURIはliteral分岐、正常business/errors後にchild context破棄、007 ERRORでcontext欠落拒否/両callbackのIO/Servlet/Runtime/Error同一性とfinally掃除・再試行0、008二worker八requestで各empty context/route/portを分離。errors init catchはServlet/Runtimeだけの実装で、fatal Error全般を正常化するものではない。

input015 prepare/static/run <frozen source>/post、JDK25.0.4/通常Main4217/20990CRC/六NullAway-SB20992同byte。Main/Test PMD-CS全raw個別適用、抑制無し、raw6はMain cleanup用Runtime catch1/欠落negative fixture null1/host worker2/定義loader2の個別非該当、適用0CS0/SB0。全line/method/class/branch100を単一JaCoCo0.8.15/旧exec合算・除外無しで要求。元command/exit/OS/JDK/source/TestID/XML/input/期待actual/coverage/hashをmanifestへ。SDK Holder/ThreadLocal固定レビューと当実execのrequestcontext/LoginClientAddress ctorだけという依存閉包を独立照合し、graph/生成/heldinitは認定しない。

新8未実行時点は合格加算0、結果075へ真正Unit/strict/独立post・SDK/source/同CRCと残リスクを保存。失敗障害は修正前915/916。Root/VM/cohort/実session/Browser/native/CHR/QA051final/全451/新leaf/正式1964-53/工数は別未受入。
