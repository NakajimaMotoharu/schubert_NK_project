# Question MVC 明示Bean配線単体仕様

NK-WEB-002 QuestionMvcConfiguration constructor/questionController、RD SCR022023/FUN010/UI224236/SS313/PG-D350/PT-QRY-HTTP008009、主WBS-P016-18。開始4100原.5/1.5/3 cap4固定。最新program manifest/旧strict/seed/followup0・当same-normal strict証拠無しを照合、historical aggregateは保持して確認再演しない。Main/QuestionController・QuestionWireClient constructorを全文review、既実装は設計に適合・製品変更不要。

|Test ID|method|独立期待|
|---|---|---|
|PT-SCR-QUESTION-BEAN001|publicConfigurationImportsAndBeanSignatureMatchQuestionComposition|公開Configuration(proxyBeanMethods=false)、ImportはWebMvcConfiguration一つ、questionController(QuestionWireClient,ApiSessionInvalidHandler)にBean/戻りQuestionController、Source宣言method一つ（計測syntheticは宣言へ数えない）|
|PT-SCR-QUESTION-BEAN002|directFactoryRequiresBothSuppliedDependenciesAndReturnsFreshQuestionControllers|client/invalid nullは固定message NPE、直接factoryの二返却がfresh exactQuestionController。管理singleton推測無し|

公開metadataと2引数read constructorのみ（receipts/tokensはOptional.empty、4引数business constructorやtoken lifecycleは未呼出し）、WebMvcConfiguration参照先init/invoke/Context/Controller method/HTTP/JMS0。既MvcBeanPortFixture f8dとSecurityContextOwnerPortFixture fa8はexact byte再利用で共通製造費再加算0、所有するcodec copyだけcloseし、sender/identifier/logger/DB/randomは呼べばfail。constructor局所validation/定数を除き実session/暗号/鍵/認証/RootVM/held四無し。期待は公開SSとliteral署名/nonnullから独立作成、production expected生成無し。

input044 prepare/static/run <frozen source>/post、JDK25.0.4/JaCoCo0.8.15/normal20990 Main4217/six NullAway-SB20992同byte。21510compile0/21512static raw1は既helper DataSource proxy定義loaderのみ非該当、適用0CS0/SB0/抑制無し。新2/target1physical、line/method/class100・自然branch0 N/A ratio null、単一exec/CRC/旧exec合算・手動除外0。Fresh依存methodは既十三samebyte normal/physical/descriptorを直接再利用＋当二constructor exactを一度に検証し、依存whole追加0。JVM/SDK metadata syscall全0は未測定。

結果121へ元XML/TestID/argv/exit/日時/OS-JDK/source/全input/期待actual/CRC/coverage/path/hash/独立postとBUGを保存、未実行/失敗/skipは合格加算0。実質問検索/送信/取消/token機能/Controller全branch/実HTTP/Browser/JMS/DB/native/CHR/QA051final/451・新leaf/正式1964-53/工数nullは別未完。障害は修正前915/916。
