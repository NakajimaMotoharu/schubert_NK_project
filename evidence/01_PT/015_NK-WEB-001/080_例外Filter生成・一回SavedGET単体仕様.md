# 例外Filter生成・一回SavedGET・限定単体仕様

Program NK-WEB-001、WBS-P015-02、FUN001/AUT001..004/UI221226/SS313314§7.2・351352/PG-D112。対象whole Main WebAccessExceptionFilterFactory constructor/create。旧Spring chain/実DB/HTTP/認証・session回帰のmethodを抽出しない。新whole WebAccessExceptionFactoryPortTestはresource-freeの実handler/cache/loggerと自己所有Mock Servletだけでconfigured SDK filterの振舞いを観測する。既No backend SecurityContextOwnerPortFixtureは同byte再利用、sessionを発行・取得・暗号化保存しない。

|Test ID|入力/操作|独立期待|
|---|---|---|
|PT-WEB-EXCFACT001|factory null handlerと同handler二回生成|nullはNPE「handler」、実ExceptionTranslationFilter二つは別object、public getAuthenticationEntryPointは同じhandler、afterPropertiesSet正常|
|PT-WEB-EXCFACT002|chainが単純AuthenticationExceptionを返すGET /scenarios?page=2|302/Location /login、Mock Servlet sessionへ相対String一つだけ保存、getSession(true)一回・属性write一回、標準DefaultSavedRequestや任意object保存なし。audit action AUTHORIZATION_DENIED/reason UNAUTHENTICATED一回|
|PT-WEB-EXCFACT003|同例外でPOST/通常AJAX GET/media GET、及びempty own contextでAccessDeniedException|前3vectorは403/Location無し/Mock session取得保存0/reason UNAUTHENTICATED、後1は設定されたAccessDeniedHandlerを観測する403/reason ROLE・認証actor無しの限定境界。実user roleや認可成功を認定しない|
|PT-WEB-EXCFACT004|普通chain正常帰還と非security IOException|同じreq/responseでchain一回、正常statusと元IOException identityを保持、session/audit0|

期待はUI221のGET遷移とPOST/AJAX/media拒否・SS314閉SavedRequest/二重保存禁止・351の独立固定action/reasonで、Productionからexpected生成なし。Mock sessionはpublic固定ID/heapだけ、属性setterがsavedRequest以外又は非Stringを拒否し、default framework cacheが二重保存すれば失敗する。実SessionRepository/暗号row/Cookie発行は行わない。requestに同owner repositoryの内部attributeとpublic TestNet IP/固定UUIDのWebRequestContextを設定するがCaddy/Root/API認証の資格にはしない。ユーザprincipal/認証token/credentialを作らない。own ThreadLocal SecurityContextは空のまま前後clear、通常のSDK例外は単純acyclic fixtureで、保留四型/失敗cohort/拒否操作の再演でない。

PT_DEFAULT：own host有限JUnit一回、Web/protocol/storage normal22084と固定SDKのみ。spring-test7.0.9は既20318原manifestのhashへ束縛、security7.1.1/JUnit1.13.4/JDK25.0.4/Gson既版。DBdriver/broker server/API/bootstrap/batch runtimeなし、API/held四・Root/native/VM/秘密key/実HTTP/network接続/実暗号・session backend呼出0。mock Servletのheap属性と自前logger callbackは必要な観測として実行し、「全session/log操作0」と偽称しない。DB/random callbacksは既fixtureで常に禁止。 public signature/SDK metadataのみ、private reflection/既filter設定の上書きによる偽観測0。

正常/例外/null/複数要求境界を全4methodで確認、対象factoryはstatelessで再送/並行業務非該当、支援側の部分counterはwholeに算入しない。全normal physical一sourceのline/method/class未達0、branchは命令分岐なし/N-Aとし100補完しない。Test javac lint/Werror/PMD/CS/GJF、同byte Main22084/86静的を再利用。独立postはsource/Git/実XML/終了/全Code・CRC/一exec/classinit/許可method/SDK/原静的適用を照合してからlimited資格を計上する。実認証/role/DB/Browser/全chain/CHR/451/親leaf未受入は維持。

通常候補WebSessionFilterFactoryのcookie設定は返却public APIからserializerを取得できず、正規のcookie後条件はDB-backed SessionFilterが必要。private field読取や別resolverへの置換で同契約を偽試験しないため当範囲HOLD、Cookie要件SameSite=Lax等は変更しない。残作業全体の枯渇とは認定しない。

元/v3/v4/v5不変、群開始1/3/6pp cap8。Test/source資格は実成立分だけ、開始時unique392/whole89・正式1964/53・工数null/QA051finalを維持する。
