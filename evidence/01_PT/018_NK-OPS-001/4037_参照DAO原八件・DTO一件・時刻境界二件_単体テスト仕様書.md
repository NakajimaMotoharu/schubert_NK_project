# 参照DAO原八件・DTO一件・時刻境界二件 単体テスト仕様書

NK-BAT-001 / WBS-P004-03、DAT009/OPS009、UI251、SS331§3.12/332/343。純JDK JDBC Proxyだけを使用し、借用ConnectionのactualDB/driver/transaction業務、ファイル/native/鍵/VM/Root/held四へ進まない。

RunReferencePortTest原8のSQL literal・timeout5・UUID/UTC2bind・全16projection・null/tx条件・zero/duplicate/missingrow・provider16箇所×旧SQL/ISE/Error三型48・例外優先18/同一SQL/suppression-disabled・割込・二借用親非共有を保持する。BUG2655の二TWR ownerだけをfinally shutdownNow＋assert await5へ有限化。期待UTCはSUTと同じ変換を使わず固定OffsetDateTime literal。PG26384で元sourceへの変更逆変換完全一致とGJF冪等を検証する。

|Test ID|class/method|fixture/input|独立期待値|
|---|---|---|---|
|PT-BAT-RUNPORT005追補|eachProviderFailureHasFixedSqlOrOriginalUnknownIdentityAndAttemptsOwnedClose|元16provider点にIAE/NPE各一つ（新32）|その同一instanceを保持し、取得済stmt/rowを一回ずつ閉じる。元三型/cleanup priorityは変えない|
|PT-BAT-RUNPORT009|literalProjectionOrAndRedactedDisplayAreIndependentOfDatabaseSetup|四Booleanの全16bit pattern|0000だけIAE、他15は各bit通り、anyReferenceは(bits&7)!=0、toStringは固定RunReferences[observation=<redacted>]。全primitiveのためnull入力は非該当、JDBC nullable columnは元004で各missingを検証|
|PT-BAT-RUN-BND001/002|BatchRunBoundaryTest原二method・source不変|UTC両端、null二つ、上下不正、submicro|4034の独立literalと同じ。定義を新規数へ重複加算せず当closure coverageに必要な同runで測定|

対象MainはRunReferenceRepository/RunReferencesとBatchRun/JdbcResourceFailures/BatchRepositoryExceptionのpure五classすべて。新11件の単一source/sessionをfresh実行する。旧PG18984原8成功はsame-byte適用だけ保存、新execへ合算しない。line/method/class/branch100%、全例外/境界/負入力、F/E/S/abort0、owned有限終了を必要条件とする。自然branch0はN/A。

Java25.0.4、JUnitConsole1.13.4、JaCoCo0.8.15、PMD7.28、Checkstyle14.3。実行は1215 qualifier compile/static、1216preflight、source固定push後1215 run <source>、1217post <source> <preflightSHA>。一回用namespace PG26386/88/90/92/94で上書き再演しない。command/環境/対象hash/OS/JDK/終了code/coverageはbegin、exit.safe.json、独立manifestへ記録する。

26388 raw22は全保持し、26389でNullAssignment一件（必要なJDBC missingcolumn入力）を個別確認。単独JUnit thread15・finite close2・fixture-localMap1・JDKProxy loader3と合わせ文脈非該当、抑制/除外追加なし。製品batch199 source/POMはnormalと同byte、645ClassStatsとBug/Missing/Error0を同じ入力へ適用確認。Main変更なし。

原追補.2/.5/1pp cap2を製造前に26380保存、元P00403/1..2 .25/.65/1.3と混ぜない。BUG2655/YKT2335の当二ownerを再試験しglobal2177/F02F03/native/実DB/全原本受入を閉じない。正式1964/53・元190新受入0・工数率null。結果4038/PG26394を後記する。
