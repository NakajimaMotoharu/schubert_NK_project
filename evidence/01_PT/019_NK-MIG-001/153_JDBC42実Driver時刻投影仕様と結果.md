# JDBC 4.2 実ドライバの時刻投影

NK-MIG-001、WBS-P004-05/2。正本SS332のSSC056/473、SS343、RDの業務日時・DB互換。製品候補のBootstrap POMが選ぶPGJDBC 42.7.13と、同driver POMのChecker Qual 3.55.1を使用した。Java 25.0.4で `python3 -B evidence/01_PT/019_NK-MIG-001/input/155_pg_temporal_row_driver.py` を実行した。

PT-JDBC42-001〜008の各TEXT/BINARYは同じ `TIMESTAMPTZ` を独立した形式から比較する。合成年は0001、1582-10-04、1582-10-15、1900、2000閏日、2020秋の重複する01:30の二offset、9999最終のµs。固定期待UTCは[input/154](input/154_PgTemporalRowVectors.tsv)の第4列。binaryはUTC 2000-01-01からの符号付き64bit microsecondを独立算術で再照合した。009/010はTEXT/BINARY NULLからJava null、およびwasNull=trueを期待する。

JVMの既定UTC／Asia/Tokyo／America/New_Yorkで、実 `PgResultSet.getObject(1, OffsetDateTime.class)` を実行した。各zone 18観測、合計54/54一致、3 JVM終了0、警告を許容しないcompile終了0。実装済み2箇所の既87件の独立proxy試験は別runとする。

実DB接続、PostgreSQLの実session timezone、実schema、pool、権限、bind後のSQL／transactionおよびclose-on-completionは未実施。合成行の所有終了はdriverの行処理だけを用いた。負例としてNULLを確認。元fixture不足はBUG-3392/3393とPG40604の実終端を保存した。このSDK試験は製品PT数や451 coverageへ加算しない。

[PG40606](../018_NK-OPS-001/evidence/PG40606-p00405-jdbc42-vendor-row-corrected-v1/manifest.json)
[PG40608 独立照合](../018_NK-OPS-001/evidence/PG40608-p00405-jdbc42-vendor-row-independent-v1/manifest.json)
