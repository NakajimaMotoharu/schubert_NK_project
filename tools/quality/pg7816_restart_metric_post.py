"""Independent261/34/current65 with explicit original Repository dependency, four counters/static."""
import pg7790_integrity_metric_post as previous
import pg7814_restart_metric_host as host

METHODS={
 'restartMetric001TwentyFourCanonicalServiceSeriesStartAtZero',
 'restartMetric002EachSuppliedRestartIncrementsOnlyItsPairOnce',
 'restartMetric003ClosedReasonParserAndGeneratedFactoriesUseTypedLiteralOracles',
 'restartMetric004BothModesRejectNullAndStandardKeepsNoDetailedState',
 'restartMetric005PartialFactoryFailureKeepsPrefixAndOriginalProblem',
 'restartMetric006IncrementFailureNeverRetriesCompensatesOrNormalizesSuccess',
 'restartMetric007ConcurrentTotalsComeFromPrecomputedInputsAndOwnersStaySeparate',
 'restartMetric008ForeignGaugeCannotBeReplacedOrClosed'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7814-restart-metric-host-v1'
    post.OUT=post.host.BASE/'PG7816-restart-metric-post-v1'
    post.PRIVATE=post.host.W/'pg7816-restart-metric-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'ProcessRestartMetricRecorder',post.PREFIX+'ProcessRestartMetricRecorder$Reason'}
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=261;post.SOURCE_FILE_COUNT=69
    return post

if __name__=='__main__':configure().main()
