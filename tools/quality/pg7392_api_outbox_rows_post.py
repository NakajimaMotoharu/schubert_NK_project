"""Independent current64 exact ordinary cases/fifteen executable API classes."""
import pg7378_api_operation_mismatch_post as previous
import pg7390_api_outbox_rows_host as host

METHODS={
 'outboxMetric001DebugHasThreeCanonicalUnknownSeries',
 'outboxMetric002LiteralCountValuesAndImmutableSnapshotMatchSdk',
 'outboxMetric003TrueZeroAndMissingStayDistinctAndRecover',
 'outboxMetric004StandardDoesNotRegisterOrRetainAndStillRejectsNull',
 'outboxMetric005InvalidBoundariesCannotEchoOrWrapMaximumValues',
 'outboxMetric006ParallelSnapshotsRemainCompleteAndImmutable',
 'outboxMetric007PartialRegistrationFailureKeepsIdentityAndCallerOwnership',
 'outboxMetric008OwnersAndRepeatedValuesCannotShareOrGrowSeries'}

if __name__=='__main__':
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7390-api-outbox-rows-host-v1'
    post.OUT=post.host.BASE/'PG7392-api-outbox-rows-post-v1'
    post.PRIVATE=post.host.W/'pg7392-api-outbox-rows-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+n for n in ('OutboxRowsMetricRecorder','OutboxRowsMetricRecorder$Counts','OutboxRowsMetricRecorder$Status')}
    post.EXPECTED_SUITES[host.SUITES[7]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=64;post.SOURCE_FILE_COUNT=17
    post.main()
