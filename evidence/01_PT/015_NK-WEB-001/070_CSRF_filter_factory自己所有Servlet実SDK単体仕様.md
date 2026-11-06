# WebCsrfFilterFactory 自己所有Servlet・実SDK配線単体仕様

Program NK-WEB-001、constructor/create、RD FUN001/AUT004/UI226/SS314§8.1/351352、WBS-P015-02。開始4082原1.5/4/7 cap10固定、seed未登録/strict pin無し/followup0。Main/callee全review変更不要。新8、target一Main/physical1、line/method/class100と自然零branchN/A（比率null、0/0補完0）。

実CsrfFilterを生成して自所有Request/Response/既存HttpSession/FilterChain/DeniedHandler interfaceで配線を検証。全frameは最初からpublic A又はB×64のCSRF値を既sessionに供給し、getSession(true)/changeSessionId/session mutationを拒否。生成/暗号/実session/DB/実HTTP/Browser/AuthContext/AppContext/Root/VM/held四操作無し。SDK constructorはdefault Xor handler/new SecureRandom objectを作るがfactoryはForm handlerへ交換。Xor.handle/nonce pathとWebCsrfToken.generateが元execで0であることを確認するまで合格しない。PRNG providerやSDK環境metadataの初期化はsyscall0とは主張しない。Child JUL CsrfFilter loggerは各Test WARNINGへ固定/元level復帰、既存app/server設定へ変更0。失敗artifactにもcanary valueを列挙しないBoolean比較を使用。

|Test ID|method|
|---|---|
|PT-WEB-CSRF-FILTER001|factoryRejectsNullDependenciesAndReturnsIndependentFilterInstances|
|PT-WEB-CSRF-FILTER002|safeMethodsExposeSuppliedUnmaskedFormTokenWithoutCreatingSession|
|PT-WEB-CSRF-FILTER003|unsafeMethodsAcceptOnlySingleMatchingFormValueAndIgnoreHeaderValue|
|PT-WEB-CSRF-FILTER004|missingMalformedWrongAndDuplicateFormValuesAreDeniedWithoutChain|
|PT-WEB-CSRF-FILTER005|reservedQueryKeyRejectsEvenWithValidFormAndEncodedKey|
|PT-WEB-CSRF-FILTER006|suppliedDeniedHandlerReceivesExactPortsAndItsIoFailureIsNotReplaced|
|PT-WEB-CSRF-FILTER007|callerChainIoFailureIsPreservedAndRequestMarkerIsAlwaysRemoved|
|PT-WEB-CSRF-FILTER008|sharedConfiguredFilterKeepsEightConcurrentSuppliedTokensRequestLocal|

独立期待=repo/handler null拒否/fresh instance、safe GET/HEAD/OPTIONS/TRACEはchain一回・既raw form token属性を非XORで供給、unsafe POST/PUT/PATCH/DELETE/BREWは単一一致formのみ許容・header参照0、欠落/空/unknown/複数不一致403一回、reserved _csrf query/plain又はencodedはform一致でも拒否、caller指定denied port/IOException identity、chain IOException identity/once-per-request marker掃除、二worker8の共有filter/request-local token分離。SDK filter単体のsafe TRACEは外部Caddy/firewallのTRACE許容を変更・認定するものではない。ExpectedはUI/SS固定値と明示callback/属性で、Production methodから生成しない。既Form handler9/repo8/denied8は依存利用だけ・旧成功確認再演0。

input011 prepare/static/run <frozen source>/post、JDK25.0.4、Main4217/normal20990/六NullAway・SB20992同byte。固定既存SDK CPにGenericFilterBean用Spring beans/context/expression7.0.9を既PG13218 pinから追加、ネット取得/POM変更無し。Test javac release25/proc:none/lintallWerror、Main/Test PMD-CS全raw個別適用・抑制無し、全source/driverGit/CP/元XML/command/OS/JDK/日時/exit/normalJarCRC/単一JaCoCo0.8.15 exec・manual除外/合成0をstrict/独立postで照合。SDK/default-handler constructorのstaticレビューと当run dependency method probe/init/held四0を結合する。未実行/失敗/skipを成功計上0、障害は修正前915/916。結果071/manifestに入力期待actual/coverage/path/hash/BUGを保存、実CSRF chain/Browser/session/Root/native/CHR/QA051final/全451/正式1964-53/新leaf/工数率は別未受入。

原PG21280 source14c8は8/F0/E1/OS1（wrong token時Utf8不足）で不合格、BUG2384/YKT2129。既toolchain security-crypto7.1.1のcodec Utf8を既aux pinでCP追加、Main/Test/POM/期待値不変更。新compile21286/static21288/全Unit21290へ固定し必要全8を再試験、旧7成功/execの合算0。新SDK追加はUTF8 utilityだけのstatic/method/initを照合、crypto処理/鍵/nonce実行として扱わない。
