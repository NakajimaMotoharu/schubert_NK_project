# Music MVC 明示Bean配線単体仕様

NK-WEB-002 MusicMvcConfiguration constructor/musicController、RD SCR011012/FUN007/UI223235/SS311313/PG211/PT-SCR072..083、主WBS-P016-13。開始4094原.5/1.5/3 cap4固定。最新program/legacy/seedとfollowupを確認、同normalSource当component strict証拠無し・historical aggregateは再演せず保持。全Main/Controllerとwire constructorをreview、既仕様実装あり製品変更不要。

|Test ID|method|独立期待|
|---|---|---|
|PT-SCR-MUSIC-BEAN001|publicConfigurationImportsAndBeanSignatureMatchMusicComposition|公開Configuration proxyBeanMethods=false、ImportはWebMvcConfiguration正確一つ、musicController(MusicWireClient,ApiSessionInvalidHandler) Bean/戻りMusicController、Source宣言method一つ（計測等syntheticは業務宣言へ数えない）|
|PT-SCR-MUSIC-BEAN002|directFactoryRequiresBothSuppliedDependenciesAndReturnsFreshMusicControllers|client/invalid各nullを固定messageで拒否、直接factory呼出しの返却二instanceがfreshかつexactMusicController。実context singletonを推測しない|

Controller method/HTTP/Context/実画面を呼ばない、公開annotation Class参照先WebMvcConfigurationのinit/invokeも0。新test-only共通MvcBeanPortFixtureは旧SecurityContextOwnerPortFixture fa8 byteを包み、自身のcodec copyをcloseするだけ。JMS requester/Registry/ProtectedReadWireClient/MusicWireClient/Controller/mapper/invalid-handler/audit constructorだけ、sender/identifier/audit/DB/randomは呼べばfail、実session/暗号/認証/RootVM/held四無し。主担当P01613で当共通fixture製造費を一回記録、将来の利用先に共通製造費を重複加算しない。既Log三件を抽出・変更・再試験しない。

期待は公開SSのBean compositionとnonnull/fresh直接生成から独立に記載。input038 prepare/static/run <frozen source>/post、JDK25.0.4/JaCoCo0.8.15/normal20990 Main4217/six NullAway-SB20992同byte、同固定SDK CP・JDK moduleを確認、単一exec/CRC/旧exec合算・手動除外0。対象Main1physicalのline/method/class100、branch自然零N/A ratio null（0/0を100へ補完しない）。共通fixture六依存は既21202の同normalWebJar/physical/exact descriptor表を直接再利用しfresh元execへ結合、他constructorもsource限定集合で一度に差を確認。JVM/SDK metadata syscall全0は未測定。

BUG2392/YKT2137は新helper field/getter同名二件を修正前起票、原21438compile/21440raw3/21446 helperbyte保持しretainedRequester/retainedInvalidへrenameだけ。最終21448compile0/21450raw1は旧owner helper DataSource proxy定義loaderのみ非該当、適用0CS0/SB0・抑制無し。単体未実行段階は合格加算0。結果115へ元XML/TestID/argv/exit/OS-JDK/source/input/期待actual/hash・独立post/再試験を保存、元見積/費用/追加発見/手戻りを分離。実Music機能/HTTP/JMS/DB/Browser/native/CHR/QA051final/全451・新leaf/正式1964-53/工数nullは別未完。
