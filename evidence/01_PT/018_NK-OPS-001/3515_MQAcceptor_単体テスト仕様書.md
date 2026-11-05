# MQAcceptor 単体テスト仕様書

Program NK-OPS-001 / ArtemisAcceptorReadinessClient全method/Reader宣言interface。RD MQ-001/002/009/010・SYS-004、UI231/251/253、SS321 §2/10/13・342 §2/4/SSC130。設計正本origin/mainをfresh fetch後に確認、321 hash 2fbf317dcc6d2048abb3c8ecdc9747e7b3d46cdba4753bec6bbc9e3ace5d5d1c、342 hash 3775cb1faf0b96572f4913d06682100da1861f1d364a66f4118b03e27abf4b82。普通群826、原見積1/3/6pp・cap10、第一Vと別の通常PGPTであり個別受入へ換算しない。

Goldenは単一acceptor name=core/factoryClassName=org.apache.activemq.artemis.core.remoting.impl.netty.NettyAcceptorFactory/params={scheme:tcp,host:127.0.0.1,port:61616,protocols:CORE}/extraProps={}及びstarted=Boolean true。全7結果fieldはliteral Map、productionからexpected生成なし。callbackのClientSession markerは全methodをAssertionErrorで禁止する。旧AcceptorObjectBoundaryTest全2も当whole Sourceを証明する同一選択へ含め、既成功の確認だけの別runはしない。mixed realbroker Testはcompile/選択しない。新10+旧2で全12、normalBatch全physical2(code1+Reader1)/CRC/単exec/全@Test/四counter100/HELD四0を独立post、coverage除外なし。

|Test ID|class.method|入力・独立期待|
|---|---|---|
|OPS-ACC-PORT-001|AcceptorPolicyPortTest.exactSingletonReturnsSevenLiteralFieldsAndImmutableIndependentResults|既知singleton/7literal/immutable/順序/verify/別結果|
|OPS-ACC-PORT-002|AcceptorPolicyPortTest.nullBoundariesRejectBeforeAnyReaderAndDefaultWiringHasNoQuery|null ctor/inspect/verify/default wiringはreader前拒否|
|OPS-ACC-PORT-003|AcceptorPolicyPortTest.nonStringManagementValuesRejectBeforeStartedRead|null/Boolean/Long/List/Map応答はstarted前拒否|
|OPS-ACC-PORT-004|AcceptorPolicyPortTest.arrayCardinalityAndEveryNonObjectElementReject|配列0/2/非object全種固定拒否|
|OPS-ACC-PORT-005|AcceptorPolicyPortTest.exactAcceptorFieldsNameAndFactoryRejectOneIndependentDifference|field/key/name/factoryの一差拒否|
|OPS-ACC-PORT-006|AcceptorPolicyPortTest.extraPropertiesMustBeAnEmptyObject|extraPropsはobjectかつemptyのみ|
|OPS-ACC-PORT-007|AcceptorPolicyPortTest.everyParameterKeyValueAndObjectTypeIsCheckedBeforeStarted|params exactkeys/各値/型/null一差拒否|
|OPS-ACC-PORT-008|AcceptorPolicyPortTest.startedMustBeTheBooleanTrueAndBothReadersAreCalledOnce|startedはBoolean trueのみ/各reader一回|
|OPS-ACC-PORT-009|AcceptorPolicyPortTest.malformedJsonAndWrongStringTypesHaveFixedDiagnostics|空/壊れ/rootwrong/非String field固定拒否|
|OPS-ACC-PORT-010|AcceptorPolicyPortTest.readerRuntimeAndErrorsKeepIdentityAndSuccessfulCallsAreNotCached|未知Runtime/Error同一参照・順序/good-bad-good非cache|

旧PT-OPS-MQ-OBJ001/002はAcceptorObjectBoundaryTestのextraProps/params非object(null,array,string,number,bool)各種、started前拒否/session操作0を確認する。新fixtureの変異は対象literal存在assert付きで一fieldずつ生成する。固定失敗messageはArtemis effective broker configuration is unavailable/cause null/suppressed0。未知reader Runtime/Errorは参照保持。再送/並行の実transportは対象外、clientはworker/session/TXを所有せず、同reader反復good-bad-goodとimmutable snapshot/順序を確認する。

input008にSDK readJsonArray→StringReader→JsonLoader→明示shaded provider→fresh reader/parser/value wrapperの静的閉包を保持。SDK6同hash・planned全11jar/ServiceLoaderのJsonPointerFactory provider欠落を先確認、既Root等拒否への迂回なし。JDK classpath/service/default-property metadata activityをゼロとは主張しない。実broker/管理query/作成消費/credential/Root/DB/VM/native ABIを実行しない。

SDK JsonException/非String field ClassCastExceptionはliteral負例で確認する。IllegalStateExceptionの内部state防御catchはSDK checkClosed/parserstate等を静的確認したが動的未証明。callback由来同型例外の伝播試験と区別し、四counter100を全例外品質/451/正式完了へ換算しない。安易な到達不能認定・反射強制・coverage除外を行わない。この残存条件は3516/結果manifest補足へ明記する。

環境Linux/JDK25.0.4、JUnit1.13.4/JaCoCo0.8.15。PG18642 normal6module Main/PG18648 SpotBugs六module同Mainhashを再利用。既qualifier prepare/static/run/post acceptor、PG19248compile/19250static、source固定/push後にPG19258全12初回。実command/対象commit/原OS終端/XML/source/hash/coverage/適用性/関連BUGは827以降と3516へ記録。正式1964PT/53scope/工数null/新leaf0/同第一V HOLDを維持する。

## 828内部製造判断後の追加・同一群継続

旧source73650/PG19258の全12・47L6M1C34B100とpost0は元証拠として保持し、新sourceへ転用しない。外部API/既default readerは不変更、package-private parser Functionを注入して実SDKから独立したfaultを再現できるよう製造する。全15(旧純粋2+既新10+追加3)を新normalJarでfresh実行する。既の内部IllegalState防御catch未証明を追加で閉じる前に合格へ加算しない。

|Test ID|class.method|入力・独立期待|
|---|---|---|
|OPS-ACC-PORT-011|AcceptorPolicyPortTest.eachDeclaredParserExceptionIsRedactedBeforeStartedAndNeverRetried|parserにJsonException/ClassCastException/IllegalStateException各実体を注入、固定message/cause null/suppressed0・一回のみ・started0|
|OPS-ACC-PORT-012|AcceptorPolicyPortTest.parserNullContractIsCheckedAtConstructorAndResultBoundary|null parserはctor failfast、null parse resultは固定parsed acceptor arrayのNPE/started0。NPEをcatchし正常扱いしない|
|OPS-ACC-PORT-013|AcceptorPolicyPortTest.undeclaredParserRuntimeAndFatalKeepIdentityWithoutStartedRead|未知IllegalArgumentException/Error同一参照、started0、SDKcatchへ誤変換しない|

追加faultはfactory/transportを呼ばないSDK例外valueのみ、input008の同SDKクラス静的解析を再利用し、新normalJarのservice metadata/全Maininputをfresh照合する。PG19270六Main NullAway/PG19272六SpotBugs/19280compile/19282static/19288全15/19290post予定。group3875の原1/3/6 cap10継続、S/V付替え0。

最終source固定前829: newMain7d2cの六module build/NullAway0及び六SpotBugs0。Test重複文字列7群をTest内独立constantへ修正、最終compile19292/static19294 raw5(2definingLoader/3resourceなしmarker)個別非適用・適用0/CS0/parser0。旧19280/19282/19284/19286はcompile/staticのみで製品PT0、元証拠を残す。PG19288は予定のみ未起動、実行対象はPG19298全15/PG19300post、input012固定producer。source/CRC/全15はfresh newJarでのみ資格確認する。
