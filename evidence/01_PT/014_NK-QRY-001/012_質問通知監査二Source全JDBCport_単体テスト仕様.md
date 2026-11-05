# 質問通知監査二Source全JDBCport 単体テスト仕様

Program NK-QRY-001/NK-NTF-001、QuestionQueryAuditWriter/QuestionMutationAuditWriter全write/enum/lambda。canonical/costOwner P01403、UI224236241/SS323324332351352/SSC157/PGD330332。群864原1/3/7pp cap10、同窓前群END→当群START共有1ppは未配賦選定overheadとして一度記録し当cap内へ保守的包含、S/Vへ付替えない。元Main/seed現在byte不変更。

入力=public ID7/8/9/合成UUID、固定UTC2026-11-06T00:00:01.123456Z、匿名/USER/ADMIN actor、QUESTION/NOTIFICATION対象、2writer各閉event6種。既codecは入力DTO構築だけに使用し、期待値は固定SQL・固定catalog table・固定JSON key/value/type/不在・column/bind/UTC・close列で手書き。operation/contextはpublic zero-formatで実発行credentialではなく、canonical/HMAC/key/権限/DB/実query/cancel/deleteへ進まない。各Jdbc fixture専有、借用ConnectionはprepareStatementだけ許可（commit/rollback/close禁止）。

|Test ID|class.method|目的・独立期待値|
|---|---|---|
|QRY-AUDIT-PORT001|QuestionCriticalAuditPortTest.port001EveryQueryEventBothScopesAndActorStatesMatchesIndependentTable|query6event×2scope×3actor、固定action/category/level/outcome/step/許容JSON|
|QRY-AUDIT-PORT002|QuestionCriticalAuditPortTest.port002EveryMutationEventBothScopesAndActorStatesMatchesIndependentTable|mutation6event×2scope×3actor、capacityN9/version9001、targetTypeと禁止field不在|
|QRY-AUDIT-PORT003|QuestionCriticalAuditPortTest.port003BothWritersSanitizeNfcUsernameAndProjectNoSensitiveFields|NFC/五制御の空白化・actorRoleと入力/token/context/body非保存|
|QRY-AUDIT-PORT004|QuestionCriticalAuditPortTest.port004EveryRequiredInputRejectsNullWithoutOwningBorrowedConnection|両writer全5引数null拒否とownedStatement close|
|QRY-AUDIT-PORT005|QuestionCriticalAuditPortTest.port005OnlyOneAffectedRowIsSuccessfulCriticalAudit|affected0/2は固定SQLException、一行だけ正常|
|QRY-AUDIT-PORT006|QuestionCriticalAuditPortTest.port006AllSqlStagesAndTimeOverflowPreserveFailureAndCloseOwnedOnly|SQL各段階同一例外/closeとInstant.MAX時刻例外|
|QRY-AUDIT-PORT007|QuestionCriticalAuditPortTest.port007PrimaryCloseAndUnknownFailuresRemainFailures|primary+close抑制例外/未知Runtime-Error非正常化|
|QRY-AUDIT-PORT008|QuestionCriticalAuditPortTest.port008IndependentWorkersShareNoMutableJdbcOrJson|同時二workerのJDBC/JSON非共有、QUESTION/NOTIFICATION不変|

実環境=既host JDK25.0.4/normal六Main NullAway19630・SB19632を全input/POM/JAR一致後に再利用、新Test javac/JUnit/JaCoCo単一slot。input/001_owned_question_audit_unit.py prepare/static/run/post question_audit、新unused slotだけ。全@Test対応・FESaborted0、whole2source line/method/class/branch100/normal全physical4/CRC/単exec-session/held四probe0、合成や手除外なし。静的raw/個別適用性/抑制0、BUGは修正前起票。013結果/公開manifestへ実時刻・OS/JDK/toolhash/source/branch/command/exit/XML/coverage/期待-実際/TestID/hash/BUGを記録。

null契約=@NullMarked/normal NullAway、全境界null/Optional有無、constructor invariant・コレクションfixture必須、NPE catch正常化しない。並行は二専有workerのmemorystateだけ、再送は固定INBOX_REPLAYED audit記述だけで実Inbox判定は未実施。未受入=正規認証/ownerDB検証/削除取消/実transaction一体性とSQL構文/lock/Root/VM/native/CHR/451全体/IT-ST、個別leaf終了依存/firstVは別。
