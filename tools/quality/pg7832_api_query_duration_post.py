"""Independent138/17/API28 exact XML/CRC/four counters/static on fixed source."""
import pg7692_mq_pressure_connection_post as previous
import pg7830_api_query_duration_host as host

METHODS={
 'dbTime001ExactlyFourFixedSeriesRequestHistogramSecondsAndFiveObservationBuckets',
 'dbTime002IndependentSecondsHistogramCdfAndTwoMaximumSamplesNeverLongWrap',
 'dbTime003QueryAndOutcomeClosedParsersAndGeneratedFactoriesUseIndependentTypedConstants',
 'dbTime004NullNegativeAndUnknownModeNeverRecordAndStandardStoresNoDetailedSamples',
 'dbTime005PartialFactoryFailurePreservesOriginalProblemAndCallerRegistryOwnership',
 'dbTime006FailureBeforeOrAfterSampleNeverRetriesCompensatesOrNormalizesSuccess',
 'dbTime007ConcurrentSampleCountSumAndMaximumUsePrecomputedIntegerInputs',
 'dbTime008ForeignCounterCannotBeReplacedBySummaryOrClosed'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7830-api-query-duration-host-v1'
    post.OUT=post.host.BASE/'PG7832-api-query-duration-post-v1'
    post.PRIVATE=post.host.W/'pg7832-api-query-duration-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'DbQueryDurationMetricRecorder',post.PREFIX+'DbQueryDurationMetricRecorder$Query',post.PREFIX+'DbQueryDurationMetricRecorder$Outcome'}
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=138;post.SOURCE_FILE_COUNT=34
    return post

if __name__=='__main__':
    host.dependency.verify_inputs()
    configure().main()
