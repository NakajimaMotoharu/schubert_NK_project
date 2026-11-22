# SSC-477 同期Handler型と受信情報の単体仕様書

NK-MSG-001、WBS-G13.04、MQ-003／MQ-006、UI232、SS311 §6.2、SS312 §3.3、SS323、SS351、SSC-477／BUG-3574／YKT-2810。対象は `RequestContext` の生成と公開値、`LayoutHandler<Q,S>` の三操作。期待値はPR444で確定した設計と固定fixture。現Dispatcherや認証、Inbox、JMSの実結果は別工程の証拠を要する。

| Test ID | 事前条件・入力・操作 | 独立期待値 |
|---|---|---|
| PT-JMS-HCTX001 | 別の固定HTTP識別子、検証済みactorを表す値、固定受信日時、配送7を入れる | 各入力を別fieldのまま返す。表示は固定redacted文字列 |
| PT-JMS-HCTX002 | 匿名と認証済みUSERの二contextを作る | actor有無とHTTP Request ID欠落をそのまま保持。電文IDによる代用なし |
| PT-JMS-HCTX003 | 五つの必須値／Optional containerを一つずつnull、別のroot Correlation ID | 個別の不正入力を拒否。部分オブジェクトを返さない |
| PT-JMS-HCTX004 | JMS配送数1、int上限、0と負値。独立に等しいcontextと差のあるcontext | 正の範囲を保持、非正値を拒否。等値と等hash、配送数の差は不等値 |
| PT-JMS-HCTX005 | GameList用の合成型の実装を三公開操作で使う | 固定 `GAMREQ01`、具体型、配送数3。interface宣言の公開操作は設計の三つに一致 |

通常・境界・null・例外は上表。型はimmutableで並行・再送状態を持たない。呼出側の再送選択、認可、取引参加、JMS ACKは後続の同経路PTで別に検証する。Java25、固定のProtocol JAR、Role／AuthenticatedActorの現在Git source、JSpecify、JUnitを用いる。選択compile／NullAway、SpotBugs、PMD、Checkstyle、単一execのraw coverageの対象・日時・command・終了値は実行結果に記録する。JMS、HTTP、DB、QA056の四型を実行または取り込む試験は設けない。
