# Log MVC 明示Bean配線単体仕様

NK-WEB-002 LogMvcConfiguration constructor/logController、RD SCR014/FUN008/AUT002/UI225/SS313/PG218/PT-SCR099、主WBS-P016-14。開始4092原.75/2/4 cap6。最新program/legacy/seedと3486/旧024を照合、同normal sourceの当component strict証拠未登録。既CompositeMvcDeclaration別Main/歴史HTTP結果を保持し再試験しない。Mainと全constructor/当early-role経路を全文review・既仕様実装あり製品変更不要。

|Test ID|method|独立期待|
|---|---|---|
|PT-SCR-LOG-BEAN001|explicitConfigurationAndBeanDeclarationHaveExactPublicComposition|公開@Configuration proxyBeanMethods false、@ImportはWebMvcConfiguration正確一つ、logController(LogSearchWireClient,ApiSessionInvalidHandler)に@Bean/戻りLogController、Source宣言method一つ（JaCoCo等synthetic methodは業務宣言へ数えない）|
|PT-SCR-LOG-BEAN002|directFactoryRequiresBothSuppliedDependenciesAndCreatesFreshControllers|二nonnull依存それぞれ欠落はconstructorの固定client/invalid NPE、直接factory呼出しの各controllerはfresh。Spring管理singleton等を推測しない|
|PT-SCR-LOG-BEAN003|returnedControllerRejectsUserRoleWithSingle403AndNoRequestOrBackendWork|自己所有USER DTOで返されたcontrollerを一度呼び、sendError403一回/null view/model空、request getter・wire送信・ID生成・audit・session/DB無し|

公開annotation metadataだけでSpring ApplicationContext/bean管理/Controller全機能/HTTPを起動しない。@ImportのClassを参照してもWebMvcConfigurationはinit/invokeしないことを元init logで検査。Default具象依存は既SecurityContextOwnerPortFixture Gitfa8と同byteの注入constructorのみ（DB全method/乱数/ID生成はAssertionError、自身codec copy closeだけ）。LogSearchWireClient/ProtectedReadWireClient/JmsRequestReplyClient/Registryはconstructor/定数初期化だけ、sender/id supplierはfail。ApiSessionInvalidHandlerはconstructorだけ、handleを呼ばない。SessionPrincipalは公開zero64形式canary/USER/Instant.EPOCHの表示・early-role DTOで実認証/権限付与ではない。ClientAddress/body/cookie/session/鍵/DB/HTTP/server/RootVM/held四0、自己所有System.Loggerは出力したらfail。

input036 prepare/static/run <frozen source>/post、JDK25.0.4/JaCoCo0.8.15、通常Main4217/20990/six NullAway-SB20992同byte。固定既SDKのannotation署名用Spring/Thymeleaf/JMS/Session jarをPG13218 pinへ照合・ダウンロード無し、JVM/SDK classpath metadata I/O全0は非主張。Main/Test/共通helper静的raw3は定義interfaceのproxy loader各非該当・適用0CS0/SB0、抑制追加無し。新3/target1physical、line/method/class100・branch自然零N/A/ratio null、単一exec/CRC/旧exec合算・除外無し。期待値は公開SS配線とliteral403、製品生成expected無し。元XML/TestID/argv/exit/OS-JDK/source/input/期待actual/hash・全dependency method/initをstrict/独立postへ、unknown到達は未受入。結果113、障害は修正前915/916。Controller/backend/認証/実Browser/native/CHR/QA051final/全451・新leaf/正式1964-53/工数nullは別未完。
