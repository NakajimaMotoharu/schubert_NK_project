# NK-ADM-001 User SQL界面契約・単体テスト仕様書

静的先行：10038 source=null/base5012/新Test hash f03e234b..でPMDraw6/CS0/実1、BUG1789/YKT1540を修正前起票。field二名・cursor表記・typed getter引数数を同値是正し、10039は新hash6b548e31a90ca745bc376d62f0b01b3d140059b23c5cda92b66bc2c0f8d3b84eでrawPMD2/CS0/processing0/実1（manifest a9b7090a51267b2f9fef5c0ad6d94f40668fc9590ad7dc38b688e239c65b7b03）。残二はUseProperClassLoader（J2EEでない自己host interface proxy）とUseConcurrentHashMap（各method一fixture・一thread/parallel=falseのprivate Map）で個別非該当、抑制追加0。まだ当PT未実行なのでその裏付けは当16methodの実結果とsource/hash postへ結合する。

2026-10-26、P010_USER_SQL_INTERFACE_CONTRACT_V1、開始1/3/8pp cap10、used25残75/reset1793513544。WBS-P010-01、RD FUN009/AUT002003/DAT003、UI225/236/241、SS312/323§9.4/331/332・411/451。対象UserQueryRequest.query/validateResponse、UserQueryRepository.search/detail/row mapping。新UserQuerySqlContractTest八method/PT-ADM-SQL001..008、Main変更なし。

## PT_DEFAULT・自己所有fixtureと限界

JDKのpublic Connection/PreparedStatement/ResultSet interface proxyだけを使う。DriverManager/DataSource/driver/URL/ソケット/DB・外部processを生成せず、private反射/既DB/Test helper・JCE/HMAC/Root/VM/permit/鍵witnessも使わない。proxyは宣言したmethod以外をAssertionErrorで拒否し、SQL/型/データ異常の故障注入をしない。UserQueryRepositoryのSQLException等catch/preserveFatal/例外graph経路は今回未実行HOLDであり、callbackはSQLException/RuntimeExceptionを投げない。実PGのSQL構文・計画・整合性/lock/同時性/DB後条件はこのmockで確認したとせず、既DB試験の未実行を保持する。

これは単にquery forwardのcoverageを上げるfixtureではなく、SSの固定50件/最終page補正、一SQL count-page snapshot/C順、prepared bindによるliteral prefix、typed UTC投影、secret column非選択、borrowed transaction不変更、RS→PS解放という**観測可能な界面契約**を独立assertionにする。新八と既Core四/Response四を同source一run/16method/3suiteで関連回帰する。既成功だけの確認再演ではない。実UserRequest/Repositoryを使用し、repository subclass/mock seamを製品へ追加しない。

## 独立期待値

入力wireはUI236のUSR96（prefix0/role64/state69/page77、size50）とUDT12byte ASCII000000000003を手組する。actor ADMIN7/USER8は公開合成値で認証済みを模すだけ、実ログイン/権限取得ではない。NOW UTC2026-09-08T00:01:00Z、bindは独立OffsetDateTime literal。結果tupleも固定Mapで手組し、Production SQL/query/mapperからexpectedを生成しない。

|ID/method|入力・操作|期待値・独立根拠|
|---|---|---|
|SQL001/sql001EmptySearchUsesOneReadOnlySnapshotAndRetainsOriginalPage|USR無filter/page999999、total0/pages1/effective1/id-null一tuple|empty page1/50/0、bind1=UTC now/2=999999、filterなし、一prepare/execute、C順/limit50/一materialized count-page。SS332§3/SS323§9.4|
|SQL002/sql002PrefixNormalizationAndLiteralWildcardEscapingStayInBinds|prefix` É_%\ `、roleUSER/stateACTIVE、empty tuple|NFC+trim後にunderscore/percent/backslashを個別quoteし末尾%追加、SQLに入力Éなし、bind順now/prefix/USER/ACTIVE/page1。SQLと値分離、SS323/332 literal検索|
|SQL003/sql003OneMappedRowKeepsTypedColumnsAndMillisecondProjection|prefixu、USER/ACTIVE、id3/u3/version4・lastLogin原.123456Z|明示UserRecordとpaged(1,50,1,1,1,1)、lastLogin .123Z/lockなし。SS323/SSC056のJDBC4.2 UTCとwire ms投影|
|SQL004/sql004MissingDetailIsAbsenceAndStillClosesOwnedStatementAndRows|UDT3/no rows|Optional.empty、UTC now二bind/long3、active sessionはrevoked=false/expires_at>now条件、target ID bind、RS→PS close|
|SQL005/sql005DetailProjectsTwoActiveSessionsWithoutSelectingCredentials|UDT3、ACTIVE/User3/session2/PW変更原.123456Z/作成SYSTEM更新operator|独立UserDetailResponseData、session2上限、PW変更.123Z、secret hash/salt/token_digest非SELECT・for updateなし。DIF016/SS323/332|
|SQL006/sql006LockedProjectionPreservesOptionalTimeAndAbsentLastLogin|prefixu、LOCKED、未来lockedUntil原.456789Z/lastLogin-null|UserRecord LOCKED/lockedUntil .456Z/lastLogin empty、filterbind LOCKED、原dataをSUT expectedに流用しない|
|SQL007/sql007UserRoleIsDeniedBeforeAnyConnectionMethod|USER8でquery|AuthorizationException/FORBIDDEN、connection method0/prepare0/close0。SS314のADMIN境界、SQL/例外graph前|
|SQL008/sql008IndependentNullArgumentsNeverReachTheBorrowedInterface|connection/actor/now各単独null、他は非nullのinterface/real repo/actor|明示NPE、connection method0、Repository SQLへ未到達。411 null契約、normalのNPEを成功にしない|

全正常SQL caseはgetAutoCommit=false/isReadOnly=true/prepareStatementの三connection callだけを認める。commit/rollback/close/設定変更はcallbackで拒否、1 query/RS→PS各一回を確認。ResultSetの列不存在はfixtureエラーAssertionError、入力はvalid tupleだけ。異常DB値・SQL失敗・複数record/並行等は既DB仕様の別未実行で、本八成功へ合算しない。

## command/品質・証跡

Test-only staticを当normal Main型byte/依存/POM不変と新hashに束縛して先行（PG-D676）、source固定後normal六compile/PT0→16 exact declarations/fixture/当byte preflight→closed16method一JUnit→独立XML/CRC/session/complete UserQueryRequestとUserQueryRepository unit counters・全Main byte/当static・traceへ。Graph9 Mainの実probeがないことも後条件で確認し、不明・実行されていた場合は成功/100へ正規化しない。Main2unit以外の全APIやDBを合格化しない。

既Core/Response八は関連回帰、新ID八だけを追加実績に数える。Failed/skipped/aborted/未実行を合格にしない。当source/run・実command/OS/JDK/tool・input/期待値/実際/coverage/BUG/hashは078結果とshared018の公開manifestへ記録する。秘密/実session/token/raw DBを保存0。正式1964/53・17/190・工数null/QA051final・全安全HOLD維持、通常group/commitで停止しない。
