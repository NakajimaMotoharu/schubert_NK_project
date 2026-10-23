"""Independent253/33/current62 executables, exact XML/session/CRC/four counters and static."""
import pg7712_observed_retention_post as previous
import pg7788_integrity_metric_host as host

METHODS={
 'integrityMetric001ThirtyCanonicalBatchSeriesStartAtZero',
 'integrityMetric002EachSuppliedFailureIncrementsOnlyItsPairOnce',
 'integrityMetric003ClosedAreaParserAndGeneratedFactoriesUseTypedLiteralOracles',
 'integrityMetric004BothModesRejectNullAndStandardKeepsNoDetailedState',
 'integrityMetric005PartialFactoryFailureKeepsPrefixAndOriginalProblem',
 'integrityMetric006IncrementFailureNeverRetriesCompensatesOrNormalizesSuccess',
 'integrityMetric007ConcurrentTotalsComeFromPrecomputedInputsAndOwnersStaySeparate',
 'integrityMetric008ForeignGaugeCannotBeReplacedOrClosed'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7788-integrity-metric-host-v1'
    post.OUT=post.host.BASE/'PG7790-integrity-metric-post-v1'
    post.PRIVATE=post.host.W/'pg7790-integrity-metric-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'IntegrityFailureMetricRecorder',post.PREFIX+'IntegrityFailureMetricRecorder$Area'}
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=253;post.SOURCE_FILE_COUNT=66
    return post

if __name__=='__main__':configure().main()
