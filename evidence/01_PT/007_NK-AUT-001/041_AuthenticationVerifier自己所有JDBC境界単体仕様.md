# AuthenticationContextVerifier 自己所有JDBC境界単体仕様

Program NK-AUT-001/WBS-P007-03、AUT001～004/MQ004、UI226/SS312§3・314§6・332§4.2/5。対象AuthenticationContextVerifier constructor/verify/inspectReadOnly/readSession/readRoleとprivate VerifiedSessionの全source・物理2class。現在503未登録/20458厳格pin無し、原AuthenticationContextVerifierTestは実PostgreSQLの別履歴として保持し再実行/抽出しない。当新fixtureは独立に手書きしたConnection/PreparedStatement/ResultSet interface Proxyだけで、JDBC driver/実DB/DataSource/DriverManager/Root/VM/HTTP/JMS/鍵/native/CHR無し。

| Test ID | method / 目的・fixture | 独立期待値 |
|---|---|---|
|PT-AUT-JDBC001|writerUsesCurrentActorLockOrderUtcBindingsAndBorrowedTransaction|固定USER/ADMINの現在rowを返す、User→Session lock→touchの正確SQL順、ASCII64aの独立SHA256/hashバインド、UTC二時刻とsession UUID、各row→statementのclose順、caller commit/rollback/close/mode変更0|
|PT-AUT-JDBC002|readOnlyPreflightNeverLocksTouchesOrChangesConnectionMode|明示RO transactionだけ、READ SQL一回/lock-touch0、autoCommit/RO四組合せのうち三つを固定Infrastructure拒否、owner不変|
|PT-AUT-JDBC003|missingRevokedExpiredAndDisabledRowsNeverReachTouch|User不在、Session不在・revoked・expiry同時刻/1ns前・disabled、write/RO双方ともcontext拒否、touch0・情報非露出|
|PT-AUT-JDBC004|nullColumnsUnknownRoleAffectedRowsAndApiNullsFailClosed|必要7column null各/未知role/affected0・2はInfrastructure拒否、constructorと両API null境界は契約拒否、SQL発行前停止/close完了、NPEをcatch正常化しない|
|PT-AUT-JDBC005|ordinaryJdbcCloseFaultsPreserveCleanupAndUnknownIdentity|8driver呼出位置の普通SQLException、row/statement二closeとcontext拒否の全4組合せ（write/RO別）、五取得済資源の個別close失敗、未知Runtimeは同一object伝播・既取得だけ一度close・caller不変|
|PT-AUT-JDBC006|parallelFreshRowsDoNotShareActorOrTransactionState|2worker32個の独立row/Connection、共有ContextHashだけが直列化、各userId/hashと一致、actor/中間state混同0・全Future/TWR終了|

OracleはSS332のSQL/ロック順とJDBC4.2 OffsetDateTime UTC/8h greatest式を手書きliteralで固定し、private SQL定数やProduction methodからexpectedを生成しない。public64a→ffe054...68ebのSHA256はPython hashlibで独立算出、実tokenではない。synthetic UUID/row/文字列のみ、実session/cookie/credential/DB dumpを読まず保存しない。現在DBエンジンのgreatest/locking/権限や実session存続をProxyで測定したとはしない。普通SQLException/closeだけで、Throwable cycle/graph/fatal injectionと既保留四classは未実行・probe/init0をpostする。

実行環境JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15/Linux、normal20704/sourcefb189を固定、全1844Java/POM同byteを検証して静的20114 D8をJavaだけ参照。prepare/static→source commit/push→単一6method run→strictpost、全物理2class/CRC/session1/全@Test/FESabort0/四countermiss0、旧exec混算・手動除外無しを必要条件とする。自然record/Java compiler標準filterは不変更、架空到達/無意味なassertionで満たさない。command=PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/012_acceptor_parser_port_qualifier.py prepare|static|run|post evidence/01_PT/018_NK-OPS-001/input/090_authentication_verifier_jdbc.json [frozenHEAD]。canonical API実受入/全007/全451とは別。

BUG2357/YKT2102原compile0/static9/Unit未実行を保存。五literalを固定定数へ共通化、profileは未使用20836/20838へ変更し旧source/結果不変。新compile0/raw4は各原行/所有でClassLoader/JUnit thread/task専有null-mapの非適用を明示し、抑制せず適用0/CS0。最初のUnitで当六方法を検証してから有限closeする。原.75/2/4cap6/計測4055開始を維持、見積/消費を固定し品質/予算/modelを変更しない。結果042へ実source/run/coverage/hash/BUGを記録する。
