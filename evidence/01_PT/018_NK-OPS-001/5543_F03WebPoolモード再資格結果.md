# PG40994 Web poolモードの結果

Core `2b16a8ed20778fe5896099cb4798cfd1ff96b176`、Linux、JDK25.0.4とMaven3.9.12。旧WEBPOOLMET001～008を当sourceで一回、8/8成功、失敗・エラー・skip・未実行各0。同一execで三物理の生line 45、method 23、class 3、branch 28、instruction 298すべて到達。Stateのbranchは自然分母0。公開ABI一致、ネスト二classは元物理とSHA一致。NullAway／Checkstyle／formatter／SpotBugs／PMD指摘0。

[仕様](5542_F03WebPoolモード再資格仕様.md) [manifest](evidence/PG40994-f03-web-pool-explicit-mode-v1/manifest.json)。実DBとWeb全体、原451、YKT-2751残候補は継続。
