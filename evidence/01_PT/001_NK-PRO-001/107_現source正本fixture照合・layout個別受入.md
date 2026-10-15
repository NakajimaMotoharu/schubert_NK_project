# 現sourceの正本fixture照合・layout個別受入

2026-10-15、Production `a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25`、WBS-P001-02。
P001-01/03及びPGPT全体の受入を本票から推定しない。

## 実施・独立期待値

PG3284工具71a953543、純4件成功。`pg3284_protocol_canonical_fixtures.py`のfixed clean実行actual0（08:31:35.109085Z）。origin/main `756a891d9ca88643eeb3ff69f888b00fb368130d`と同byteのUI233～236/SS323を直接parseした。Productionのregistry/catalog/mapperは期待値算出へ使用しない。

- UI233全64tupleのdirection/interaction/data長/record長/最大件数/総長がfixtureと一致。独立式`256+data+record*最大件数=総長`も照合。
- UI234～236全389項目、74非空領域の名称・開始byte・byte長・型・必須・ruleが完全一致。共有PAGED48/MEDIA1024/USRMUT24は正本の明示使用先だけへ展開。全64のDATA及び存在するRECORDは開始1/連続/正の長さ/正本領域総長を検査、gap/overlapなし。
- SS323全64型対応/69 distinct typeも一致したが、これはP001-03のfield変換oracle受入ではない。
- PG3286工具355e71a62、純3件成功。既終了PG3274の原manifest SHA119eb400…、静的XML SHAae4db31e…をRO照合し、実17suite/84caseの名前・件数・XML hashを抽出。現在Test/resourceの全byteが実実行snapshot010f631baと一致する。XML properties/stdoutは公開しない。全回帰・VM・業務操作の再実行0、新規PT加点0。

原完全hash・各実Test名・fixture/hash・sourceは`evidence/provisional/PG3284-canonical-acceptance/{canonical-fixtures.json,test-witness.json,layout-acceptance.json}`へ保存する。

## P001-02の全20artifact対応

| 対象（layout package、注記以外） | Test ID／実JUnit | 独立期待値・受入判断 |
|---|---|---|
| LayoutId、LayoutDefinition、LayoutRegistry | L01～03／LayoutMetadataTest全4 | UI233全64独立tuple、1開始ID、未知version/重複/方向不一致/負長/record無矛盾/百万超過拒否、戻り集合immutable。catalogの実値をexpectedにしない |
| FieldArea、WireType、Presence、Padding、FieldDefinition | F01／layoutIdAndFieldDefinitionAreStrictAndOneBased | 固定literalの3/3/4/3種とX/N/BのSPACE_RIGHT/ZERO_LEFT/NONE、start1/end8,11,12、空名称/rule・不正長/桁overflow・type/padding不一致を型付き拒否 |
| LayoutFields、LayoutFieldCatalog | F02～03／LayoutFieldCatalogTest全3 | 正本転記389行との完全一致、64layout/空4、未知/null/変更不可、列不足/型/必須/重複/領域/間隙/長さ不整合を拒否 |
| LayoutValidationException、UnsupportedLayoutException | L02/L03/F03、上記suiteのassertThrows | 既知だが不正なmetadataと未知layout/versionの専用例外を区別。広いRuntimeExceptionで受入しない |
| FieldValue、FieldValueSet | 002のvaluesAreImmutableNullSafeAndRedacted | 固定literalのText/Numeric/Flag/Unset、元map変更・返却names変更からの防御、null container/key/value・空key拒否、比較/hash/redaction。共有試験費を再加算しない |
| WireMessage | 002のfixedPayloadIsDefensiveAndWireMessageChecksLengths | 固定headerとpayloadのdata/record長・件数の各不整合、null header/payloadを拒否。受理時同一payloadを保持 |
| PayloadTypeCatalog | T01/T02／PayloadTypeCatalogTest全5 | SS323独立64行で実data/record class名を照合、未知layout/型不一致/record有無/null拒否。mapper field意味はP001-03で別監査、catalog lookup/型契約のみ本対象 |
| LayoutPayload | MessageCodecTestの上記case及びinterface宣言 | sealed permits FixedPayload、5抽象methodのみ。実行可能methodなし、除外追加ではない。実FixedPayload経由のlength/copy契約を照合 |
| layout/package-info、time/package-info、transport/package-info | compile/NullAwayの全protocol対象 | package全体@NullMarkedのみ。実行不能な注釈宣言であり、coverage不足や試験除外ではない |

全件は485 owner P001-02の20path/hashへ対応し、他ownerのFixedPayload/codec自体の受入を本票で変更しない。専有RD行は0だが、UI233/234～236及びSS322/323の契約は上記独立原文照合を適用する。

## 個別criteria

- `contract`：上表の入力/戻り値/例外/immutableとL/F/T Test IDが、公開の実JUnit methodへ全件対応。外部wire異常とJava内部requireNonNullの即時preconditionを混同せず、NPE catchの正常化なし。
- `scope`：20path、16実行family＋1抽象interface＋3package注釈、sharedClassReferences空を照合。原inventory scope/主担当/費用は変更0。
- `quality`：PG3274実3701/542/1643、PG3276独立0/六静的0/FES-flaky-notrun0、PG3278同a9全1643Main/79resource/debug物理同byte・CRC0/native28を106及び018/881から照合。現公開同source XMLで当対象LINE/METHOD/CLASS/BRANCH missed全0。HostのProtocol全84、module四100。全PGPTでは他module603L115M470B未網羅を維持。

本対象はimmutable metadata/value/lookupで、DB/外部IO/transaction/再送副作用・所有資源を持たないため、その並行更新・再送・資源解放試験は非該当。並行readは共有codec実8worker fixtureとimmutable戻り値の検査を参照し、現VMのlive権限や業務成功は主張しない。

P001-02の終了依存は空。全三criteriaと同source/hashの厳格監査成功後だけ当leafをACCEPTEDへ変更する。正式1964PT/53scope、工数完成率null、QA051final保留、他189項目・252実行leafの範囲及び原/改訂予算は維持する。1/190という件数は工数百分率ではない。

再現：`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<pyflakes-runtime> python3 -B tools/quality/wbs_progress_audit.py`。既終了全回帰やnativeを監査のため反復しない。関連BUG1279～1283/YKT1045～1049は有限工具/oracle是正完了で、本票の全工程認定を意味しない。
