# G13.07・Web session/security/起動境界24 sourceの主関連責任

2026-10-25 14:57 JST、G13_WEB_BOUNDARY24_SOURCE_V1/source64446不変更、開始.5/2/6pp/cap10。fresh67残33/reset1793382075（05:54:10UTC）、現在窓残10以下/取得不能で保全、旧累計80/90なし。

sourceは`src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/`以下。Mainの元ownerとSS/Test目的で主担当を分け、sessionというpackageだけからP01501等へ一律配賦しない。Spring security連携はP01502、token lifecycle P01503、logout P01504、API session失効P01506、login成功/失敗handlerは実MqLoginHandler P00706、assembly P01806。関係する他WBS・runtime不確定を全部保持し、artifact費を利用側へ再配賦しない。

|source|primary/cost|実Main・既Test/SS根拠|
|---|---|---|
|api/file/WebBrokerContextsCredentialTest.java|WBS-P005-02|WebBrokerContexts、JMS-WEB003、実broker/credential実行なし|
|api/file/WebNativeCodecsCredentialTest.java|WBS-P018-06|WebNativeCodecs、WEB-NKEY003|
|api/file/WebNativeRuntimeCredentialFixture.java|WBS-P003-07|ServiceCredentialId/合成five-key fixture、実secretなし|
|web/bootstrap/WebAdmissionRemainderTest.java|WBS-P018-06|Web起動入力/admission、SS343/PG-D378|
|web/bootstrap/WebManagementDeadlineTest.java|WBS-P018-06|WebManagementServer、WEB-MGMT335001..003|
|web/bootstrap/WebNativeRuntimeOwnedComponentTest.java|WBS-P018-06|WebNativeRuntime、WEBOWN327001..007|
|web/bootstrap/WebNativeRuntimePartialTest.java|WBS-P018-06|WebNativeRuntime partial、OPS-NWEB-PART001..|
|web/bootstrap/WebRuntimeRemainderTest.java|WBS-P018-06|Web runtime、OPS-WEB-REM001..003|
|web/bootstrap/WebUnstartedManagementTest.java|WBS-P018-06|Web management stop、NHOLD317001|
|web/security/WebAuthorizationFilterTest.java|WBS-P015-02|WebAuthorizationFilterFactory、WEB121..124|
|web/security/WebRequestIdentityConsistencyTest.java|WBS-P015-02|request/security identity、WEB-IDENT-CONSIST001|
|web/session/ApiSessionInvalidTest.java|WBS-P015-06|ApiSessionInvalidHandler、WEB158..165|
|web/session/EmbeddedWebSecurityTest.java|WBS-P015-02|Servlet/security boundary、実HTTP/DBなし|
|web/session/ErrorMvcTest.java|WBS-P016-24|WebErrorDispatchFilter/error MVC、WEB148..157|
|web/session/LogoutControllerTest.java|WBS-P015-04|LocalLogoutHandler、RERUN007|
|web/session/SessionAccessFailureTest.java|WBS-P015-02|WebAccessFailureHandler、WEB125..130|
|web/session/SessionFormLoginTest.java|WBS-P015-02|MqFormLoginFilterFactory、WEB082..089|
|web/session/SessionLoginHandlerTest.java|WBS-P007-06|MqLoginSuccessHandler/FailureHandler、WEB113..120|
|web/session/SessionOperationTokenV2Test.java|WBS-P015-03|SessionOperationToken、QA049/TOKV201..205|
|web/session/SessionSavedRequestTest.java|WBS-P015-02|EncryptedSessionRequestCache、WEB076..081|
|web/session/SessionSecurityContextTest.java|WBS-P015-02|EncryptedSessionSecurityContextRepository、WEB068..075|
|web/session/WebCsrfIntegrationTest.java|WBS-P015-02|EncryptedSessionCsrfTokenRepository/Filter、WEB050..053|
|web/session/WebRequestSecurityTest.java|WBS-P015-02|Web security/request、WEB101..108|
|web/session/WebSecurityChainTest.java|WBS-P015-02|WebSecurityFilterFactory、WEB131..136|

元9386v3 current source/CP graph、現9438 register、元485 Main owner、原PT/SSを固定。24 sourceのhelper closure/current-normal hash/JDK SourceFile・CP/実Main宣言を静的照合し、事前のliteral表を別parseしてprimary expectedと比較する。related集合を多数決で狭めず、reflection/UNKNOWN等の不確定は保持。credential合成fixtureのsource対応を実key読み出しやnative admissionに変換しない。

SQL/DB/HTTP/broker/native/child/Root/Unit/認証/target compile-load/JUnitの実行0、旧成功PTの確認再演0。五fullpath選択vector、cost一field/primary/関連/保留捏造・hash/source取り違え/status/欠落重複/近傍/旧logical優先を反証。旧761とartifact witnessまで保持。見込1586→1610/1789/Test621→645/824・残203→179・限定761→785だが独立検証後のみ計上。これはfile責任の整備であり全method/要件/oracle/TestID/依存・実行PT/coverageの完了ではない。

原941/歴史943/481484/予算/受入意味・正式1964-53/17-190/工数null/QA051final/全actualHOLD/全current WBS guardHOLDを維持。費用はG13.07一回だけ、利用者承認済みQA049などを取り直さず仕様も変更しない。前段の一覧診断一回はnamespace api/fileをweb packageと同一視してIndexError（対象実行0）、実tuple/完全source pathで再同定した。通常小群/commit/報告/PMO待ちで終了せず、その後も独立PGPTへ自走する。
