# 1664 API Outbox観測Repository 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171-MON005～013/UI252/SS331351/PG-D547/group1885。OutboxObservationRepository.read/status・Snapshot constructor/全生成5method、自己所有JDBC proxyのみ。実DB/driver/role/Clock/VM/Root/keys/配備操作0、承認SS331の既mq_outbox status三値/created_at NNを固定SQLで読む部品の製造。

固定SQL oracleはTest独立文字列 `SELECT status, COUNT(*) AS row_count, MIN(created_at) AS oldest_created_at FROM schubert.mq_outbox GROUP BY status`。borrowed readonly/non-autoCommit/READ_COMMITTEDのみ、timeout1s。queryが成功し全RS/PS close後だけsnapshotを返し、欠落groupだけcount0/age0（最古row無しの空集合同定値）、失敗/SQLNULL等を0正常化しない。age=caller asOf−MIN(created_at)、futureを拒否/時刻補正0。型はgetObject(OffsetDateTime.class)→Instant、実PG driverの互換・期限/source/asOf真正性は後続未受入。

| Test ID / outboxDb method | fixture・操作・独立期待値 |
|---|---|
| OUTBOXDB001 / 001ShuffledRowsHaveLiteralCountsAndAgesAfterReverseClose | 順序ERROR/PENDING/SENT・件数7/3/5・epoch差11/2/4秒、全counts/age固定期待・RS→PS close各一回/Connection変更0 |
| OUTBOXDB002 / 002EmptyAndSparseGroupsAreZeroOnlyAfterQueryCompletes | 空/単PENDING=Long.MAX_VALUE・created=asOf、未知ではなくquery成功後の欠落status0/zeroage、sum/long overflow処理を推測しない |
| OUTBOXDB003 / 003NullAndWrongTransactionNeverPrepareOrMutateBorrowedConnection | conn/asOf null・autoCommit/readOnly/isolation不適合・各getterSQL故障、prepare0/不正Connection変更0 |
| OUTBOXDB004 / 004NullUnknownAndDuplicateStatusCannotReturnPartialValues | status SQLNULL/未知canary/重複、固定checked拒否・部分snapshot返却0・全close |
| OUTBOXDB005 / 005NullNonpositiveCountAndNullOrFutureTimeAreNotKnownZero | count SQLNULL/負/0group、timestamp null/future、固定checked拒否・全close |
| OUTBOXDB006 / 006TypedOffsetTimeHasExactUtcAndCalendarBoundaryOracles | +09:00 literal08:59:58.5→epoch差1.5s、0001→9999末尾独立暦差315537897599.999999s、同時刻0、typed列名/型assertでTimestamp誤読拒否 |
| OUTBOXDB007 / 007NullResourcesAndAcquisitionFailuresNeverRetryOrCloseConnection | nullPS/nullRS、prepare/timeout/executeでSQL/Runtime/Error元同一throw・取得済PSだけclose・一発行 |
| OUTBOXDB008 / 008ReadAndCloseFailuresPreserveOriginalIdentityAndSuppressedOrder | next/status/count/wasNull/oldest/RSclose/PSclose×SQL/Runtime/Error、元同一throw・RS→PS/重複0、primaryにRS/PS failureが順序通りsuppressed |
| OUTBOXDB009 / 009ParallelBorrowedConnectionsHaveNoCrossOwnerState | 64別owner connection/各pending1～64・age1～64秒/error2・age4/sent0、混線0・全close |
| OUTBOXDB010 / 010SnapshotInvariantsAndGeneratedContractsUseIndependentFixedValues | counts(3,5,7)/ages秒(2,4,6)、self/同値/null/他型/二component差/accessor、独立hash96447・固定nested全fieldtext・constructor各null拒否 |

暦oracleは公暦0001～9999の3652059日から末尾µsを差し引いた固定値で、production/Duration.betweenでexpectedを作らない。record hashはcounts3045/ages2052を固定primitive/JDK Duration31foldから独立算出、31*3045+2052=96447。内外recordの当methodをexpected生成に使わず、生成5をJaCoCo数値へ加算0。fixtureはown JDK interfaces proxyでproduction reflectionなし、未知API/SQL/列名/型/Connection制御はassert失敗、rollback/retryを正常化せず呼出0。

新10/必要既80→当90PT11suite/全22Java・実19＋metadata1予定。原run7462/独立7464/六正常compile7466/全Jar7468/trace7470/review7472をsource固定で実施、環境/command/日時/branch/commit/exit/XML/input/output/coverage/static/BUG/hashは原manifestと結果へ。未実装TDD初失敗は障害でないが実装違反は修正前起票。開始3/5/9pp上限10・原-v4-v5固定、元製造新10/既80再資格/tool費を分離。whole451/正式1964-53/原190新受入0/工数null/QA051final/PTALT0/actualHOLD不変更。
