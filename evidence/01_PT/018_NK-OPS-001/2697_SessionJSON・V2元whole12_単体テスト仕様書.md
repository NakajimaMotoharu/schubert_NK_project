# 2697 Session JSON/V2元whole12 単体テスト仕様

source6b53efeec87f3ec36a840dd8e7759656cb4aee5c / dev-foundation / Gitd266a897e857b730d33f6d80e29c61408fbd3a66。NK-WEB-001/NK-AUT-001、RD FUN-001/AUT-001..004/MQ-021、UI226/236、SS314 §7.2.1/QA049補足400..410・SS352、SSC038・PG-D094/356/913。event3087（実event番号はevents正本）見積.5/3/6pp cap10、PT_DEFAULT。PG14528/30、12method/2suite。先行古source2272/2363等は参照のみ。

元Test二class635行は全body/初期化/fixture/依存を確認済み。四target Source SessionAttributeCodec/SessionAttributes/SessionOperationToken/SessionAttributeException、全physical closureを測定。Principal/SavedRequest/AuthenticationContext/UserRole/WireEnum全body確認済み、これら依存の全面counter資格は当群で主張しない。データは公開dummy文字列/UUID/時刻、Gson strict parser/自己threadのみ。暗号/鍵/実session/HTTP/DB/API/VM/Root/graph9/cohortなし。Lifecycleは実DB初期化を要するためwholeHOLD、部分抽出/代替実行0。

|Test ID|独立oracle・境界/異常|
|---|---|
|WEB009|手書きJSON builderの順序/全属性組合せ、v2encode/legacy decode、全fieldを別assert|
|WEB010|constructor/factoryのnull要素・collection/名前NFC64byte/CSRF/用途/10件/UUID重複・immutable copy・redaction|
|WEB011|unknown/duplicate/nested/null/type/version/部分認証4fieldを拒否、固定例外/cause無/suppressed0|
|WEB012|不正UTF8/BOM/深さ超過/末尾別document/最大16384・16385byte/入力不変|
|WEB013|Unicode/quote/slash/保存先2048byte/全8用途/duplicate UUID/11件|
|WEB014|key順序逆転受入、canonical時刻/UUID/role/context/unsafe target拒否、過去時刻は認証判断せず保存|
|WEB015|10thread100task/20秒get、別入力name/target/countから手書きJSONと全field独立assert|
|TOKV201|pending constructor/時刻同値・1ns・1秒/issuedより前/null completed拒否|
|TOKV202|v2 literal golden・completed時刻三vector、encodeとdecodeを独立入力へ別適用|
|TOKV203|v1 legacy pending、root順序逆、completedAt v1混入拒否・v2write|
|TOKV204|completed null/type/unknown/duplicate/canonical/版文字列・指数拒否|
|TOKV205|pending/consumed混合10件literal golden・11件拒否/10thread100task/20秒|

期待JSON/固定値はProduction methodで生成しない。時刻・hash等Production内部変換の往復だけを独立証明としない。nullの契約違反NPEはassertThrowsで検出するがProductionがNPEをcatch正常扱いしない。finite taskとownJVM外側180秒を区別、未実行/timeout/skip/flakyはPASSにしない。

command: python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14528_session_json_v2_whole_twelve_pt.py、その後14530対応entry。normal14216の同source全input/六Jar/外部依存、static14224、JDK25.0.4/Platform1.13.4/JaCoCo0.8.15は各manifest pin。原OS/JDKprefix・終了・XML/FES・一execCRC・四Source全closure・全counter/不足を独立照合、結果2698へ。manual exclusion0/oldSource転用0/exec合成0、新Main/Test/TestID0/正式工数更新0。Main ownerP01501またはP01503とTestUNKNOWNを維持する。
