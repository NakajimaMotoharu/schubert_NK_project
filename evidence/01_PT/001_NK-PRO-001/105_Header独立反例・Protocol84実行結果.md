# Header個別oracle是正・Protocol84実結果（暫定）

2026-10-15、仕様104、WBS-P001-01、BUG1279/YKT1045・BUG1280/YKT1046。Production a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25は不変更、正式1964PT/53scope・工数率null・QA051final保留を維持。

## 実行と独立検証

| 実操作 | 固定source/実結果 | 独立根拠 |
|---|---|---|
| 3264-before/exec1230 | 501970e18、06:37:50～56Z、actual0。正常二Test成功＋三変異を見逃す | private payload2c631264、正常/変異全て実一Test成功。診断五caseはPT/coverage加点0 |
| 修正前起票 | aec31c214、BUG1279/YKT1045 | Production障害は主張せず、例外型と二wireの個別oracle不足を登録 |
| Test是正 | ce3ac30b7 | 構造不正をLayoutValidationExceptionへ限定、六name/wireをUI232 literal、九参照null契約・百万byte/overflow二Test追加 |
| 3264-after/exec8820 | ce3ac30b7、06:41:42～49Z、actual0。正常二成功・三変異を各実一Test AssertionFailedErrorで拒否 | payload66c7cc43、compile拒否/NoTestsでの成功0、agentなし/診断PT加点0 |
| 3266/3268-exec98150 | archive e8ece7a7 / snapshot7670335dc、06:45:17～39Z、Maven0/実84PT/17suite/174Main | 最初のkeyscan拒否ではremote三directoryなしをfresh確認。同一archive/scriptの未発行部分だけ再開。新whole/VM/Root再発行0 |
| 回収工具の末尾表示 | 外工具exit1、KeyError coverage | child0を外工具0へ読み替えない。BUG1280/YKT1046は5d73841afで修正前起票、3e2fba8bdで公開projectionのschema分離・純再現test |
| 3270/exec25608 | actual0、06:48:25Z完了。元84 XML・coverage・静的・source/原入力1896file・全Jar member一致 | servermanifest8a20d86a、原3266servermanifest6dcd5532、全原XMLhash/実testcase84/重複0/skip-failure-error-flaky-rerun0/署名済みMainに対するmember同値。Maven再発行0 |

Protocol四counter：LINE3464/3464、METHOD741/741、CLASS157/157、BRANCH1010/1010（すべてmiss0）、SpotBugs0。174はJar内全Main class物理数、157はJaCoCo CLASS counter対象数であり、同一単位と混同しない。Header実七TestをXML名の固定集合で独立確認。全六moduleの新Test統合・global四100・個別WBS受入はまだ未完。稼働中の3699はHeader新二Testを含まないため本84の全体成功へ合算0。

OS=Ubuntu26.04.1LTS、実JDK25.0.4+7-1-26.04-Ubuntu、Maven3.9.12/JUnit5.13.4/JaCoCo0.8.15/SpotBugs4.10.4.0は既固定toolchain/POM。新導入0。commandは104/工具、原Maven argvとsource/archive/hash/XML/counterは私有3270原manifestへ保持し、公開manifestは安全なprojectionのみ。

## 対象別traceと横展開

| 契約 | 独立oracle/Test ID・実method | 判定/残り |
|---|---|---|
| CommonHeader構造・長さ・参照 | H02/H03、HeaderModelTestの構造不正/metadata mismatch/正常QSE＋HDR3266-001/002 | 型限定/九null/百万byte/次byte/overflow、同84で全七成功 |
| MessageKind/InteractionKind | H01、enumsMapOnlyApprovedWireValues | Q/S/E・S/A/I全六name/wire、二wrong-wire変異を拒否 |
| ResultCode | H01、同Testの十二name/wire/profile literal | 既BUG1244の独立oracle是正を保持、101の反例・103の消費側横展開は別歴史証跡。今回Main/Testの当十二literalは不変更 |
| AuthenticationContext | H01/H03、authenticationContextValidatesAndRedacts | 長さ63/大文字/null拒否、比較・hash・redaction・公開wire accessorの期待値を保持 |
| MQ014/015/017 header | MessageCodecTest.headerEncodingMatchesIndependentUi232GoldenVector | 256byte/offset0,8,11,19,22,24,60,96,177,181,187,193,199とspaceをUI232から独立生成。response/event、破損全固定項目、body長は同classの各Testで確認 |
| MQ016 named DTO | T01/T02、PayloadTypeCatalogTest.explicitCatalogMatchesIndependentSs323NamedTypeFixture/allSixtyFourLayoutsRoundTripThroughSixtyNineExplicitNamedTypes | SS323独立TSV64行/69実型、14反復layout。共通実装費の主担当はP001-02/P002-01等から移さない |
| MQ017 field定義 | F02、LayoutFieldCatalogTest.catalogMatchesIndependentUi234To236Fixture、LayoutMetadataTest | UI233の64layout/UI234～236の389field独立TSV、gap/overlap/型/必須/offset。fixtureの原UI三SHAはfresh現origin/mainと全一致 |
| MQ018 UTF8 | FieldCodecTest.textEncodeNormalizesUtf8AndPadsWithAsciiSpace/textDecodeIsStrictCanonicalAndOptionalAware | 固定c3a9/ASCII space、日本語3byte・emoji4byte、NFD→NFC、1byte超過・不正UTF8/controlを独立literal/JDK標準UTF8で確認 |

semantic18enumは102の全name/wire独立table・36mutation拒否で広いoracleに該当せず、今回変更0。同時にheader/codec/ProtocolSemanticTypeTestを検索し、広いRuntimeException期待は今回のassertInvalid一箇所だけ。MessageCodec黄金値は変えず、個別Testの見逃しを全moduleの見逃しと誤認しない。全24DB/実Browser/CHR/他WBS固有業務の受入をこのheader純部品結果で代替0。

BUG1280/YKT1046は純五check＋実保存projectionの表示＋3270独立原証跡で有限工具範囲を閉じる。BUG1279/YKT1045は新Test集合の必要一全体統合/同source native再資格まで継続。WBS-P001-01も未認定を維持し、全criteria・同source証跡・終了依存の最終matrix照合後にのみ変更する。

## 消費・保存

0832監査着手.1/.35/.8pp、0833三反例判明後の追加是正.5/1.5/4pp、0834鍵scan一回失敗/未発行輸送再開。原/v3予算不変更、共有新窓0→1ppは他群と重なる観測であり重複加算・均等配賦0、個別実費/N/Tnull。旧窓67usedから新窓0への変化原因はUNKNOWN_EXTERNAL_CHANGE、実施側reset/課金操作0。
