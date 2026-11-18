# 4688 SSC-471 業務Outboxの必須JDBC資源と単体テスト

Program NK-MSG-002／NK-DAT-001。JdbcOutboxRepository.enqueue、claim、markSent、markFailure、型付きStatement/ResultSet解放。RD DAT-009/ASY-001/MQ-006、UI213/241/242、SS324 §8・SS332 §7 SSC-471、WBS-P004-05/2、P00602-PG03、F03/2-2、BUG3296/3297、YKT2597/2387。既仕様007と元PG21014/28は保存する。

| Test ID | Fixtureと操作 | 独立期待、終了条件 |
|---|---|---|
| PT-OUT-JDBC001～009 | 既JdbcOutboxPortTest 8、OutboxReturningIdContractTest 1を全method実行。元固定SQL、UTC・µs、rows、status、retry、null列、lease、statement/result故障、16独立ownerの全期待はそのまま。 | 元007のliteral/UTC/bind/order/SQLSTATE/identityと一致。元16worker解放はshutdownNow→await10秒の有限性を追加確認。 |
| PT-OUT-JDBC010 | 純JDK Connection proxyで文取得がnull、4入口を独立に呼ぶ。 | 既required-value契約の固定SQLDataException 22004、autoCommit→prepareだけ、affectedやJDBC呼出の成功なし、未取得closeなし、借用close/commit/rollback/configなし。 |
| PT-OUT-JDBC011 | 独立二Fixtureでenqueue/claimのexecuteQueryだけをnullにする。 | 既22004、文終了一回、ResultSetへの一切の呼出しなし、borrowed Connectionを保持。 |
| PT-OUT-JDBC012 | ResultSet.nextの元SQLを固定し、行・文それぞれのcloseへ別SQL、別Fixtureで同一行失敗の自己抑制を渡す。 | 元一次のobject identity、行close・文closeのsuppression順、一回ずつ。行が同一の場合はJDK IllegalArgumentExceptionのcauseが元一次、新一次へ文障害だけをsuppressed。 |

JDK25.0.4、Maven3.9.12、独立Expectedは上表のliteral/順序/identity。5193～5195でfresh NullAway/Checkstyle/SpotBugs/PMD、同sourceの全12、raw未除外・物理CRCと旧公開ABI、前後表を確認。関連commit/run/終了時刻・manifestとSHA、到達値、未達、障害対応は実行結果4689。Proxyは実DB、JMS、dispatcher、Root、native、保護対象を初期化しない。
