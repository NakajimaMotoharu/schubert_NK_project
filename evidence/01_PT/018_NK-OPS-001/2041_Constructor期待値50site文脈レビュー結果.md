# Constructor経由expected・50site静的レビュー

2026-10-26、群2330/G03.01/開始.25/1/3 cap10、current ddde。原10120のexpectedConstructorTypes非empty50site/八source。各fileは索引dd sourceからSHA不変。既2030/2031/2038/2039と重複する文脈は根拠参照し、Test/工数の二重消化へ加算しない。新製品実行0/静的source読取だけ。

|source|site数|独立根拠・補助propertyの区別|
|---|---:|---|
|AuthenticationErrorProfileTest|4|FieldValue Numeric900/retryと固定日本語/256byte境界max。Testの432byte固定goldenをdecodeした結果とliteral DTO値を比較、同decodeをexpectedへ使わない。|
|PayloadGoldenVectorTest|2|minimum/maximum PayloadValuesは独立inputを保持する往復property。layout由来入力だけで外部期待を認定せず、同methodの別assertionは独立UI TSV hashをencode結果へ比較する。|
|ScenarioRecordEncodingTest|8|4800byte固定goldenからEntry71/sequence1/line42/narration/本文/audio0をdecode、input改変後も同literal値。expectedはdecode出力ではない。|
|PayloadTypeCatalogTest|2|固定safeのFieldValue.Textとoptional/orUnsetの保存属性。戻り値を先行factoryから採取せず、入力literalを構成する。|
|SemanticFieldValueTest|15|safe/42/true/JST numeric20260902123456789/固定UUID/HEX/path/日本語をTest literal DTOとして明示し、別TypedFieldValues変換へ比較。生wire/semantic objectの独立allowlist/negativeは別assertion、DTO constructor自体の完全品質をこの比較だけで認定しない。|
|ProtocolSemanticTypeTest|15|独立enum name=wire表からFieldValue.Text、ID42/status200/elapsed999999999と0のliteral DTO。line199のvalue.wireValue由来expectedはgeneric adapter保存の補助propertyで、承認enum集合の独立根拠には用いない（別独立表を保持）。|
|JstWireTimestampTest|2|固定UTC Instant最大年と99991231235959999の独立numeric/textを比較、Production formatterでexpected生成なし。|
|LinuxStartupAdmissionTest|2|Test FixtureのA/固定dev2・ino4及びunsigned raw -1/-2をIdentity tupleへ明示。SUT withAdmittedをexpected構築へ呼ばず、raw fixture属性/descriptor/順序assertionと組合せる。実native/親所有/boot資格へ転用しない。|

当50文脈で新欠陥は認定しない。constructorを使うことだけでtautologyとも完全独立とも判定せず、比較対象のmethodと入力/出力の起源を区別した。Protocol/Storage52source索引の直接216・identifier202・constructor50は分類重複を含み、これを468PT又は全G03完成とはしない。API/Web等の全module期待値、全要求-TestID-method/branch-evidence join、同source/全coverage/正式品質・HOLDは別未完。新WBS受入0/正式1964-53/既17-190/工数null不変。
