# 2623 Web三form 元whole二十四件・単体テスト仕様書

着手前2026-10-30 JST/Production開発source6b53efeec87f3ec36a840dd8e7759656cb4aee5c/normal14216/管理HEADae9557ac47090e580b614c9542bc58872c0f5b48・push73062真正0。群3010/開始0.5/3/5pp cap10/WBS-F03、PG-D876。後続索引を先に確認（Scenario/Log Test名直接一致0・Questionは2058あり）、三Main全527行/三元Test全854行・private helper/initializer/全callbackを読了。新fixture/新Test/Production変更0。

|Program/class・主なmethod|元Test ID/全8method|関連/独立期待|
|---|---|---|
|ScenarioSearchForm bind/toRequest/getValues/getIssues/page/isValid/redacted toString|PT-WEB214～221・web214CanonicalRequest～web221ConcurrentValidation|FUN003/UI222223234/SS313352/SSC072。固定Optional/enum/既定page1-size100、NFC期待éとUTF8 128/256境界、control/surrogate/未知field・重複/整数上限999999・negative→1、null/防御copy、64taskの固定body-n/page-n。Main canonical P01603。|
|LogSearchForm bind/date/toRequest/getter/redaction|PT-WEB278～285・web278DefaultsAndFilters～web285ConcurrentBinding|SCR014/FUN008/AUT/UI222225235/SS313352/SSC073。固定6type×3level、NFC/byte64-256/不正Unicode・binding/enum/page、JST literal→明示UTC、leap/year0000/精度/31日±1ms、null・immutable/redaction、64task。Main canonical P01614。|
|QuestionSubmitForm bind/invalidCharacter/isValid/issues/token/displayValues/toRequest/ensureOpen/close/redaction|PT-QST-FORM001～008・qstForm001～008|QST001/UI224236/SS313323322/PG-D351。質問NFC後1～4096byte/先頭space保持・末尾ASCIIspace拒否、controls/孤立surrogate、UUID文法のみで認可付与なし、欠落/重複/_csrf/未知/null、immutable/close二回と他ownercopy、100task。Main canonical P01618。|

Test三pathのcanonical/costはUNKNOWN/null維持、主関連をTest ownerへ推定しない。正常/境界/異常/例外/null/並行/所有を元wholeで扱い、実HTTP/DOM/CSRF認証・token発行消費/session/業務DB/JMS/再送は当formの試験で受入しない。各原Test methodとassertionは非改変でfixture入力・操作・期待を保持する。

独立oracle：Scenario/Logは明示literal・Optional/enum・固定JST/UTC対・0～999999の表、Production bind/date/toRequestからexpectedを作らない。QuestionはTest内goldenが4144byte空白arrayの本文offset0/長4096・UUID offset4096/長36をJDK UTF8/ASCII/arraycopyで配置、NFC期待は明示é。PayloadCodecはactual側だけ、2058の文脈を現Test全文で再確認した。実token/session/credentialは一切使用・保存せずsynthetic UUIDは元Test内だけ、公開結果はmethod名/状態/hashのみ。

依存/安全：三DTO全body、PayloadValues/FieldValueSet/FieldValue/FixedPayload、実encode経路/FieldCodec全body、固定literal389-field catalogのconstructor/parse初期化、TypedFieldValuesの使用method（text/uuid/requireUnsignedRange等）を確認。CatalogはString定数＋固定LayoutRegistryのmemory parseで外部fileを読まない。残helper全Sourceや他64layoutの再受入にはしない。自前8thread poolと固定入力・最大4097byte等のbounded値、JDK/Jar/own XML・exec以外の実DB/broker/HTTP/VM/Root/cohort/鍵/permit/native/配備/退役/実サービス操作0、元graph9を呼ばない。

command=python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14270_web_three_forms_whole_twenty_four_pt.py。元3Testのhash b681fa5d/161a06a8/20f36e96と同source normal六Jar/既Reporterを固定し新-onlyslot、JDK25.0.4 javac→JUnit/JaCoCo一session・8/8/8=24件/3suite/FES・未実行0。14272独立postは原XML/全Source/SDK/hash/実終了・8 false-result反例・単一sessionCRCと全三Source七physical（Scenario/Log各base+Code+Field、Question base）を測定。各Source四counterとmiss/自然0を保持、無意味な追加呼出/手動除外/旧exec合成なし・標準生成filter不変更。

2624結果に日時/OS/JDK/tool/branch/source/実command/exit/元独立期待・実際/counter/BUG/公開path/hashを保存、元15件は再演せず別exec保持。旧0061-400転用/正式1964-53/個別17-190/工数null/QA051final/全F03-451・既動的HOLD/原本保全・二held工具metadata前除外は不変更。未完試験/条件を合格へ加算しない。
