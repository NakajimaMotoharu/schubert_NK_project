# MorningSuccessfulBackupProjection 原whole7 単体テスト仕様

2026-11-01 / PG-D1080 / PG17250-MORNING-SUCCESS-PROJECTION-ORIGINAL7。Production6b53不変更、保存HEAD9be59a97350a2dbe6aa2c6c0deb64a4ff0bdc844、開始2/5/9共有pp cap10・主F03。index→2515/1922と現2643 registryを照合し、元7件は当source未登録。425未登録suiteの読取棚卸しでBeforeAll等の直接markerが無かったことだけを実行許可にはせず、以下の具体calleeを確認した。

## 事前判定 PT_DEFAULT（元Test7を全部実行）

Test全250行を読了。原MDB-PROJ-1737-001～007（最初のJavadoc001～006表記より実7methodを正とする）。元MorningDatabaseSessionTest.Probe5112～5338、credential3611～14、外側literal/static fieldsとRUNを確認。Probe.openはConnection/PreparedStatement/ResultSetのJDK proxyを返すだけでDriverManagerを呼ばず、Propertiesをfake値で検査し返却後clear/カウンタ0をassertする。schema/gateもeventだけの元port。constructorは同package注入四引数、RootStartupContext/DriverManager constructorを呼ばない。実DBのURL文字列は型/値であり接続操作ではない。

元補助Testには@BeforeAll実DB/Flywayがあるので、そのwhole65を選択しない。既存classを削除・切出し・新fixtureへ改造せず、全sourceのままjavac-onlyで依存をコンパイルする。normal14216 snapshotのTest sourcepathだけを使い、Mainは固定六jar。旧Test classpathは使わない。closed reporterのMapはProjectionTest7だけでpackage scanなし、BeforeAllを持つ補助outer TestはJUnit対象0。static field初期化はliteral/BatchRun/Instant、DBは未初期化field。補助classの存在だけでTest whole65をPASSにしない。

Mainのexecute478～547/query556～659/constructor398～477/successfulBackupとsuccessfulHandle901～983を確認、既11580/82→16112/14同byte全文PG参照、3361 D-MDB001/003/005へ接続。JdbcResourceFailuresはSQL対未知順位のpure helper、InspectorDbCredentialはmemory値（17216既資格、再用成功合成0）、BatchStepAttempt/Step/Resultは既immutable値契約。実DB/Root/VM/鍵/原本Backup/JMS/native/permit/intent/権限操作0、四held/六native/RootFailed record不在と外側DB Testライフサイクル非実行を独立照合する。実DBの所有やSUCCESSをこのfake条件から認定しない。

| Test ID | 原method suffix | 入力/独立期待 |
|---|---|---|
|MDB-PROJ-1737-001|BothSqlOrdersReturnLiteralIdsAndNoMutation|手書DB/config row順2通り→ID1737001/1737002、step/attempt1/start固定、fake全resource0/commit0|
|002|EmptyMeansNoReusablePairAndIncompleteOrExtraRowsReject|0行→empty、1/3行・同step二行→固定非成功、rollback/commit0|
|003|EveryRequiredProjectionNullRejectsWithoutNpeOrLeak|十mandatory column×二row NULL→IO固定拒否、resource全帰還、NPEを成功化0|
|004|EachSemanticFieldCounterexampleRejects|日付/終了/件数/byte/error/非Backup step単一差分×二row、未来µs/非µs→拒否|
|005|PairAttemptStartAndEndMustBeOneBundle|二step attempt/start/endの各不同値→拒否、独立literal期待|
|006|EndAtObservationAndPositiveByteBoundaryRemainEligible|ended=観測時刻/byte1→ID固定のpresent、resource帰還|
|007|AllowedJdbcFailuresAndUnknownProviderIdentityCloseEveryResource|HISTORYの六故障点×SQL/ISE/Error、SQLは固定redacted IO/cause suppressedなし、未知は同一instance、resource0/commit0|

全IDの正式prefixはMDB-PROJ-1737-、loop反例数をJUnit件数へ加算0。expectedはliteral row/時刻と固定IO文字列/同一ThrowableでありProduction関数を使って作らない。null input/所有・再送/並行の全DB受入は当七の範囲外で原65/実経路に残す。

raw17250はfresh javacとone owned JUnit/session/exec、元XML7/FES・aborted/container0/全input前後hash/OSJDK/command/終了を保存。normal Batch external libraryとimplicit original helper compileを元CPへ結合、sourceを変更しない。post17252以降は全MorningDatabaseSession Source17physical/Code11/NoCode6のmissを含む四counter・CRC/session/四held六native/未選択Testの実行不在を測定する。既record PTやcounterとexecを合算しない。必要な原証跡が不足なら未確認をPASSへ加算しない。

RD OPS009/DAT009/UI251/SS331332341343、SSC104/134/200。新業務仕様/設計変更0、正式1964PT53scope・歴史17/190・工数null/QA051final/全HOLD不変更。全回帰/実DB/Rootの確認再演0、小群/commit/PMO待ちで停止せず保全条件まで継続。
