# ADMIN query SQL前境界・単体仕様

2026-10-26、2036依存判定、主P01001/関連P01004-P01401追加費0、群P010_PRE_SQL_BOUNDARY_IMPLEMENTATION_V1・開始1/3/8 cap10。RD FUN008009/AUT002003/DAT003、UI225/235236241、SS311312314323332354/411451。原担当UserQueryRepository=P01001、LogQueryRepository=P01004を保持。Main変更なし。

|新Test ID|class/method|入力/独立期待|
|---|---|---|
|PT-ADM-PRE001|UserQueryPreSqlBoundaryTest.userPre001SearchNullContractsBeforeSql|null connection/actor/now/requestを単独投入、全NPE/名前はconnection/actor/now/request、JDBC0|
|PT-ADM-PRE002|同.userPre002DetailNullContractsBeforeSql|detailに同四null、全NPE/同名/JDBC0|
|PT-ADM-PRE003|同.userPre003UserCannotSearchOrDetailBeforeSql|USER actor、search/detail共FORBIDDEN/固定operation is not available/causeなし、JDBC0|
|PT-ADM-PRE004|同.userPre004OversizePrefixRejectedBeforeSql|ADMIN、ASCII prefix65byteをconstructorで保持、X64 encode拒否FieldEncodingException、JDBC0|
|PT-LOG-PRE001|LogQueryPreSqlBoundaryTest.logPre001NullContractsBeforeSql|connection/actor/request単独null、NPE/各名前/JDBC0|
|PT-LOG-PRE002|同.logPre002UserCannotQueryBeforeSql|USER actor、FORBIDDEN/固定message/causeなし、JDBC0|
|PT-LOG-PRE003|同.logPre003OversizeKeywordRejectedBeforeSql|ADMIN、Keyword257byte/X256、FieldEncodingException、JDBC0|

Fixtureは公開actor ID7/8・Role enum・固定Instant/Optional・Page1/size50（User）又は100（Log）。ConnectionはJDK自己Proxyで、任意methodを呼べば回数を増やしてAssertionError、SQLException/RuntimeExceptionの注入はしない。全期待はSSのnon-null/ADMIN/固定field幅と独立literalから定め、Productionからexpectedを作らない。入力構築をassertの外に置き、constructor拒否をRepository拒否へ誤算入しない。

全経路は最初のtry/JDBCより前。SQL/row/transactionの失敗catchとpreserveFatalはHOLD、Source2036で依存を分離。JDBC invocation0、保留Main二及び各SQL専用helper probe0を独立postで必須とする。実DB/既fixture/Root/VM/鍵close/サービス/認証情報/OS環境/ファイルへ不接続。再送/並行/DB後条件は本input-only境界に非該当、関連実経路の未試験をPASS化しない。

変更Testを先行static/GJF当file→source固定/正常六compile/PT0/NullAway-Werror→当3file13method閉catalog（Question六は014/007参照）→一JUnit/一exec→全XML/CRC/保留probe/JDBC0/complete三Repository source-unit四counter/全Main不変・他Test保持/traceへ進める。全class四100を予測せず未達保持、結果とcommand/OS/JDK/source/exit/hash/BUGは084/014-008/shared manifestへ保存。新機能TDD未実装の最初の赤はBUG扱いせず、実装済仕様違反は修正前起票する。
