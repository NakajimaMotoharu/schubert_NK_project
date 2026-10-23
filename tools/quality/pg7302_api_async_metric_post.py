"""Independent actual8 API methods/3 executable classes, distinct from historical Batch/Web."""
import pg7008_monitoring_mode_post as post
import pg7300_api_async_metric_host as host
import pg7106_micrometer_http_host as sdk

METHODS={
 'asyncGauge001ActualDebugHasFiveCanonicalUnknownGaugesAndBorrowedOwner',
 'asyncGauge002LiteralCountsRemainImmutableAndUnknownNamesCannotBecomeLabels',
 'asyncGauge003TrueZeroAndMissingAreDistinctAndKnownValuesRecover',
 'asyncGauge004StandardDoesNotRegisterOrRetainAndStillRejectsInvalidBoundaries',
 'asyncGauge005NullMissingAndNegativeCountsCannotChangeExistingSnapshot',
 'asyncGauge006MaximumLongIsExactInSnapshotAndOverflowCannotWrap',
 'asyncGauge007ParallelSnapshotsRemainCompleteWithoutCrossOwnerOrSeriesGrowth',
 'asyncGauge008PartialProviderFailureKeepsIdentityAndCallerOwnedRegistry'}

if __name__=='__main__':
    post.SLOT=host.SLOT;post.RUN='PG7300-api-async-metric-host-v1';post.POM=host.POM
    post.OUT=post.host.BASE/'PG7302-api-async-metric-post-v1'
    post.PRIVATE=post.host.W/'pg7302-api-async-metric-post-v1'
    post.PREFIX='dev/codex/schubert/nk/api/monitoring/'
    post.SOURCE_ROOT_PREFIX='src/schubert-nk-api/'
    post.EXTRA_AUXILIARY_JARS=sdk.SDK
    post.METHODS=METHODS
    post.NAMES={post.PREFIX+n for n in ('AsyncJobMetricRecorder','AsyncJobMetricRecorder$State','AsyncJobMetricRecorder$Snapshot')}
    post.EXPECTED_SUITES={host.SUITES[0]:dict(tests=8,failures=0,errors=0,skipped=0)}
    post.TOTAL_TESTS=8;post.SOURCE_FILE_COUNT=3
    post.main()
