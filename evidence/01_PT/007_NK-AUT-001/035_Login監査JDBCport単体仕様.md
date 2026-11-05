# Login監査 JDBC port単体仕様

Program NK-AUT-001 / LoginAuditWriter.write / AUT001・MON004・UI226/252・SS314§12/351§3-4/332・411/451、772。

|Test ID|method・入力・独立期待|
|---|---|
|PT-AUT-AUDITPORT001|successLiteralSqlAndTenBindingsExcludeSessionOrCredentialData：SS列順のliteral SQL/10bind/時刻UTC/INFO/LOGIN_SUCCEEDED/actor7/固定message-correlation UUID/IP bytes、固定JSON文字列・閉4key、statementclose1。Expectedはproductionmethodから算出しない。|
|PT-AUT-AUDITPORT002|deniedAndLockedReasonsKeepExactClosedJsonAndNullActor：内部reason4種×retry0/1/900。0は0101/LOGIN_FAILED、1..900は0106/LOGIN_LOCKED、WARN、nullactor BIGINT、DENIED、閉4key。code literalはUI234/SS323と既004SQLoracleを照合。|
|PT-AUT-AUDITPORT003|displayUsernameUsesNfcAndSingleSpaceForEveryForbiddenControl：e+結合acute＋CR/LF/TAB/U2028/U2029は独立literal「é＋5space＋Z」。10bind/update/close1。|
|PT-AUT-AUDITPORT004|allNonOneCountsRejectBeforeCallerCanCommitAndCloseStatement：MIN/-1/0/2/MAX更新件数は固定SQLException/SQLState40001、update/close1。正常1は001/002で確認。|
|PT-AUT-AUDITPORT005|providerFailuresPreserveIdentityAndTwrSecondaryWhileBorrowedConnectionIsUntouched：prepare/bind/execute/close×SQL/RTE/Error同一性とclose回数、body×close各3種9組はJavaTWR契約のprimary同一性・secondaryそのもの1件。Webのcustom例外順位を持ち込まない。freshThrowableを各組へ用いる。|
|PT-AUT-AUDITPORT006|nullCallerContractIsRejectedAndAnAcquiredStatementStillCloses：caller非null契約result/name/clock/address/connection違反はNPE拒否、既取得stmtはclose、update0。411のAPI境界不正拒否でありNPEcatchや正常化ではない。|
|PT-AUT-AUDITPORT007|concurrentWriterUsesOnlyEachCallersSeparateStatement：独立borrowedconnection二つで有限二thread、ユーザ名/レベル/closeを別値照合。callersのcommit/rollback/connectioncloseはfixtureが禁止。|

FixtureはConnection/PreparedStatement Proxy、手作成events/bindings/count/Throwableだけ。DNSなしInetAddress.getByAddress固定bytes。Successは純DTOの非発行合成context/zero UUIDをメモリ内だけで組立て、wireValueは取得せず、監査bind/JSONへの混入を閉schemaで禁止。実credential/session/鍵/DB/pool/driver/Root/native/HTTPアクセスなし。既AuthenticationServiceTestは実DB/crypto fixtureのため選択・compile・再実行しない。Mainの正常build/NullAway・六SBはPG18642/18648全入力pin一致を確認し再利用する。

全7 unique/一classを正常Main JARで新単exec/sessionへ実行し、Main全physical/CRC・全@Test/元XML・line/method/class/branch全100を独立post。staticは全finding適用性を個別判定し、抑制・任意branch除外・旧exec合算をしない。実DB監査永続化/認証整合/暗号/親WBS/V/451全体は未受入のまま。実source/run/環境/command/exit/hash/BUGは036結果へ記載。
