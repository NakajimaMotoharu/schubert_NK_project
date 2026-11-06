# FormCsrfTokenRequestHandler メモリ境界 単体仕様

NK-WEB-001/WBS-P015-02、RD FUN001/AUT004・UI226・SS313/314§8.1/352、PG-D100。MainD8不変更、constructor/handle/resolveCsrfTokenValue全Source。PT_DEFAULT、969/event4003原0.5/2/4pp cap6。

新JDK memory Servlet proxyと固定合成placeholderだけ。SpringSecurity7.1.1 CsrfTokenRequestAttributeHandler/SupplierCsrfTokenのjavapを確認し、handleは_csrf/class-name二属性へlazy wrapperを保持、sourceはsession/store/token generation/matchingを呼ばない。固定supplierは実key/実token無し、null/failureはvalidへ変換しない。64/128文字と許容alphabet、null/multi/null要素/短長/不正alphabet、queryの正確_csrf・percent decode/壊れescapeの早期null、別case/unknown query正常、query取得外側例外とbody内側IllegalArg/fatal等を独立期待値で区別する。戻り文字列を実CSRF認可と解釈しない。

全9method、自己所有2worker8request/10秒joinで属性非混在を確認。legacy WebCsrfIntegrationTest/暗号session/DB setupは呼出/抽出0。actual token/cookie/session/key/DB/JMS/HTTP/VM/Root/held4は無し、証跡はhashと要約だけでplaceholder値を出力しない。resolverでは渡したCsrfToken getterを一切読まないことをthrowing fixtureで確認する。既SSの_csrf固定名はcase-sensitive、上位filter/CSRF比較/認可の責務は保持する。

shared012/profile069・六SDKsha固定、prepare/static→Git固定→単一全9/JaCoCo・全physical1/四counter100/currentCRC/strictpost。normal20112/SB20114再利用、app初期化handler/WebCsrfToken/新Testだけ、Cipher/SecurityContextHolder/store無し、JVM metadata/native数は未測定null。結果053/manifestへ時刻/環境/tool/command/source/exit/XML/counter/BUG/hash、真正終端後freshを結合する。全security chain/Browser/CSRF grant/session/全451/正式1964-53/歴史17-190/工数null未受入。

|Test ID|method|
|---|---|
|PT-WEB-CSRFPORT001|lazyHandlingSetsOnlyTheTwoRequestAliases|
|PT-WEB-CSRFPORT002|nullApiBoundariesRejectBeforeDelegation|
|PT-WEB-CSRFPORT003|validSchemaReturnsSubmittedValueWithoutReadingToken|
|PT-WEB-CSRFPORT004|missingMultipleNullAndMalformedValuesReturnNull|
|PT-WEB-CSRFPORT005|queryCsrfAndInvalidEscapesRejectBeforeBodyRead|
|PT-WEB-CSRFPORT006|absentEmptyAndDifferentCaseQueryNamesKeepBodyValue|
|PT-WEB-CSRFPORT007|deferredNullAndFailureAreNotMadeIntoValidValues|
|PT-WEB-CSRFPORT008|bodyArgumentFaultIsNullButOutsideQueryAndFatalPropagate|
|PT-WEB-CSRFPORT009|sharedHandlerKeepsParallelRequestAttributesSeparate|
