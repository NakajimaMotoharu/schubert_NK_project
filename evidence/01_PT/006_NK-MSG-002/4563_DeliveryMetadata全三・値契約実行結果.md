# DeliveryMetadata 値契約の単体実行結果

SS312/SSC153・SS351、WBS-P005-03/F03、PT-JMS-EVENT-DELIVERY-VALUE、BUG-3215。Core `47aeed19a157661363ffab5c4b5054f6b20230a1`、Unit `dfcdf44b142064a7497e3d8e87cd38b533d54b77`。PG38236の元2＋追加1、全3初回成功、失敗・エラー・skip・未実行0。固定UTCと合成ID、3fieldを独立に変えた期待、HashSetでの値契約、固定redacted診断を確認。対象の全8 Code、11 line・8 method・1 class・12 branch・68 instructionを実測、miss 0、除外0。CRC／単一execと独立XMLはPG38238。

PG38232-v2厳密Main1/Test2終了0、PG38234-v2 CS/format/SB 0。PMDの残 `equals(null)` 一箇所は明示した負値契約による非該当。初回の試験用重複literalは定数化し、Mainのhash不変。全JMS・外側producer・451は継続。

[PG38238 独立証跡](../018_NK-OPS-001/evidence/PG38238-delivery-metadata-independent-v1/manifest.json) SHA-256 `37f2f5fa0745d9023ddcf105f55d0b8ebe6d4ecd7b44777085e35129976c8dc2`。
