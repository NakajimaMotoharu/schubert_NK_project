# 業務MVC三設定・同core閉Bean配線単体仕様

NK-WEB-002、QA048049、SCR017/019/021、FUN001009010/AUT004/UI224226236/SS313314/PG-D357366368。対象UserBusinessMvcConfiguration/NotificationBusinessMvcConfiguration/QuestionAcceptanceMvcConfigurationのconstructorとBean method。開始4112原1/3/6cap8、P01503とP01617/19/21の一共有費用群。個別実費配賦は未知null、共通owner製造費を各画面へ再加算しない。

|Test ID|method|独立期待|
|---|---|---|
|PT-SCR-BIZBEAN001|notificationBusinessSignatureRequiresTheTokenLifecyclePort|Configuration proxyBeanMethods=false/Import WebMVC一つ/Bean NotificationController(client invalid tokens)・宣言一method|
|PT-SCR-BIZBEAN002|notificationBusinessRejectsEveryMissingPortAndReturnsFreshControllers|client/invalid/tokens各null固定message拒否・fresh exact NotificationController|
|PT-SCR-BIZBEAN003|userBusinessSignatureRequiresTheTokenLifecyclePort|Configuration proxyBeanMethods=false/Import WebMVC一つ/Bean UserAdminController(client invalid tokens)・宣言一method|
|PT-SCR-BIZBEAN004|userBusinessRejectsEveryMissingPortAndReturnsFreshControllers|client/invalid/tokens各null固定message拒否・fresh exact UserAdminController|
|PT-SCR-BIZBEAN005|questionAcceptanceSignatureRequiresReceiptAndTokenPorts|Configuration proxyBeanMethods=false/Import WebMVC一つ/Bean QuestionController(client invalid receipts tokens)・宣言一method|
|PT-SCR-BIZBEAN006|questionAcceptanceRejectsEveryMissingPortAndReturnsFreshControllers|四port各null固定message拒否・fresh exact QuestionController|

新BusinessMvcOwnerPortFixtureは同じlexical EncryptedWebSessionRepository coreをSpringEncryptedSessionRepositoryとinjected SessionOperationTokenLifecycleへ渡す。DataSourceは全callback fail、明示自己所有SecureRandomSpi/Providerは未登録で全乱数callback fail、全identifier supplier fail。public zero32bytesはcodec constructor format canaryのみ、encrypt/decrypt0、closeは自己copyだけ。receipt repository constructorは同じ不活性DataSourceを借用、SQL未実行。old SecurityContextOwnerPortFixture/MvcBeanPortFixtureは一切変更しない。新helperの共通製造は当群一回、各画面再加算無し。

Facade・Controller business constructorのみ。全Controller method、token issue/require/complete/mutate、session create/find/save、receipt read/register/transaction、invalid.handle/audit.record、JMS exchange/requester register/ID/Clock取得/乱数/暗号/実DB/HTTP/Browser/Root/VM/held四を呼ばない。WebMVCはannotation class参照だけでinit/invokeしない。新JUnit六件・三Mainのline/method/class100、natural branch0 N/A ratio null・三physical/単一exec/CRCを要求。依存common13 exact samebyte descriptorを旧Log21426と照合し、追加facade/controller三組/lifecycle injected constructor/receipt constructor/User固定PURPOSES clinitだけをfresh元execで独立照合、依存whole追加0。SDK/JVM全syscall0は未測定。

期待は上位承認済み組立契約と固定署名/null messageの独立literal、productionによるexpected生成0。input052 prepare/static/run <freeze>/post、同一Main4217/normal20990/six static20992、JDK25.0.4/JaCoCo0.8.15。GoogleJavaFormat1.36.1は既ローカルartifact/POMのruntime依存で新二Testだけformat/dry-run21660、工具hash公開manifest。初回21652 CommonMark欠落exit1はBUG2398/YKT2143へ修正前登録し元記録保持、0へ書換無し。新compile/static/Unitの真正結果・XML・日時/OS-JDK/argv/終了/入力期待actual/証跡hashを結果129へ。未実行/failed/skippedは加算0、実業務/QA051final/native/CHR/451/正式認定/個別WBSは別未完。
