# 4690 SSC-472 WebLog OutboxのJDBC必須資源単体試験仕様

Program NK-WEB-001、NK-DAT-001、WebLogOutboxRepository.enqueue/claim/markSent/markFailure、型付き解放。RD MON-003/MQ-007/MQ-008／UI242/252、SS324 §9、SS332 SSC-472、SS351。元WLG-PORT-001～020、仕様046。WBS-P004-05/2、P006-03、F03/2-2、BUG3300/3301、YKT2597/2387。

| Test ID | Fixture／操作 | 固定独立期待 |
|---|---|---|
| WLG-PORT-001～020 | 元WebLogOutboxPortTest全method、同じ合成文・行・UTC・リース・暗号を行わない公開の保持byte。 | 046の表示、行順、backoff、試行回数の上限、bind、CAS、例外、二Futureの既5秒。二worker所有はfinallyで停止と10秒待ちを確認する。 |
| WLG-PORT-021 | 4操作へStatement nullを返す別々の借用JDK JDBC proxy。 | 22004、既固定診断、AUTO→PREPAREだけ、bind/更新/行/closeなし。Connectionの所有操作へのfixtureは失敗する。 |
| WLG-PORT-022 | claimの実行結果ResultSetだけnullのJDK proxy。 | 22004、AUTO→PREPARE→QUERY→PS_CLOSE。取得済み文終了一回、行への呼出しなし、Connection所有操作なし。 |
| WLG-PORT-023 | claimの行nextと行closeで同一Throwable、別の文close失敗を発生させる純JDK Proxy。 | JDK IllegalArgumentException、causeが元一次、文の失敗だけを新一次へ抑制。順RS→PS、各一回、借用Connection不変。 |

PG39690の候補固定後、5200以降の明示プロファイルでNullAway、Checkstyle、SpotBugs、PMD、23全件JUnit XML、同じ単一execの無filter四counter・CRC、固定公開ABIと元SQL/fixture逆一致を確認する。元PG19638/PG19646は原記録のまま保持。実DB/JMS、暗号データや鍵、Webのアクセス、権限、実worker起動、QA050のLogout用retryを実行・変更しない。実環境・終了code・対象commit・証跡SHAと残scopeは実行結果4691。
