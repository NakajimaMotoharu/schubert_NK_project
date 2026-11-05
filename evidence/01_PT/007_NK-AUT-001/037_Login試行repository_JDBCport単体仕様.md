# Login試行repository JDBC port単体仕様

NK-AUT-001 / LoginAttemptRepository全method / AUT001・UI226§4・SS312§4/314§5/331§4/332§5・PT-AUT-003-D・411/451・776。正規化済usernameKeyのbyte上限96は表示入力64byteと混同しない。User→IP固定順、既borrowed transaction、成功/失敗のbindとownedstatement/rowcloseを独立検証する。

|Test ID|LoginAttemptPortTest method・入力・独立期待|
|---|---|
|PT-AUT-ATTEMPTPORT001|lockOrderAndLiteralSqlBindingsMatchUserThenCreateThenIp。設計5SQL中selectUser/createIP/selectIPをliteral比較、User7/名前/RoleUSER/active/0失敗/nullwindowとIP0/windowNOWをproperty比較、bind型UTC・close順、user不在/create0でもIP読取。|
|PT-AUT-ATTEMPTPORT002|persistedClosedRoleStatusAndNullableTimesHaveExactProjection。USER/ADMIN×ACTIVE/DISABLED、User5/IP10、window/lock時刻の独立literal値、row/stmt閉鎖。|
|PT-AUT-ATTEMPTPORT003|usernameByteAndNullContractsRejectBeforeBorrowedTransactionMutation。ASCII1/96・é×48=96成功、空/97/é×49拒否、非nullcaller全境界NPE拒否、autoCommit=trueは固定catalog・SQL0。NPEcatch/正常化なし。|
|PT-AUT-ATTEMPTPORT004|requiredAndMalformedUserColumnsBecomeFixedCatalogAfterClosingOwnedResources。必須6列null、未知role/status、ID0/空username/疑似hash256/failed-1は固定AuthenticationInfrastructureException、cause/suppressedなし、row/stmtclose1。疑似hashは非credential固定文字列のみ。|
|PT-AUT-ATTEMPTPORT005|missingIpAndInvalidRequiredIpStateNeverEscapeAsDefaultOrSuccessfulSnapshot。IP欠落、必須failed/window null、failed11、Instant.MAXのUTC変換不能を固定拒否。取得済資源だけをclose、既User→createIPまでの順維持。|
|PT-AUT-ATTEMPTPORT006|failureWritesIndependentFirstAndThresholdWindowGoldenBindings。最初0→1/null lock、15分境界User4→5/IP9→10/lockNOW+900、900秒を超すwindowと丁度lock expiryは新1/windowNOW、時計後退は固定拒否、Instant.MAXは取得済stmt1close/update0。期待は手作成Map、SUTのafterFailureをexpected算出へ呼ばない。|
|PT-AUT-ATTEMPTPORT007|successClearsUserWindowsAndMapsNonNullIpWindowToNow。User5/IP10から0/nullwindow/nulllock、User lastlogin条件true/NOW、IP mandatorywindowNOW、user不在ならIPだけ。|
|PT-AUT-ATTEMPTPORT008|unexpectedUserOrIpUpdateCountsRejectAndNeverTouchCallerLifetime。各UPDATEのMIN/-1/0/2/MAX件数は固定拒否、失敗箇所までのstmtだけclose、caller commit/rollback/connectioncloseは禁止。|
|PT-AUT-ATTEMPTPORT009|scriptedProviderFailuresCleanupAndHiddenFatalSelectionFollowBorrowedOwnership。auto/getter/prepare/bind/query/next/update/rowclose/stmtcloseのSQL/RTE/Error、SQLは固定catalog、unknown/Errorは同一性、reading/record双方のSQLcause Errorもその同一性。全取得資源close試行。既AuthenticationInfrastructureExceptionの独立pure module-local graphを使い、HELD四classは呼ばない。|
|PT-AUT-ATTEMPTPORT010|concurrentIndependentAttemptsNeverShareBorrowedStatementsOrRowSnapshots。別User7/8・名前の二worker、Future5s有限、別borrowedconnection/row/bindingsを確認。実DB行lock・isolation性能を証明しない。|

FixtureはJDK JDBC interface Proxy、手作成Map/row/event/件数/ownThrowableだけ。InetAddressは固定bytes/ofLiteralでDNSなし。実DB/pool/driver/credential/鍵/認証発行/Root/VM/nativeアクセスなし。旧実DB LoginAttemptRepositoryTest/LoginAttemptSequenceTest等はcompile/runへ含めない。

元draft PG18912compile0、formatter後編集import不足PG18916compile1と後続guard1（静的未実行）はBUG2284/YKT2029へ保存。修正PG18918compile0/18914raw12、重複2適用を修正前追記、追加caseのSQL/RTE/Error行列は初回実行前に充実。最終PG18924compile/18926static、exactsource固定後PG18932全10/一classを正常APIjarで新単exec/sessionへ実行し、classCRC/全physical/全@Test/元XML/HELD四probe0/全四counter100を独立post。Main全6input/JAR/NullAway/SBはPG18642/18648の同b093と照合し再利用、旧exec合算・任意除外・静的抑制なし。結果と環境/source/command/exit/hash/BUGは038へ保存。親WBS/実DB/crypto/V/451全体は未受入。
