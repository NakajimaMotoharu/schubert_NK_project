# NK-ADM-001 Log SQL界面契約・単体テスト仕様書

2026-10-26、P018_LOG_SQL_INTERFACE_CONTRACT_V1/群2287、主WBS-P018-09・関連P010-04追加費0、開始1/3/8pp cap10、used26残74/reset1793513544。FUN008/AUT002003/MON003004、UI225/235§11/241、SS311/312/323§9.5/332§3～4・411/451。対象LogRequest.query/validateResponse、LogQueryRepository.search/record/filters。

新LogSqlContractTest/PT-LOG-SQL001～008の八methodと、既LogPlainContractTest八methodを同source/一run/16method/2suiteで関連回帰する。既八成功だけの確認再演でなく、新query経路の追加。source固定後の当正常六compile・NullAway/Werror→閉じた16宣言preflight→一JUnit→独立XML/一exec/session/完全二unitのCRC/四counterへ進む。Main変更予定なし。

## 自己fixtureと独立性

JDK public JDBC三interfaceの自己proxyのみ、backend/driver/DB/URL/ネットワーク/私有反射/外部processなし。declared callback以外はAssertionErrorで停止、SQL失敗やinvalid DB rowを注入しない。RepositoryのSQL catch/preserveFatal/Graph9を実行しない。正常のnullable任意列は許容値で、必須列は全て有効値。禁止product probe0を独立postで確認。actual DB構文/plan/整合性/並行/lock/後条件を本fixtureで合格にせず、既DB試験は未実行のまま。

入力はUI235 LGSREQ656のoffset（0,256,272,336,592,600,617,634,640）とASCII固定値から手組。expectedは独立SQL fragment/bind順・UTC literal・typed LogRecord・PAGED48とUI235 record2088のoffsetから手組golden、Productionの検索/mapperでexpectedを生成しない。合成公開IDのみ、実token/credential/session/keyを使用しない。

|ID/method|目的・fixture/入力|独立期待値|
|---|---|---|
|SQL001/sql001EmptySearchRetainsRequestedPageAndStableSql|filterなし/page999999、total0/pages1/effective1/id-null|LGSRSP01/Paged1,100,0,1,0,0、bind999999、level許可集合/共通materialized count-page/日時ID降順/limit100。原pageはcanonical999999のまま|
|SQL002/sql002AllFilterMasksBindLiteralWildcardsAndUtcBounds|七optionalの128mask、é_%\\/SECURITY/Read//a_%\\/WARN/FromTo各1秒|keyword二bind・path一bindは独立escaped substring、action完全一致、UTC OffsetDateTime typedbind、page最後。各predicate有無とSQLに入力非埋込|
|SQL003/sql003MinimalMappedRowKeepsOptionalAbsenceAndMilliseconds|required valid row・全nullable列null、時刻.123456Z|独立LogRecord/.123Z、required action/details Optional有、nullable八列empty、RS→PSclose|
|SQL004/sql004FullMappedRowMatchesIndependentFixedWidthGolden|全任意列有・合成UUID各1/2/3・status200/elapsed0/IP2001:db8::1|typed全値と独立2088byte（offset/UI235表・JST17桁・reserved spaces）、期待をcodecから生成しない|
|SQL005/sql005FinalPageClampHasExactHundredRowBoundaries|total101/pages2/effective2/id101一row・request999999|Paged2,100,101,2,101,101とrecords1、SQLoffset100が式に固定、responseに原page整合検証|
|SQL006/sql006InvalidInputStopsBeforeBorrowedReadOnlyBlock|直接typed page0/size99/不正31日期間、他全有効|validation IllegalArgumentException、connection method/prepare/close各0。DB catchに到達しない、NPEを合格にしない|
|SQL007/sql007UserRoleDeniedBeforeAnyJdbcMethod|Role.USER、正規wire|AuthorizationException/FORBIDDEN、JDBC method0、役割gateはquery前|
|SQL008/sql008NullArgumentsStopWithoutInterfaceCalls|query repository/connection/actor、Repository connection/actor/request各独立null|明示NPE境界拒否、非null残引数保持、JDBC method0、normalでNPEをcatchしない|

正常SQLはgetAutoCommit=false/isReadOnly=true/prepareStatement一回の三Connection callだけ認める。commit/rollback/close/設定変更なし、executeQuery一回/ResultSet→Statement各一close。並行実行やDB異常/容量overflowはこの選択外、未網羅counterを隠さず080へ残す。

実command/日時/環境/branch/commit/coverage/全case実結果/BUG/証跡hashは080とshared018公開manifestへ記録。failed/skipped/aborted/not-runを成功へ加算0。正式1964PT/53scope/17-190/工数null/QA051final・全安全HOLD不変。
