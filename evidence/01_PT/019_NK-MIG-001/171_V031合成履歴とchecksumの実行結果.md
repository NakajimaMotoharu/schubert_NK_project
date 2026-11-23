# V031 履歴照合の局所実行結果

## 原runの件数訂正（BUG-3724）

PG43292の真正JUnitは既存15件・15成功。本文の「従来の14件」は旧runのディレクトリ名を件数として表示した誤り。元のPG43660で実際に追加実行した新規1件と、その生coverageは同じ。原XML、現16件の集合との比較を下記の訂正根拠に固定する。 [PG43672](../018_NK-OPS-001/evidence/PG43672-current-v031-sixteen-single-exec/manifest.json)

PG43660、PT-OPS-SCHEMA016、WBS-P019-01.02/2。試験source `c2e391a14d2dd2ca9c2132bd1073f12fc46e9b7e`、V031本体 `5d6b7ca00a095d648c32d59228dbac671a30b55c`。実行時はJDK25.0.4、Flyway 13.4、JUnit 1.13.4。

- 既存V030の固定CRCとV031の独立計算値を使用。V031のFlyway資源checksumは `1880247817`。合成V031の正規六列は受け入れ、旧版止まり・checksum差・script差・未知版の四入力は拒否した。行・文を各1回解放し、借用connectionは保持。
- 最初のコンパイルは補助二型が不足して終了1、テスト開始0。PG43292と現の同一7物理を照合して採用し、新規一件だけ成功。従来の14件はそれぞれの元証跡を保持。書式は明示一sourceで終了0。
- 当execの生四指標は行81/93、メソッド14/18、クラス2/2、分岐42/72。部分測定を全coverageへ合算していない。実DB・署名済み履歴・全451は未認定。
- [PG43660の元試験とcheckerのhash](../018_NK-OPS-001/evidence/PG43660-ssc479-flyway-local-history-v1/manifest.json)
