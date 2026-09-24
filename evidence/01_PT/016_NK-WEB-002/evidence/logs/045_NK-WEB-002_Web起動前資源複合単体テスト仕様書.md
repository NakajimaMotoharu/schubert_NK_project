# NK-WEB-002 Web起動前資源複合単体テスト仕様書

Program `NK-WEB-002`、PG270、class `WebDependencyReadiness`、method `verify`、Test class `WebDependencyReadinessTest`。RD SYS-002/004・MQ-001/003、UI212/231/252、SS311/321/342、442、BUG-250/YKT-154。外部HTTP開始より前の所有資源closeがfatal `Error`のとき、通常検査失敗の固定診断へ降格しない。Current baseline/画面/電文は変更しない。

| Test ID / method | fixture・入力・操作 | 独立期待値 |
|---|---|---|
| PT-SCR-136 / `scr136FatalDatabaseCloseCannotBeDowngraded` | 公開Connection proxyで`isValid`通常SQLException＋`close`別fatal Error、通常＋通常、fatal＋fatalの3組。Broker supplierは呼出回数を保持 | 通常＋fatalでは元close Error、通常＋通常では固定redacted・causeなし、fatal＋fatalでは元検査Error同一性。各Connection close1、Broker取得0。SS342起動fail-closedとJava所有資源の重大故障優先から導出。Production methodでexpectedを生成しない |
| PT-SCR-137 / `scr137FatalBrokerCloseCannotBeDowngraded` | 正常DB Connection、JMSContext `createConsumer`通常JMSRuntimeException＋`close`別fatal Error、通常＋通常、fatal＋fatalの3組 | 通常＋fatalでは元close Error、通常＋通常では固定redacted・causeなし、fatal＋fatalでは元検査Error同一性。各JMS close1、DB connection close1、HTTP未起動 |

既存PT-SCR-113～116の実PG18/Artemis、欠落/null/無効DB、JMS停止・単独通常close/redactionを回帰する。上記通常/fatal組合せと既存正常body/単独closeで追加全条件分岐を実測する。選択command JDK25/Maven3.9.12 `./mvnw -o -pl src/schubert-nk-web -Dtest=WebDependencyReadinessTest test`、正式全reactorのrun/commit、coverage、OS/tool、input/expected/actual、sanitized RED、関連BUG、manifest/hashは046へ記録する。Failed/skippedを合格に算入しない。
