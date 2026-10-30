# 2788 Protocol7 Carrier既存exec資格結果

2026-10-30、source6b53/normal14216、branch dev-foundation。2787のcommandを一回実行。PG14862はlint0/body0、tool compile・counter inventory・session identity・coverage diagnostic全0。元PG14360の31件/7 suiteは再実行せず、同一exec/CRC/全11 classを解析した。

|項目|実測|
|---|---:|
|追加照合Source / physical|7 / 11|
|Code有 / 真のNoCode physical|5 / 6|
|NoCode Source / 未網羅Source|5 / 2|
|LINE missed / covered|4 / 24|
|METHOD missed / covered|3 / 10|
|CLASS missed / covered|0 / 5|
|BRANCH missed / covered|4 / 6|
|四100 Source / 新Product試験・JVM・受入|0 / 0|

Numeric/Flagは実counterを持ち、生成filterによるzero metadataではなかった。6 interfaceだけNO_CODE。FieldValueはL1/M1不足・B自然0、FieldValueSetはL3/M2/B4不足。0/0を100%にしない。欠測ではなく保存execの実不足として保持し、次群で独立した不足境界試験を検討する。現registry280Sourceへ未結合であり、当7を完了扱いしない。

## 証跡・独立検証

- `evidence/provisional/PG14862-protocol-carrier-seven-existing-post-v1/manifest.json` SHA256 `33a0eaa5881826498d6b9b22d4b6436e50445dedbc713ffc5c056092611b1738`。entry `5e7c471e02edc27e9945879516275bc64d4af5f52b78bb3b5f6533e0fe1b112e`。原XML31/元OS-JDK/全Source/fixtures/actual exec-session/CRC/Code/四counterを保持。
- `evidence/provisional/PG14864-protocol-carrier-independent-v1/manifest.json` SHA256 `2eaa92a143443201cb1ac3cb84a6e9d4d519ff279142cdbac06f0b6a5cdc9aff`。entry `10cc880790903d3f658325435c7f86bcc31a4fcbcb650f53f9be07e3952f927d`、lint0/body0。22 metadata反例、XML全一意、全closure/真NoCode/CRC/counter合計と不足を独立照合。
- 独立工具の最初のlintはunused importにより1/body未開始。draft importだけ除去後に上記一回bodyを実施、製品の失敗や再演ではない。

## BUG2113 / YKT1860（工具限定完了）

修正前の二回guard拒否はPG14861に保存し、元成功を変更しない。新literal helperはslice連結、PG14863の原実行結果は工具正常11/異常11、元native置換のowner2→修正版owner1、Product0。元結果の記録のための再演は0。PG14862準備generatorは固定14846から生成しactual0、生成Pythonのmain/owner一意とliteral `$` を保持して全受動後条件を完走。

YKT1860の明示9工具はPG14864の`horizontalWitnesses`で各path/hash/AST/元qualified manifest hashへ個別join。全対象が元成功時のbyteと一致し、top-level関数重複なし。以前の置換値はname/hash/countで特殊tokenなし（69blockはslice連結）のため非該当。単なる検索でなく元独立証跡と22再発防止vectorで確認した。held二ファイル、私有raw、全過去生成履歴は対象外・未保証。完了日2026-10-30、修正commitは本結果を含む最初のcommit。

正式1964PT/53scope、旧17/190、工数null、全F03/451/G07/QA051final/外部HOLDは不変更。旧exec成功の新source転用・合算なし。VM/DB/network/Root操作0。Current908/131・280Source354physical、60JVM/988methodは不変。
