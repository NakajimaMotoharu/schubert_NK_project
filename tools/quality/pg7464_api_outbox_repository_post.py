"""Independent90/11 actual suites/current19 executable classes with fixed source/CRC/session."""
import pg7450_api_outbox_age_post as previous
import pg7462_api_outbox_repository_host as host

METHODS={
 'outboxDb001ShuffledRowsHaveLiteralCountsAndAgesAfterReverseClose',
 'outboxDb002EmptyAndSparseGroupsAreZeroOnlyAfterQueryCompletes',
 'outboxDb003NullAndWrongTransactionNeverPrepareOrMutateBorrowedConnection',
 'outboxDb004NullUnknownAndDuplicateStatusCannotReturnPartialValues',
 'outboxDb005NullNonpositiveCountAndNullOrFutureTimeAreNotKnownZero',
 'outboxDb006TypedOffsetTimeHasExactUtcAndCalendarBoundaryOracles',
 'outboxDb007NullResourcesAndAcquisitionFailuresNeverRetryOrCloseConnection',
 'outboxDb008ReadAndCloseFailuresPreserveOriginalIdentityAndSuppressedOrder',
 'outboxDb009ParallelBorrowedConnectionsHaveNoCrossOwnerState',
 'outboxDb010SnapshotInvariantsAndGeneratedContractsUseIndependentFixedValues'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7462-api-outbox-repository-host-v1'
    post.OUT=post.host.BASE/'PG7464-api-outbox-repository-post-v1'
    post.PRIVATE=post.host.W/'pg7464-api-outbox-repository-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'persistence/OutboxObservationRepository',post.PREFIX+'persistence/OutboxObservationRepository$Snapshot'}
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=10,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=90;post.SOURCE_FILE_COUNT=22
    return post

if __name__=='__main__':configure().main()
