# JdbcOutboxRepository 自己所有JDBC境界単体仕様

Program NK-MSG-002、WBS-P006-02、RD ASY-001/MQ-006/MQ-008、UI213/241/242、SS324§8/331§7.2/332§7、BUG2366/YKT2111。

Production method: constructors/enqueue/claim/markSent/markFailure/read/readDlqMetadata/requireTransaction/requireError。対象1Main source全physical。JDK25.0.4/Maven3.9.12、固定自己所有Connection/PreparedStatement/ResultSet callbackのみ、実DB/driver/JMS/worker/VM/Root無し。既存DB/Backup/原本/鍵/Current baselineにアクセスしない。依存DLQ/RetrySchedule/Entry/Request/RequiredColumnの実byteを利用するが、その全体資格・WBS leaf受入は別途。

期待値はProduction methodで生成しない。INSERT13列とNULL JDBC型/UTC、claim SQLのSKIP LOCKED/条件/順序/limit1..100/lease10秒、更新CASは承認SQLからliteral記述。retryは独立表1/5/30/60/300秒、±10pctと100飽和後継続を算術期待。idはDB bigint NN、wire N12の内部id追加制約は導入しない。payloadはpublic空白320byteのopaque fixtureでcodecや実電文互換合格ではない。

|Test ID|method|目的・独立期待|
|---|---|---|
|PT-OUT-JDBC001|enqueueBindsExactUtcAndOptionalDlqWithoutOwningTransaction|正常INSERT全binding13、DLQ5列/typedNULL5列/UTC、空result拒否/ownedclose|
|PT-OUT-JDBC002|claimUsesBoundedLeaseStableOrderAndImmutableRowBody|limit境界1/100、SQL、lease10秒、同時刻id昇順、空・immutable/clone|
|PT-OUT-JDBC003|requiredAndInvalidRowsFailClosedIncludingNullableAttempt|必須全12列NULL、各invalid、typedattemptNULL拒否/例外保持|
|PT-OUT-JDBC004|dlqMetadataIsAllOrNoneAndPreservesClosedProjection|all-none、or各短絡branch/各必須欠落、正DLQ5列とASYNC不整合拒否|
|PT-OUT-JDBC005|sentAndFailureCompareAndSetUseIndependentRetryTableAndCap|SENT/ERROR CAS0/1/2、retry表/±100permille/99/100継続、defaultjitter範囲|
|PT-OUT-JDBC006|argumentsAndTransactionsPreventSqlAndRespectErrorBounds|null/空/不明/limit0,101、borrowed transaction、error64/256境界・control、jitter外拒否|
|PT-OUT-JDBC007|ordinarySqlFaultsCloseOnlyRepositoryResourcesAndRemainFailures|普通SQL/set/get/execute/close故障、SQL同一性、borrowedConnection無commit/rollback/close|
|PT-OUT-JDBC008|sharedRepositoryParallelCallsKeepOwnRowsBindingsAndBody|共有Repo二worker16固有row/parameter/body/close分離|
|PT-OUT-JDBC009|sqlNullReturningIdentifierCannotBecomeSuccessfulZero|NN採番NULLが0成功にならない、独立retained回帰|

原診断PG20982はsource5d8a0869/normal20704の1件F1/OS1・資格0、全保存。実装済みのNN不備として修正前起票済み。全9method/2Test classを是正後同source一runで実行し、Failed/flaky/skipped/not-runを成功へ算入しない。LINE/METHOD/CLASS/BRANCHの全miss0、全branch/例外/境界・nullの意味を確認し、除外/exec合成なし。変更Mainはfresh六module通常compile/NullAway/静的を行い、旧20114全Java同一という前提を新sourceへ転用しない。

実行: 018/input094 normal <frozen-source> →095 static <same-source> →012 qualifier prepare/static/run/post（Outbox専用profile）→独立post。正確command・OS/JDK・日時/branch/source/入力期待actual・終了code/coverage/BUG/hashは各manifestと008結果へ記録する。JDK SQLExceptionログgetter/ThreadLocalRandom SDK activityを別途既reviewと実class-initへ結合し、全syscall0とは主張しない。四held/Root/native/CHR/全451正式未受入を維持する。

## 必須列例外oracle補正（BUG2368/YKT2113、2026-11-06）

原PG21004は9/F3/OS1の未資格。SS332のNULL補完禁止と、Main修正前からのRequiredColumn.requireValue（source fb189、SQLDataException/SQLSTATE22004）を独立根拠とし、PT003/004/009の必須NULL期待を22004へ確定する。read.idのNULL→0は既id>0のOutboxIntegrityException、DLQoriginal無しの他部分有りもOutboxIntegrityException、非null無効投影はOutboxIntegrityException＋IAE。表003の例外保持はこの区分を指す。元診断は例外0を示し欠落拒否不足自体は確認済みだが、例外型OutboxIntegrityという当初のTest仮定は誤りとして保全し、新期待の根拠へ使用しない。Production/既null契約/設計/Current oracleは変更しない。是正後の新source全9を再試験し旧6成功を流用しない。
