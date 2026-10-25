# User要求plain正規化四・単体テスト仕様

PG9964/source1aeの初回は8/2中7成功1失敗・actual1。BUG1783/YKT1534を修正前起票。core003のlogin layoutはcontext absent規約と衝突し対象decodeへ未到達だったため、通常unknown layoutの固定ZZZREQ01へ修正する。製品・期待例外・承認仕様は不変更、新sourceで同8件の必要回帰を実施し、初回失敗とexec/XMLを別保全する。

静的先行：PG9958/source=null/base35b・固定新Test hash e72a1e7ebe0ea647e11929e095f03ba2bf5eb0aa025467015a4df3e2c8679bd9、元正常Main/他入力不変。CS0/PMDraw1/processing0/真正1、manifest bbbd2c34b9b97d2c3628a3be2ed847bb4cd4b5364cabf2d211a0e0ba59cb2c2d。指摘は67行のcanonical.fields().get(index)というborrowed fieldで、外側try-with CanonicalRequestが全fieldを解放するため個別非該当（close実行による寿命試験ではなく既source所有契約の静的確認）。raw値を0へ変更/抑制しない。source固定後に当byte/compilerとの対応を確認する。

2026-10-26、P010_PLAIN_CANONICAL_CORE_V1、開始1/3/8pp cap10・used22残78/reset1793513544。NK-ADM-001/WBS-P010-01、UI236§3/5・SS323§9.4/324§3、451。MainはUserQueryRequest、関連CanonicalRequest/Fieldの既公開sourceを読取り、String/List/UTF8/NFC/配列cloneとcleanupだけで、鍵/HMAC/JCE/provider/外部依存を持たないことを確認した。Production Main/外部仕様不変更、新Testのみ。

## 独立性・禁止範囲

新UserQueryCanonicalCoreTestの四methodを、既UserQueryResponseBoundaryTest四methodと当source単一run（八/二suite）で普通JUnit実行する。新規観点が同SUTのfield生成/状態独立性へ入るため既四を関連回帰として含め、旧成功だけの再確認ではない。既DB/JMS Test/helperは使用せず、fixtureは当Test内の96/12byte、架空actor/UUID/時刻、明示field name/type/valueだけ。

CanonicalRequestはplain User検索条件/IDの表現として使用し、標準try-with cleanupだけを行う。key/nonce/ciphertext/fingerprint/暗号providerなし、進行中close/並行/消去後bufferの検証はしない。Snapshot鍵close拒否の別名再試行ではなく、対象class/data/期待値/実行経路が別。queryは**repository/connection/actor/nowをすべてnullにした呼出しだけ**で、非null repository/connectionを生成せず、SQL・Graph9処理へ入るreceiverが存在しない。private reflection/JDBC proxy/DB/HTTP/JMS/VM/Root/鍵/私有raw/old job操作0。

## Test IDと独立期待値

|ID/method|入力/操作|期待値・独立出典|
|---|---|---|
|PT-ADM-CORE001 / core001FilledSearchFieldsUseIndependentLiteralMetadata|space96へSS/UI offsetにNFC Équipe/ADMIN/ACTIVE/000001050、actor7。canonical getterを確認|owner7、USRREQ01/001/REQUEST:USRREQ01、五field順usernamePrefix/X1,role/X1,state/X1,page/N1,pageSize/N1。値は入力Équipe/ADMIN/ACTIVEとASCII1/50を手組期待。SUTのbranch/getterからexpectedを生成しない|
|PT-ADM-CORE002 / core002MissingOptionalsAndDetailRetainOriginalValues|optional全spaceの検索、UDT raw000000000003、actor8|optional三fieldのvalueはnull（空byteとは別）、page1/50。detailはUDTREQ01/001/REQUEST:UDTREQ01、userId/N1/ASCII3だけ。正常cleanupはtry-with、close/鍵寿命の試験ではない|
|PT-ADM-CORE003 / core003RedactedMetadataAndInvalidDecodeStayBounded|検索toString、未知request layout、decode null|UserQueryRequest[REDACTED]固定、未知layoutはPermanentProtocolExceptionの固定message/causeなし、nullは明示API境界NPE。SSのstrict request allowlist/411redactionと既ADM042の固定拒否規約|
|PT-ADM-CORE004 / core004NullActorsAndRepositoriesStopWithoutDelegation|検索/明細canonical(null)、query(null,null,null,null)|APIの明示null拒否NPE。repository実体/接続を一切作らず、queryのbodyから非null receiverへ進めない。認証/SQL動作や全引数の独立null条件を本四callだけで証明しない|

## 品質・未完

Test-only staticをMain/依存/POM不変の型byte証拠付きで先行できる場合はPG-D676を適用、source=null/base/hashで記録し旧commitへ偽装しない。source固定後正常六compile/PT0→八宣言/二class/当byte・pure fixture preflight→当八だけJUnit→XML/CRC/session/complete UserQueryRequest unitの四counter/変更source static・全Main byteのpost。queryの正常SQL分岐へ入らず、unit全100を前提にせず未網羅を保存する。0-counter/旧exec/native/別sourceを合算しない。

新ID四件/新Test一path、既四との回帰を八新規と数えない。field expectedはSS/UI literalと固定fixtureから作りProduction canonical method/HMACから期待値を生成しない。source修正時の必要回帰は実施、初回TDD未実装失敗と既機能障害を区別し、既機能違反は915/必要916を修正前起票する。正式1964/53・17/190・QA051final/工数nullと全安全HOLDを維持、通常群/commitで停止しない。
