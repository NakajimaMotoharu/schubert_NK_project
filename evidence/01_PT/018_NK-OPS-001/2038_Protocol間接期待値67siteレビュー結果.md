# Protocolのidentifier期待値67site・文脈レビュー

2026-10-26、G03.01/群2322・着手.5/2/6 cap10。10120 syntax索引202 identifierのうち、先行2034のPayload12を除くProtocol67を当source d4baで点検。全選択16sourceは索引時からSHA不変、source/line/method/各文脈のhashをPG10222へ結合する。静的読取のみ・製品PT/compile/native/DB/VM/鍵/外部操作0。識別子一致だけで独立と自動認定しない。

|source（Test/helper）|site数|期待値の起源と当siteの意味|
|---|---:|---|
|AuthenticationErrorProfileTest|4|UI234/236の固定432byte、space・ASCII retry/UTF8 messageをTestのloginGoldenで直接配置。31error profileも独立TSV/固定stateから配置、encoder出力をexpectedにしない。|
|MessageCodecTest|8|QS256byteはUI232独立offset、full messageのdata/recordはTest自作配列、constructor保存/defensive copyは独立input。SS response/EI event二siteだけは往復propertyしかなく、PT-PRO-002-H01の独立golden条件の不足をBUG1806/YKT1557へ起票。|
|PayloadGoldenVectorTest|3|count/最大長はProduction layout由来であり独立wire oracleでなく補助整合性、別UI233全64TSV/最小最大goldenが外部根拠。singleton同一性はpropertyで独立wire認定へ用いない。並行expectedは既UI234手書き384byte。|
|ScenarioRecordEncodingTest|2|Test.goldenが4800byte/offset0,12,18,26,164,4260へ独立値を配置しencode比較/防御copyを確認。|
|LargeResultRecordCodecTest|11|Testの4800byte配列、9600byte連結、ゼロ10000recordとJCA SHA256から算出。descriptor識別子/pathは固定literal。Production hashからexpectedを再計算しない。|
|MediaDescriptorValidatorTest|6|独立7組extension/MIME、固定0×64hash、UTF8境界path/nameと入力type/logicalId。DTO保存属性であり同factorygetterをexpectedへ使わない。|
|HeaderModelTest|4|公開合成a/b contextと固定UUIDのvalue/equals/hash・他型拒否property。独立wire getter literalと全許容enum表は別assertion、暗号/sessionの認定でない。|
|IndependentNamedFieldOracle|5|独立fields-ui234-236/named-types-ss323/named-accessors TSV由来。priorは同named型の二layoutの独立形状一致、rawType/scalarはTestの明示semantic型表、expectedMapは独立fixtureのFieldValue。共有shape比較をwire実測へ換算しない。|
|LayoutFieldCatalogTest|2|Test resource fields-ui234-236.tsvの非comment行をexpectedとしProduction catalog/parser両者へ比較。|
|LayoutMetadataTest|1|Test resource layouts-ui233.tsvの64独立行とProductionから組み立てたactualを比較。|
|PayloadTypeCatalogTest|3|独立input PayloadValuesのencode/decode補助property、個別mapper自体の独立性は別IndependentNamedFieldOracle全69型/295component/79optional表で検査。往復だけで全mapper充足としない。|
|SemanticFieldValueTest|6|Instant.parse固定UTC、UUID.fromString固定text、0/a/b hashや固定pathの入力。Sha wrapper等の比較は保存/変換propertyであり、wireValue固定literal/negativeの独立assertionと区別。|
|JstWireTimestampTest|2|JDK LocalDateTime/ZoneIdで年0の独立Instant、固定UTC Instant.parseとJST17桁literalの双方。Production formatterの出力からexpectedを生成しない。|
|BrokerTopologyTest|1|Testの六literal tableでaddress/queue/TTL/sizeを別検査した後のenum address逆引きidentity。JMS接続/ACK実証でない。|
|FailedJmsIsolationExceptionTest|4|合成Throwable identity、equals trueでも別nodeの保持/suppressionなしの独立前提。実JMS/graph Main二へ接続しない。|
|UnconfirmedJmsRollbackExceptionTest|5|同上、Test-owned failureをcause/suppressedにidentity比較し、補助equalsと区別。rollback業務実行でない。|

65siteは当文脈で欠陥を認定せず（補助propertyを独立外部oracleと認定しない）。二不足site/一methodは修正未完、BUG1806の二独立header vectorへ進む。Storage identifier123・constructor候補50等・全要求/TestID/branch/evidence joinは残る。67を67PT又は67WBS消化に数えず、全G03/正式1964-53/17-190/工数null/HOLD不変。
