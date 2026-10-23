"""Current32 exact API cases/eight executable metric classes, no historical coverage union."""
import pg7330_api_async_collector_post as previous
import pg7348_api_pool_metric_host as host

METHODS={
 'poolMetric001DebugHasExactlyFourCanonicalUnknownSeries',
 'poolMetric002LiteralCountsAndIndependentGaugeValuesRemainExact',
 'poolMetric003MissingAndTrueZeroAreDistinctAndRecoverable',
 'poolMetric004StandardNeverRegistersOrRetainsAndStillRejectsNull',
 'poolMetric005NegativeMissingUnknownAndMaximumBoundariesDoNotWrap',
 'poolMetric006ParallelUpdatesKeepWholeImmutableSnapshots',
 'poolMetric007PartialProviderFailurePreservesIdentityAndBorrowedLifetime',
 'poolMetric008OwnersAndRepeatedObservationsCannotGrowLabelCardinality'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7348-api-pool-metric-host-v1'
    post.OUT=post.host.BASE/'PG7350-api-pool-metric-post-v1'
    post.PRIVATE=post.host.W/'pg7350-api-pool-metric-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+n for n in ('DbPoolMetricRecorder','DbPoolMetricRecorder$Counts','DbPoolMetricRecorder$State')}
    post.EXPECTED_SUITES[host.SUITES[3]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=32;post.SOURCE_FILE_COUNT=9
    return post

if __name__=='__main__':
    configure().main()
