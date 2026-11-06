# Media MVC 閉Bean配線単体仕様

NK-WEB-002 MediaMvcConfiguration constructor/mediaController、RD FUN005..007/UI223237/SS313333/PG-D343、主WBS-P009-05。開始4106原.75/2/4 cap6固定。最新program/legacy/seed/followupは当same-normal strict証拠無しを照合、historical aggregateは保持し成功再演しない。Main/MediaController四引数constructor/MediaDescriptorWireClient constructor/MediaRangeService二constructor/WebMediaAudit constructor・version/clinitを全文review、既実装は適合・製品変更不要。

|Test ID|method|独立期待|
|---|---|---|
|PT-MED-MVC-BEAN001|publicConfigurationAndFourPortBeanSignatureMatchMediaComposition|公開Configuration proxyBeanMethods=false、ImportはWebMvcConfiguration一つ、mediaController(client/invalid/service/audit)にBean/戻りMediaController、Source宣言method一つ（synthetic計測methodは除く）|
|PT-MED-MVC-BEAN002|directFactoryRejectsEachMissingPortAndReturnsFreshMediaControllers|四依存各nullをclient/invalid/service/audit固定messageで拒否、直接factoryの二返却はfresh exactMediaController。実context singletonを推測しない|

公開metadata/constructorのみ、参照WebMVC init/invoke/Context/Controller全method/MediaDescriptorWireClient.exchange/MediaRangeService.deliver/respond/WebMediaAudit.recordを呼ばない。Range serviceはfake FileSource（呼出時AssertionError）と空Semaphoreだけ、実descriptor/file/channel/Range読取/stream/ログ無し。Media auditは自己所有NoLog（出力時fail）と固定Clock/公開version、timestamp定数初期化・version文字列検査だけ。既MvcBeanPortFixture f8/owner fa8 exact byte再利用、全DB/random/sender/ID/logger callbackをfail、自分のcodec copyのみclose、暗号/実session/credential/RootVM/held四0。共通製造費再加算0、既Range部品のPT確認再演0。

期待は公開SSの四port compositionと明示literal署名/nonnullで独立、production expected生成0。input050 prepare/static/run <frozen source>/post、JDK25.0.4/JaCoCo0.8.15/normal20990 Main4217/six NullAway-SB20992同byte、21570compile0/21572raw1は既DataSource proxy定義loaderのみ非該当・適用0CS0/SB0/抑制無し。新2・target1physical、line/method/class100/自然branch0 N/A ratio null・単一exec/CRC/旧exec合算・手動除外0。Fresh依存methodは共通十三samebyte descriptorを直接再利用し、当四新constructor/固定timestamp・versionだけを独立照合、依存whole追加0/JVM-SDK全syscall0未測定。

結果127へ元XML/TestID/argv/exit/日時/OS-JDK/source/全input/期待actual/CRC/coverage/path/hash・独立post・BUGを保存。未実行/failed/skip加算0、障害は修正前915/916。実media配送/HTTP/認証/descriptor/file/native/Browser/CHR/QA051final/451・新leaf/正式1964-53/工数nullは別未完。
