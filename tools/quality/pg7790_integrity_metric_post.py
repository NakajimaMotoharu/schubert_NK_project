"""Independent253/33/current62 executables, exact XML/session/CRC/four counters and static."""
import pg7712_observed_retention_post as previous
import pg7802_integrity_metric_host_v2 as host
import copy
import pg7806_integrity_dependency_component_post as complete

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
    baseline=previous.configure()
    for key in ('PREFIX','NAMES','METHODS','EXPECTED_SUITES','TOTAL_TESTS','SOURCE_FILE_COUNT',
                'SOURCE_ROOT_PREFIX','EXTRA_AUXILIARY_JARS','EXTRA_PRODUCTION_DEPENDENCY_JARS'):
        setattr(complete,key,copy.deepcopy(getattr(baseline,key)))
    post=complete
    post.SLOT=host.SLOT;post.RUN='PG7802-integrity-metric-host-v2'
    post.OUT=post.host.BASE/'PG7790-integrity-metric-post-v1'
    post.PRIVATE=post.host.W/'pg7790-integrity-metric-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'IntegrityFailureMetricRecorder',post.PREFIX+'IntegrityFailureMetricRecorder$Area'}
    post.NAMES.add('dev/codex/schubert/nk/batch/repository/BatchStep')
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=253;post.SOURCE_FILE_COUNT=67
    return post

if __name__=='__main__':configure().main()
