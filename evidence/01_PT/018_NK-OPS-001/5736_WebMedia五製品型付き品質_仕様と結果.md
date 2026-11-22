# Web mediaの五製品の型付き品質

NK-MED-001、WBS-F03/2-2-b、UI223/237、SS333 §10、既PT-MED Range・body・header／例外。対象はHttpByteRangeParser、MediaRangeService、MediaBodyStreamer、MediaDeliveryException、ContentDispositionFactory。元PG41260の通常28および独立負例1を分けて保存。数値・Range演算overflowの416とASCII unitの契約を維持。生execは元runのまま。

PG42898、2026-11-23 JST、Core e8368d22c4。現sourceとpackage-infoをroot POM同NullAwayの構成でJDK25 compile。既13物理に全byte一致し、NullAway0。実使用Protocol五物理は元SDKと現通常Protocol JARで一致。SpotBugs・Checkstyle・解析欠落各0。PMD生1は呼出内のheadersに対する指摘で、Response生成時に独立コピーするため適用外。現製品PT再演0。Web全正規JAR、実HTTP・FileStore、および全451は引き続き評価対象。[PG42898 manifest](evidence/PG42898-web-media-five-main-typed-v1/manifest.json)

2026-11-23 451適用性の追記。PG41260原28は実行事実。うちprivate constructor反射の3件とその到達は現受入根拠に使用しない。静的品質13物理と残る通常経路は別に評価する。YKT-2863、結果5745参照。
