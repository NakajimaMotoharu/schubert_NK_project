# Log plain契約八・単体テスト仕様

2026-10-26、群2275/開始1-3-8cap10（2015と同一群、二重費用なし）、NK-ADM-001/WBS-P018-09（原941のLogRequest主担当、DAO P01004へ付替えない）。LogPlainContractTest、PT-LOG-PLAIN001..008、UI235§11/SS323§9.5・324/332/451。

## PT_DEFAULT・fixture

既LogRequestTest/LogVectors/DB/JCE fixtureを使わない独立新class。656space byteへUI235 zero-based offsets0/256/272/336/592/600/617/634、page1又は999999・size100。optional七fieldのnames/types/values/dateはTest-local固定表、日時JST→UTCは固定9時間差で独立算出。wire未知layoutはZZZREQ01（login専用context規約を流用しない）。null queryは全nullだけでrepository/connection実体なし。plain field標準cleanupのみ、鍵/寿命/並行/Graph9/actual/外部操作は2015と同じHOLD。

|Test ID末尾 / method|入力・操作|独立期待値|
|---|---|---|
|001 / plain001AbsentFieldsAndOriginalPageHaveLiteralMetadata|optional全space/page999999|owner8/LGSREQ01/001/REQUEST:LGSREQ01、九field/先頭七null、N1 page999999/size100、header同一/固定redacted|
|002 / plain002FilledFieldsPreserveUtf8OriginalFiltersAndUtcDates|七field全present|é_%/SECURITY/Read//plain/WARN/固定UTC二件、名前/順/X1,T1/UTF8原値、page1|
|003 / plain003MalformedLayoutLengthEnumDatesAndReservedAreRejected|未知layout/655/657byte/enum UNKNOWN/TRACE/不正月/page0/reservedx|PermanentProtocolException、固定message/causeなし、試験組立自体の例外と区別|
|004 / plain004NullPublicBoundariesStopBeforeAnyRepositoryReceiver|decode/canonical/response/null、query全null|明示NPE、非null backendなし・SQL未実行|
|005 / plain005EmptyResponseClampsRequestedPageWithoutChangingCanonicalPage|要求999999、empty response page1/100|validate成功、canonical原page999999は変更しない|
|006 / plain006WrongPageSizeAndRecordCountNeverAcceptNpeAsSuccess|page0/size99/record不足|identityのみIllegalArgumentException、codec制約はLayoutValidationException、NPE混入不合格|
|007 / plain007WrongResponseLayoutAndNonPagedDataAreRejected|USRRSP01/LogSearchRequestDataをLGSRSP01へ|両IllegalArgumentException、expectedをSUTから生成しない|
|008 / plain008AllSevenOptionalPresenceMasksUseIndependentExpectedValues|固定七bitの全128mask|各bit0=null/1=対応fixedUTF8、九field名/型/順保持。128を128独立Test IDと水増しせず一method|

実行は2015と同source一回16/2、正常compile・新二Test static・独立XML/両unit CRC/session/四counter・全Main byte/traceを照合。query実DB経路を未実行のまま残し、全100/全PGPTを宣言しない。環境/command/source/結果/hash/BUGは後続結果へ。
