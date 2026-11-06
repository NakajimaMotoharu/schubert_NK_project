# EncryptedSessionSecurityContextRepository 自己所有interface単体仕様

Program NK-WEB-001、Main EncryptedSessionSecurityContextRepository/Deferred、RD FUN001/AUT001～004/UI226/SS314§7.2.6・331・352、WBS-P015-02。開始4076原1.5/4/7pp cap10固定。全public/package method/Deferred private stateと正常/境界/不正/null/例外/並行を12methodで同source/run全2physical確認。元DB-backed SessionSecurityContextTestやそのmethod/fixtureを抽出・実行しない。ClosedWebAuthenticationは原FOUR100/PG17950～54で既証明、依存利用だけで新source/新method二重算入0。

自己所有Servlet Proxyは要求属性/既存session取得false/closed principal read/setだけ許容し他methodはAssertionError。フレームごとのconfigured owner実object同一性を検査。既存のresource-free SpringEncryptedSessionRepository/lifecycle/codec/JDBC store constructorだけからownerを作り、DataSourceは全callback失敗、SecureRandomは独自非登録provider/SPIでseed/nextBytes/generateSeed全失敗、ID supplierも全失敗。public zero32byteはconstructor形式canaryのみ、暗号encrypt/decrypt/nonce/session発行/SQL/外部鍵取得無し、closeは自己所有copy消去だけ。helperのpackageアクセスは既constructor注入口を使い、reflection/Unsafe/外部実ownerの偽認証無し。target methodsはこのownerのidentityしか使用しない。held四は初期化/呼出/抽出無しをinit/probeとsource reviewで確認するまで未受入。

SpringSession4.1.1のSESSION_REPOSITORY_ATTRは固定jar javapでSessionRepository.class.getName()と確認し、独立fixture文字列org.springframework.session.SessionRepositoryへ固定。元の推測suffixは最初のrun前に訂正した。これはSDK契約期待でありProductionからexpectedを生成しない。principalは固定public-actor/ADMIN/context zero64/2026-01-01Z、実認証や権限付与でなくメモリDTO。型/role/名前/credentialnull/同一性は独立literal期待。

|Test ID|method|
|---|---|
|PT-WEB-SCTXPORT001|nonnullBoundariesRejectBeforeAnySessionCallback|
|PT-WEB-SCTXPORT002|requiresExactConfiguredOwnerBeforeLazyOrImmediateReads|
|PT-WEB-SCTXPORT003|emptyDeferredFrameIsLazyStableAndNeverCreatesSession|
|PT-WEB-SCTXPORT004|principalDeferredFrameUsesInitialClosedIdentityAndOneRead|
|PT-WEB-SCTXPORT005|containsDistinguishesAbsentMissingWrongTypeAndValidPrincipal|
|PT-WEB-SCTXPORT006|storedMetadataArgumentAndStateFailuresUseFixedNonSensitiveSignal|
|PT-WEB-SCTXPORT007|saveAcceptsEqualClosedIdentityAndEmptyOnlyWithoutStoredPrincipal|
|PT-WEB-SCTXPORT008|saveRejectsChangedOrRemovedPrincipalWithoutMutationOrInvalidation|
|PT-WEB-SCTXPORT009|fixateWritesPrincipalExactlyOnceOnlyInSuppliedExistingSession|
|PT-WEB-SCTXPORT010|compatibilityLoadDelegatesToFreshDeferredContext|
|PT-WEB-SCTXPORT011|failedInitialReadUnlocksAndNeverCachesPartialContext|
|PT-WEB-SCTXPORT012|concurrentSharedDeferredAndSeparateRequestCachesRemainOwned|

主観点はnonnull/configured owner・遅延session非生成・初期empty generated固定/認証closed principal固定・一回read/同じcontext返却・contains属性欠落/型・固定metadata failure・save構造等値だけ・異なる/empty identityは非変異拒否・fixate既存interfaceへのprincipal一回setだけ・7.1.1deprecated互換load（唯一SuppressWarnings deprecation、品質/coverage除外ではない）・failed初read後unlock再読・二worker16共通Deferredと別request cache分離。実SpringWebSession/Session lifecycle/フィルタ登録/DB/暗号/実Login/Logout/CSRF発行は呼ばない。

input005 prepare/static/run <frozen source>/post。JDK25.0.4、六Production Main4217/normal20990/SB20992の完全同byte再利用、Main再compile/元成功確認再演0。明示classpathはprotocol/web/Jspecific/Servlet/Spring/Security/Session4.1.1/固定Gson/errorprone/JUnitだけ、driver/Artemis/Bootstrap/Playwright無し。新Test/helper javac release25/proc:none/lintall/Werror、全対象Main/Test/helperのPMD-CS個別適用性、同normal全六static0。全2physical line/method/class/branch100、単一JaCoCo0.8.15 exec/通常JarCRC/全XML/TestID/sourceGit/producer-verifier/SDK/init/held4probeをstrictおよび独立postで照合、手動除外/旧exec合算/無意味assert無し。入力fixturehash/期待actual/command/終了code/branch/source/OS/JDK/日時/coverage/BUG/証跡hashは結果065とmanifestへ。未実行/失敗は合格算入0。実Browser/認証chain/DB/native/Root/CHR/QA051final/全451・新leaf・正式1964-53は別未受入。
