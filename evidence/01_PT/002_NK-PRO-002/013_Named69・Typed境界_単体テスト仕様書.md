# NK-PRO-002 Named69・Typed境界の当source単体テスト仕様

2026-10-25、sourcefd3d04df5710ca28f0e34f919cbc103e569a607b、主WBS-P001-03（原69named Main/TypedFieldValues/TypedPayloadValuesの担当）、関連P001-02（PayloadTypeCatalog）/P002-02（semantic）の参照追加費0。群PROTOCOL_NAMED_CANONICAL_COMPONENT20_V1、開始.5/2/6pp cap10、freshused9/残91/reset1793513544、実N/T/配賦/工数null。Program原001/P05/P06・006/PAGE・011/SEM、RD MSG001～011/SS323§3の69named/SS322§9/UI234～236。製品/既Test/既oracle/source変更0。

目的：現sourceで未実行のnamed独立field意味/optional/null/型不一致を通常PTで実施し、named69とcatalog/typed helper/semanticの全source unitを単一runで測定する。semantic15成功の確認だけを目的に再演せず、依存component全体の同一runに必要な20case/4suiteへ拡張する。旧全4222/別source資格を転用せず、旧exec unionなし。既IDの必要追試で新ID0。

PayloadTypeCatalogTestの明示6method：allNamedTypesHaveIndependentDirectionalFieldMeaning、explicitCatalogMatchesIndependentSs323NamedTypeFixture、allSixtyFourLayoutsRoundTripThroughSixtyNineExplicitNamedTypes、optionalFieldsSupportUnsetAndPresentValuesWithoutLosingWireNames、catalogRejectsUnknownLayoutsAndMismatchedDataOrRecordTypes、typedModelsAndHelpersRejectNullMissingAndWrongKinds。これに既semantic8/PAGE3/SEM3を加える。他classのTest発見/実行なし。

独立期待値：固定SS323 fixtureでlayout64/named69/record layout14、fields389の固定域を除く独立named component295/optional79/空data型4を確認する。IndependentNamedFieldOracleのwire値は手書きENUM_MEMBERS/ENUM_WIRE、固定TIME＋index、標準UUID/ASCII数字/fixture文字列だけから独立構成し、Production factoryはactual入力の生成だけに使う。期待値をその返り値で生成しない。公開constructor/公開from/公開accessorのみを、独立field順/型/名称で結び、正常/optional empty-present/各非primitive null/unknown余剰field/fields()/REDACTEDをassertする。roundtripだけを唯一のoracleとしない。型不一致/未知layout/null/collection不変/欠落/field wrong kindの期待例外は原P05に従う。

| source fixture（src/schubert-nk-protocol/src/test/resources/protocol下） | SHA-256 |
|---|---|
| named-accessors-independent.tsv | 27b9a458374f5b9edda50d78fae42ee76dabf15d8d1ecd9c94e56dbab63162d5 |
| fields-ui234-236.tsv | b07bd90705a4761ebcc97b859bd495dadaf26501fcee3b60c4edd72474a4811b |
| named-types-ss323.tsv | 9529fce86672b27a435665331648110521be6f59c5fe3fe5ca516df5234c7a76 |

fixtureは元3284 canonical正本の同byte確認済み公開TSVを当source/git blob/normal/currentで照合し、旧PT/native合格を再利用しない。実行前に対象Test/helper全文の到達処理を点検。PT_DEFAULT：既memory型/byte/時刻/enum/UUID、有限public reflectionと三公開resource読取だけ。private reflection/権限変更/アクセス回避/実credential/実auth/DB/JMS/HTTP/Root/VM/native/鍵/配備/intent/permit/RuntimeHook操作0。public factoryから生成するのは合成値型で外部資源を持たない。自己所有JUnit/新slot/XML/exec以外への書込なし。

事前条件：normal9694/current入力hash/source一致、全1843Main同byteの9702と現新Test静的0を参照、変更なしのcompile/static/全回帰反復0。新PG9708 slot/出力はABSENT、元job終端・二重起動なし。独立PG9710は元XML20/4・source/fixture/session/CRCを照合し、独立TSV69型＋4helper source unitとその全nested classを除外なしで計数する。未実行class/分岐を0missへ正規化しない。coverage100は実測まで未達、全Program/全source/451/正式/CHR/native/QA051final/全actualHOLDは別gate保持。必要BUG/YKTは修正前に登録し、通常小gate後も残PG/PTへ継続する。
