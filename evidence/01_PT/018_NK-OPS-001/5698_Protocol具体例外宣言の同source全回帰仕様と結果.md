# Protocol具体例外宣言の同source全回帰仕様と結果

BUG-3591／YKT-2826、WBS-F03/2-2-b、SS323・354、UI233～236。対象 b31a1fb86fba08e139d307061b53cfabacf1bf57、製品Core f8532c27c2666570fe450f285c5a5436aacd8e7e。十のProtocol試験sourceで18宣言を元のIO、公開反射、JCA、有限待ちの具体型へ限定。固定表、期待値、製品処理に変更なし。比較ではimportと具体宣言を除くコードの同一性を確認した。

JDK25、Maven3.9.12、対象moduleだけを固定し、元PG41526と同じoffline verifyを1回実行。171件／39 suite成功、failed/error/skipped 0。比較対象は元171件の固有classとmethod、独立表、固定wire、datetime、固定enum、合成メモリ、並行。レポート evidence/01_PT/018_NK-OPS-001/evidence/PG42624-f03-protocol-current-ordinary-171-and-unfiltered-v1/case-results.json。現規則のSpotless/NullAway、製品と対象fixtureのSpotBugs、Checkstyleは正常。PMDの生指摘は合成陰性、試験所有の有限worker、局所Mapに対応し、抑制を変更しない。

単一の現JaCoCo execを176物理classへ適用。無フィルター行3639/3639、メソッド1432/1432、実行class162/162、分岐1080/1080。元測定の合算なし。UUID、ログ、mock fixtureは独立入力を維持。実MQ、DB、Root、全6製品451及び正式受入は未判定。

- evidence/01_PT/018_NK-OPS-001/evidence/PG42624-f03-protocol-current-ordinary-171-and-unfiltered-v1/case-results.json SHA256 ae44c06ebd1906c6805621f57b261770b4033b942abc15db9884c1fe3e258798
- evidence/01_PT/018_NK-OPS-001/evidence/PG42624-f03-protocol-current-ordinary-171-and-unfiltered-v1/class-counters.tsv SHA256 5561227dcb6400fec0a69a97e9c38473e9227f60cd9a70deb984061dc6e6109d
- evidence/01_PT/018_NK-OPS-001/evidence/PG42624-f03-protocol-current-ordinary-171-and-unfiltered-v1/manifest.json
