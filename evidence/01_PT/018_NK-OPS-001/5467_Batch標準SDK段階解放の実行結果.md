# Batch標準SDK段階解放の実行結果

BATCHHOST017は修正前Core `cdb649a5f054bc2ceed72ef57e55605f14a590d1` のPG40872で不一致1。期待したGC→registry→registryに対し、GC→registry→GC→registryとなった。製品修正 `55add7630760e956c20e534dca8f6c90d93707b7` では、各ハンドルをclose成功後に保持対象から外す。失敗したハンドルの保持と、GC成功を待つregistry解放の順序を保った。

Java 25、固定Micrometer 1.17.1／Prometheus client 1.7.0、既owner fixture。PG40874で新規1と影響既存16の計17が同一実行で成功。失敗、エラー、スキップは各0。javac `-Xlint:all -Werror`、書式、Checkstyleが成功した。BatchStandardMetricSource単一classはline 42/42、method 9/9、class 1/1、branch 16/16、instruction 177/177。ほかのクラスと全451は別の判定対象。

[修正前PG40872](evidence/PG40872-batch-standard-gc-partial-close-v1-before/manifest.json) [修正後PG40874](evidence/PG40874-batch-standard-gc-partial-close-v1-after/manifest.json) [同実行coverage](evidence/PG40874-batch-standard-gc-partial-close-v1-after/coverage.xml)
