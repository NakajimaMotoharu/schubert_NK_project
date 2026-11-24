# JaCoCo内側カウンタの整合性を確認する単体仕様

NK-OPS-001、SS354、451、WBS-G08／G01、BUG-3795、YKT-2959。原JaCoCo XMLと固定の合成reportを使う。

| Test ID | 固定入力と期待値 |
|---|---|
| PT-QA-JC-SHAPE001 | 集計が正しく、同XMLのclass、method、sourcefileの局所カウンタも未到達0なら受理。 |
| PT-QA-JC-SHAPE002 | root/packageが合格でも、class、method、sourcefileのいずれかでmissed 1なら拒否。 |
| PT-QA-JC-SHAPE003 | sourcefileのlineに命令または分岐の欠測があれば拒否。0の属性を欠く行も拒否。 |
| PT-QA-JC-SHAPE004 | method内に同種類の重複、定義外種別、非整数がある場合は拒否。 |

既存のモジュール必須四指標、package集計、同source原receiptは維持する。class間で行が重なるため、階層間の行数を単純加算しない。旧正規PG43646は構造互換だけを照合する。製品実行、再計測、旧coverageの転用なし。
