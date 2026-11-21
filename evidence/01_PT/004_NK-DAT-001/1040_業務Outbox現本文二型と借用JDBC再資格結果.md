# 業務Outbox現本文二型と借用JDBCの再資格

WBS-P004-05/2、SSC-471／SS332。既仕様PT-OUT-JDBC001～009、既Outbox資源専用ケースも含む。OutboxEntryとOutboxRequestに現本文所有修正があり、既試験を現閉包で再資格する。その他の元Java 8本・元試験2本・関連POMに差分0。

PG41410はJDK25/Mavenの元コンパイラ設定で現10 Mainを一回build。JDK Proxy現通常12/12、F/E/skip/not-run各0。元独立SQL文字列・UTC・4 statement/2 ResultSet・保有/借用資源順の期待値を維持。PG41412は真正単一exec、CRC8、現JdbcOutboxRepositoryの無除外L178/M13/C1/B40/I699全到達を独立検証。

原4所有のRequiredColumn／LogProjectionDatabaseExceptionは前証拠と現入力同一。ApiJdbcPoolとJdbcSyncRequestProcessor、実DB後条件、F02/F03終了依存、451を保留。実DB/driverを使用していない。Outbox値10件は別元runの関連証拠。両runを合算せず、正式新規0・完了価格0。

- evidence/01_PT/018_NK-OPS-001/evidence/PG41410-p00405-current-outbox-value-jdbc-v1/manifest.json SHA-256 51acd79c5cb68cd800d2a3000c1cdaf2202a76fa98726b0cc58fbd31fe365999
- evidence/01_PT/018_NK-OPS-001/evidence/PG41412-p00405-outbox-jdbc-independent-v1/manifest.json SHA-256 7be3e6e842498cd1ecf3d6ec9664056c54067877657239c9465c69ce1e17664f
