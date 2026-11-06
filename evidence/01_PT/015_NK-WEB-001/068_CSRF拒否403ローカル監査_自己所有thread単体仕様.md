# WebCsrfDeniedHandler 自己所有thread内403・監査単体仕様

Program NK-WEB-001、ctor/handle、RD FUN001/AUT004/MON004/UI222226252/SS313314351352、WBS-P015-02。開始4080原1/3/5 cap8固定、原seed未登録/strict pin無し・followup0。Main全文/全calleeとSDK固定modeをreviewし変更不要。新8method、対象一Main/physical1。コードに条件分岐がなければbranchはNATURAL_ZERO_BRANCH/比率null、line/method/class100と全例外/境界を測定し0/0を実測100へ補完しない。

専用child JVMの起動arg spring.security.strategy=MODE_THREADLOCALに固定し、固定Spring Security7.1.1のThreadLocalStrategy constructorを静的確認。custom class reflection/global/inheritable strategyを使わず、起動後のstrategy変更APIは呼ばない。各main/worker test threadの合成contextだけset/clear、既存app/user/serverの認証・設定へアクセス0。Servlet Proxyは内部属性get/set/removeとstatus/sendError403だけを許容しgetSession/header/body/cookie/parameter/任意responseを拒否。clock/UUID/ip/actor/CSRFは固定public canary（ofLiteral192.0.2.1のみ・DNS無し）、実session発行/DB/API/MQ/Root/VM/鍵/暗号0。

|Test ID|method|
|---|---|
|PT-WEB-CSRF403001|nullBoundariesRejectBeforeRequestResponseOrAuditCallbacks|
|PT-WEB-CSRF403002|unauthenticatedDenialReturns403AndOneClosedAuditWithoutInspectingException|
|PT-WEB-CSRF403003|authenticatedDenialWithoutSuppliedCsrfKeepsNoDisplaySnapshot|
|PT-WEB-CSRF403004|authenticatedSuppliedCsrfCapturesDisplayStringsWithoutLoggingSecretCanary|
|PT-WEB-CSRF403005|missingOrWrongTrustedRequestContextStopsBeforeAnyTerminalCallback|
|PT-WEB-CSRF403006|untrustedAuthenticationAndMalformedDisplayInputFailBeforeAudit|
|PT-WEB-CSRF403007|terminalCallbackFailuresPreserveIdentityAndDoNotRetryOrContinue|
|PT-WEB-CSRF403008|twoWorkerThreadLocalActorsAndRequestAuditsRemainIndependent|

期待はProductionから生成せずUI/SSのliteralへ固定：nonnull時以外はrequestContext必須、403設定→request表示snapshot掃除/必要な既csrfを表示用project→local audit一回→sendError403の順。匿名はactorfields無し、closed actorはusername/ADMINだけ、timestamp固定3桁/WEB/WARN/SECURITY/AUTHORIZATION_DENIED/DENIED/details{reason:CSRF,route:/**,targetType:HTTP_REQUEST}、許可key完全一致。denialのgetMessage/getCauseはTest内AssertionErrorで非読取を要求、Throwableはloggerへ渡さない。csrf/authcontext公開canaryもlogへ出ない。既表示snapshotの除去/必要時再保持、ctx欠落/型・不正Auth・表示token誤型/名前、callbackRuntime/Error/IOException同一性・再送/継続無し、二worker8のcontextとauditの分離をassert。

input009 prepare/static/run <frozen source>/post、JDK25.0.4、Main Core4217 normal20990/六NullAway・SB20992全同byte。CPはprotocol/web/Jspecific/Servlet/Spring/Security/commonslogging/Gson/errorprone/JUnitのみ、SpringSession/DBdriver/Artemis/Bootstrap/Playwrightは不要。Test javac release25/proc:none/lintallWerror、Main/Test PMD-CS全raw個別分類、source/driverGit/元XML/全hash/normalCRC/単一JaCoCoexec/手動除外・合成無し、SDK modeとactualinit/held四probeをstrict/独立postで照合。既WebSecurityAudit/Display/ClosedAuth等の資格は依存利用だけで新規全sourceへ加算0。実Browser/CSRFfilter/認証/所有/native/CHR/QA051final/451/正式受入は未完。SDK/JVM syscall全0は未測定。障害は修正前915/916登録、元失敗source/run保持・再実行は必要分だけ。結果069/manifestに日時OS/JDK/branch/source/command/exit/入力期待actual/coverage/BUG/path/hashを保存。
