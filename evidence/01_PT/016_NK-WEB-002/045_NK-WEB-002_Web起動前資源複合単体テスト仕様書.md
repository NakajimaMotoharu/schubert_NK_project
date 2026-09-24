# NK-WEB-002 Web起動前資源複合単体テスト仕様書

Program `NK-WEB-002`、PG270、class `WebDependencyReadiness`、method `verify`、Test class `WebDependencyReadinessTest`。RD SYS-002/004・MQ-001/003、UI212/231/252、SS311/321/342、442、BUG-250/YKT-154。外部HTTP開始より前の所有資源closeがfatal `Error`のとき、通常検査失敗の固定診断へ降格しない。Current baseline/画面/電文は変更しない。

| Test ID / method | fixture・入力・操作 | 独立期待値 |
|---|---|---|
| PT-SCR-136 / `scr136FatalDatabaseCloseCannotBeDowngraded` | 公開Connection proxy `isValid`が通常SQLException、`close`が別fatal Error。Broker supplierは呼出回数を保持 | 元Error同一性、Connection close1、Broker取得0。SS342起動fail-closedとJava所有資源の重大故障優先から導出。Production methodでexpectedを生成しない |
| PT-SCR-137 / `scr137FatalBrokerCloseCannotBeDowngraded` | 正常DB Connection、JMSContext `createConsumer`が通常JMSRuntimeException、`close`が別fatal Error | 元Error同一性、DB/JMS各close1、HTTP未起動。固定redacted通常故障との境界を独立確認 |

既存PT-SCR-113～116の実PG18/Artemis、欠落/null/無効DB、JMS停止・通常close/redactionを回帰する。追加する通常＋通常、fatal＋fatal、正常body＋fatal closeなどの全分岐/例外後条件は実装と並行して本表に追補する。選択command JDK25/Maven3.9.12 `./mvnw -o -pl src/schubert-nk-web -Dtest=WebDependencyReadinessTest test`、正式全reactorのrun/commit、coverage、OS/tool、input/expected/actual、sanitized RED、関連BUG、manifest/hashは046へ記録する。Failed/skippedを合格に算入しない。
