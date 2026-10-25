# Layout/field catalog七methodの静的意味対応

1955の開始見積り・scopeを維持。現source64446、対象は不変metadataでありDB/JMS/再送/transaction/実ownerの受入ではない。以下は親のsource読取レビューで、別処理による参照照合や静的literal比較は動的PTの独立再実行ではない。

| class | method | 既存Test ID family | 独立期待値・根拠 | 適用範囲と未確認 |
|---|---|---|---|---|
| LayoutMetadataTest | registryMatchesIndependentUi233Catalog | PT-PRO-001-L01, PT-PRO-001-L03 | UI233由来TSVの64 tupleをexpectedとして読込。ID/QSE/interaction/data/record/count/totalの順序付き完全一致、version1と未知2、変更禁止を明示 | Production registryはactual側だけ。元3284のfixture根拠は現在byte同一で再利用、旧PT結果は移さない。全分岐資格ではない |
| LayoutMetadataTest | registryRejectsEmptyNullDuplicateAndKindMismatches | PT-PRO-001-L02 | 空・null集合/要素、重複、REQ/RSP/未知識別子、QWK eventとQSB asyncの相違を固定構築し専用例外を期待 | helper dは入力構築だけでexpected生成でない。最後の正常request受理は例外なし確認。全識別子異常の網羅を主張しない |
| LayoutMetadataTest | layoutDefinitionChecksEveryLengthAndKindInvariant | PT-PRO-001-L02 | SS322の256+8+10×countから固定264/274/284、count -1/3、version2、六桁超過、record零組合せ、百万超過、整数overflow、明示total257、event/internal組合せ | Mainの計算法をexpectedに呼ばない。nullは内部constructor preconditionのNPE期待であり、外部wire正常処理でもNPE catchでもない |
| LayoutMetadataTest | layoutIdAndFieldDefinitionAreStrictAndOneBased | PT-PRO-001-F01, PT-PRO-001-L02 | 固定ASCII8文字・辞書順、1始まりend8/11/12、enum数3/3/4/3、blank/零/overflow/不一致end・padding拒否 | enum数だけで意味を認定せずpadding switchと照合。generic javaTypeをcatalog変換のLong専用契約へ拡張しない。null全parameter網羅は本method単独で主張しない |
| LayoutFieldCatalogTest | catalogMatchesIndependentUi234To236Fixture | PT-PRO-001-F02, PT-PRO-001-L03 | UI234～236由来389行TSV、64layout/空4、空白prefix、unknown/null/immutable、X/N/B→String/Long/Booleanを明示 | Mainは独立のJava textblockでfixture classpath resourceを読まない。単純なparse/tsv自己roundtripだけに依存しない。60有項目layout/74非空areaの範囲であり全codec/mapper受入でない |
| LayoutFieldCatalogTest | parserRejectsMalformedUnknownAndDuplicateRows | PT-PRO-001-F03 | 手書き8列入力の不足、未知layout/HEADER/型/必須区分、F属性許可名、非整数/非正/blank/同area同名/gapを個別例外期待 | unknown layoutはUnsupportedLayoutException、その他はLayoutValidationException。NPEはnull契約のみ。重複名とoffset重複の同一扱いをしない |
| LayoutFieldCatalogTest | layoutFieldsRejectWrongAreaGapLengthAndNull | PT-PRO-001-F03, PT-PRO-001-F01 | DATA長1の固定layoutに正しい1byteとwrong area/start2/length2/不要recordを構築、immutable/null集合・要素を期待 | List.copyOfによる入力固定とvalidateAreaを読取照合。並行可変状態や再送状態を含まない。実並行PT成功ではない |

## 純粋fixture証拠の再利用境界

元`001_NK-PRO-001/evidence/provisional/PG3284-canonical-acceptance/canonical-fixtures.json`のSHA-256は`0e9a0c22816212b1a019e904f7ba46a67980b51490768efedf4a9d2d2817b3cd`。その五設計文書は現origin/main8b91944df、三TSVは現source/snapshotとbyte同一。64 tuple/389 field/74 area/64 named mapping/69型の既存純粋fixture根拠だけを再利用する。old sourceQualified=true、a9 source、旧受入/PT/native/coverageは現在へ転用しない。元toolは旧stage系をimportするためmainを再演しない。

現在sourceのRegistry標準宣言64とCATALOG_TSV389を、固定文法の静的source literal比較で独立TSVへ結ぶ。Java initializer/constructor、Production parser/codec、JUnitは実行しない。未知構文・escapeは推測解釈せず失敗させる。これは実行PTの代替PASSではなく、expectedがProduction生成でないことと現sourceのliteral対応の追加根拠である。

関連は既Program001の六family/十method-family関係。family全体/全branch/四counter100/新Test ID/正式受入への加算0。SS323 named-typesはfixtureのbyte再認証だけで全named mapperの意味確認は未実施。1953のHeader enum wire値対応を参照するが再計上0。新規製品障害は本読取範囲では確認なし、未確認を非該当や成功へ変換しない。
