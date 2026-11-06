# Login filter入口判定単体仕様

Program NK-WEB-001/MqFormLoginFilterFactory#create/lambda・匿名filter constructor。RD FUN001/AUT001..004、UI226、SS313314352/PG-D105。群4110、WBS-P015-02原1/3/6 cap8固定。製品仕様の実装は既存、Main変更なし。元SessionFormLoginTest実PG試験は再演・部分抽出しない。

|Test ID|method|独立期待|
|---|---|---|
|PT-WEB-LGNROUTE001|fourMissingPortsAreRejectedAndFactoryReturnsFreshFilters|provider/contexts/success/failure各nullはその固定messageのNPE、同portから二返却fresh同class|
|PT-WEB-LGNROUTE002|unmatchedMethodAndExactPathDelegateOnceWithoutReadingForm|GET/HEAD/postとPOST別URI・末尾slash・null URIは後続一回/同request response、フォーム・session・address・responseの取得0|
|PT-WEB-LGNROUTE003|matchingPostRejectsEncodingBeforeFormAndUsesOnlySuppliedFailureHandler|POST /loginだけconverterへ、ISO-8859-1を固定LoginFormRejectedException/原因nullで拒否、指定callback一回、後続/他port0|
|PT-WEB-LGNROUTE004|failureHandlerIOExceptionKeepsIdentityWithoutContinuing|指定failure callbackが投げる自己所有IOExceptionは同一instanceで伝播、後続0/callback一回|

期待はUI226/SS314のexact routeと固定message/明示callback回数で独立作成。production methodでexpected生成なし。request/response proxyは列挙getter以外全てfail。owner fa8固定fixture（全DB/random/session/ID callback fail）のconstructorとcodec自己copy closeだけ、provider/probe/login clientはconstructorだけでauthenticate/exchange0。credential/password/body/content/address無し、実HTTP/session/DB/JMS/暗号/RootVM/held四無し。SDK own-JVM ThreadLocal設定固定、失敗時clearのみ。入力020に同一SDK bytecodeの公開入口/失敗callback経路review hash、既Console/JDK reviewと結合。Spring Context起動無し。

JDK25.0.4/normal20990 Main4217/SpotBugs20992六module同byte、input019 prepare/static/run <freeze>/post。新四予定、対象physical factory+匿名class二つ・ソース条件四branch全網羅を要求、全line/method/class missed0。元単一exec/normal CRC・元XML/TestID/source/hash/実環境/argv/終了・静的分類・fresh依存exact method witness/独立postを結果079へ。SDKや依存全branchを当対象100へ含めず依存whole credit0、未知初期化は不合格。未実行/失敗/skipは加算0。実Login/session/Caddy/Browser/CHR/native/QA051final/451/正式受入は別未完。

BUG2396/YKT2141：起動前Checkstyleのwildcard import1を明示五assertion importへ修正、原21618/21620とWIP21628を保持、新21624/21626へ束縛。まだUnit未実行。
