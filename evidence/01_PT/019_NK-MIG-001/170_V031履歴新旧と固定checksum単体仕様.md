# V031 履歴受入と独立checksum

WBS-P019-01.02/2、SCP-005／DAT-009、SS331 §3.2、SS343 §9、SSC-479、BUG-3721、YKT-2921。既存の `SchemaHistoryAdmission.inspect` と、V031を含む候補SQL資源が対象。

- PT-OPS-SCHEMA016。PG43276のV030 checksum `-1529040748` と、PG43658の独立CRC-32によるV031 checksum `1880247817` を固定入力とする。対象末尾二版を抜き出してfixture上の連番1・2に置き、固定schema行と合わせる。既存fixtureのV029／030ケース014は別に保持する。
- 現V031の版・script・checksumの一致は六項目がそのまま返る。旧V030止まり、同名V031のchecksum差、同版のscript差、未知V032は固定の照合エラー。各ケースで行と文を各一度解放し、借用connectionのcloseは0。期待値は固定入力から構成する。
- PG43660では、V031のUTF-8資源に対する独立CRC-32とFlyway 13.4の資源checksum実装を照合する。FlywayのDB migrationや実DBから値を得る手順は別の受入に残る。
- JDK25、既存JDBC代理、現sourceのAdmission/Row、JUnitによる単独実行。接続、署名、実DBでのV031適用結果、全scope coverage、正式451は別判定。
