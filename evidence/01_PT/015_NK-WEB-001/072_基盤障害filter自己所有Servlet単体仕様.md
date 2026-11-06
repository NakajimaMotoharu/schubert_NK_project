# 基盤障害filter 自己所有Servlet単体仕様

Program NK-WEB-001、WebInfrastructureFailureFilter constructor/doFilter、RD AUT/TST/FUN/UI221222226/SS313314351352、WBS-P015-02。開始4084原1/2.5/4 cap6固定。seed未登録・strict pin無し・followup0、Main全reviewで要求実装あり、製品変更不要。

全fixtureはJDK proxyのRequest/Responseとcaller FilterChain、固定DispatcherType/committedだけ。実session/DB/credential/HTTP/Browser/Root/VM/held四無し。SessionStoreExceptionは固定無cause constructor sentinelのみ、preserveFatal/例外graph分類を実行しない。getterは指定4操作以外AssertionError、body/header/session/content/設定/既存processへ接触無し。新8・同一source/normal20990 CRC/単一session JaCoCo、全line/method/class/branch100、人工除外・旧exec合算無し。

|Test ID|method|
|---|---|
|PT-WEB-INFRA001|nullPortsFailBeforeAnyCallback|
|PT-WEB-INFRA002|nonHttpRequestOrResponseFailsWithoutRunningCaller|
|PT-WEB-INFRA003|successfulCallerIsUnchangedAndNeverQueriesFailureMetadata|
|PT-WEB-INFRA004|typedStorageFailureMapsExactly503OutsideErrorDispatch|
|PT-WEB-INFRA005|committedOutputRethrowsSameTypedFailureWithoutReadingDispatcher|
|PT-WEB-INFRA006|errorDispatchRethrowsSameTypedFailureWithoutSecondErrorSignal|
|PT-WEB-INFRA007|otherFailuresAndErrorCallbackFailuresPreserveIdentityWithoutRetry|
|PT-WEB-INFRA008|sharedFilterKeepsEightConcurrentFailuresAndSuccessesRequestLocal|

期待は明示callback順とHTTP literal503/例外identityから独立作成。001 null三境界はcallback0、002 非HTTP request/response各組合せServletException固定文・callback0、003 全Dispatcher×committed成功はchain一回だけ・metadata読取0、004 REQUEST/ASYNC/FORWARD/INCLUDEのtypedSSEはchain→committed→dispatch→send503各一回、005 commit済みは同例外を再throw・dispatch読取0、006 ERRORは同例外で二重send0、007 その他IO/Servlet/Runtime/Error及びSSEをcauseとするServletExceptionは同一性・metadata0、sendError IO/Runtime/Errorも同一性・再試行0、008 sharedfilter二worker八requestで成功/失敗交互の順序/状態分離。全assertは既SSのtyped-only503と有限callback期待に由来し、製品からexpectedを作らない。

input013 prepare/static/run <frozen source>/post。JDK25.0.4、全Main4217/normal20990/six NullAway・SB20992 byte不変、明示固定SDK CPは既pinから検査・ダウンロード無し。Test javac release25/proc:none/lintallWerror、Main/Test PMD・CS/既samebyteSB、OS/JDK/source/全input/command/exit/元XML/TestID/実際値/coverageをmanifestへ。元execのSSE methodはconstructorだけを独立照合、未知initやheld type実行なら未受入。

BUG2387/YKT2132は最初の静的raw8中、Test event重複literal3で起票・元21312/14/Test全byteを21318へ保全し定数化。Main/oracle不変。最終21320compile0/21322static raw5各非該当（host workers2/defining proxy loader3）・適用0CS0/SB0。Unit未実行時点では合格加算0。結果073へ真正Unit/strict/独立post/障害再試験path/hashを記録。実runtime/Root/VM/cohort/native/CHR/QA051final/451・正式1964-53/新leaf/工数は別未受入。
