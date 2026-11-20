# F02 Storage追加辺の実行結果

NK-PRO-003／NK-OPS-001、WBS-F02-a、SSC-461とSS333、PT-OPS-STGRAPH-GENERIC-001／002。製品Core `a8913bc836f81632613b34243f84b7b15eb3e054` のStorage Mainは元包装入力と同じ。Test sourceは `73257d0276`。

- PG41294の当JAR二物理で新規2と必要既6の全8件成功。失敗・エラー・skip・未実行0。追加辺関数の固定順序・一回性、早いErrorの参照同一、入力graph不変を確認した。
- 初回の独立postは旧readerが現在のstrict引数に未対応。元JUnit XML・単一execと元post非0を保全し、現strict readerを固定してpostだけ回収。生L27／M10／C2／B12／I143、CRC二件一致、無除外。元JUnitを再起動していない。 [当試験・元と回収後のhash](evidence/PG41294-f02-storage-extra-edge-v1/manifest.json)
- PG41296の書式・Checkstyle・PMD指摘0。SpotBugsの生1は既`assertThrows`で固定null拒否を証明する従来の行。methodの字句同一と現生結果から新規適用0／未分類0を確認し、生指摘を保持。 [型付き結果](evidence/PG41296-f03-storage-generic-edge-typed-v1/manifest.json) [適用性](evidence/PG41296-f03-storage-generic-edge-typed-v1/applicability.json)

実JDBC・実fileと旧1引数入口は変更なし。未移管上位・FileOperation、全六製品と正式451、元項目の正式受入は継続。実行はinput/5653と5654。開始見積り0.12／0.35／0.75pp、上限1.0pp。
