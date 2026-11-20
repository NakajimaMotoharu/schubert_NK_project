# F03 新しいUser一覧・JDBC循環試験の静的結果

WBS-F03/2-2、SS352／354、PT-WEB-SCR015-COUNT-001、PT-OPS-JDBCGRAPH006～008、BUG-3473。JDK25.0.4、PMD7.28.0、SpotBugs4.10.4。対象のMainは変えていない。試験sourceは修正commit、固定入力・OS・コマンド・sha256は各manifestへ記録した。

PG41228ではUserのPMD、SpotBugs各0。JDBC fixtureの一式でPMD2。修正は訪問回数の更新と判定を分け、初回を定数で表す。既JDK next、期待同一性と再訪失敗を維持した。

PG41230は同じJDBC 3試験が成功、失敗・エラー・skip・未実行各0。PG41232は当5物理のSpotBugs・欠落・処理各0、当3methodの生L19/M3/B12/I80全到達。PG41234は修正JDBC Testに生PMD指摘・抑制・処理各0。変更のないUserはPG41228正規結果を参照し、動的・静的再実行とも0。追加した試験定義の二重計上は0。

再現は入力5622と5623の `--style-fixed`、入力5631の `--fixed`。全六製品のF03・451・実環境は未受入。

- [元PG41228](evidence/PG41228-f03-current-user-jdbc-fixture-static-v1/manifest.json)
- [再試験PG41230](evidence/PG41230-f03-jdbc-graph-fixture-expression-fixed-v1/manifest.json)
- [独立PG41232](evidence/PG41232-f03-jdbc-graph-fixture-expression-independent-v1/manifest.json)
- [修正後PMD PG41234](evidence/PG41234-f03-jdbc-current-fixture-pmd-fixed-v1/manifest.json)
