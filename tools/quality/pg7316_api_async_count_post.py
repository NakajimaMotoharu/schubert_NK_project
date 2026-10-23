"""Independent sixteen cases/four executable API metric classes, current source only."""
import pg7302_api_async_metric_post as previous
import pg7314_api_async_count_host as host

METHODS={
 'asyncDb001ShuffledFiveRowsHaveIndependentCountsAndBorrowedOwnership',
 'asyncDb002EmptyAndSparseGroupsAreKnownZeroOnlyAfterSuccessfulQuery',
 'asyncDb003NullOrWrongTransactionCannotPrepareOrMutateConnection',
 'asyncDb004NullUnknownNegativeAndDuplicateRowsCannotPublishPartialCounts',
 'asyncDb005MaximumLongIsExactAndTotalOverflowCannotWrap',
 'asyncDb006NullResourcesAndPreparationFaultsPreserveOriginalFailureWithoutRetry',
 'asyncDb007ReadAndCloseFaultsKeepIdentityAndSuppressionWithoutCauseTraversal',
 'asyncDb008ParallelBorrowedConnectionsHaveNoCrossOwnerState'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7314-api-async-count-host-v1'
    post.OUT=post.host.BASE/'PG7316-api-async-count-post-v1'
    post.PRIVATE=post.host.W/'pg7316-api-async-count-post-v1'
    post.METHODS=previous.METHODS|METHODS
    post.NAMES|={post.PREFIX+'persistence/AsyncJobCountRepository'}
    post.EXPECTED_SUITES[host.SUITES[1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=16;post.SOURCE_FILE_COUNT=5
    return post

if __name__=='__main__':
    configure().main()
