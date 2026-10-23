"""Independent current56 exact ordinary cases/twelve executable API classes, no historical union."""
import pg7364_api_pool_observation_post as previous
import pg7376_api_operation_mismatch_host as host

METHODS={
 'opMis001DebugHasExactlyEightCanonicalZeroCounters',
 'opMis002EachObservationIncrementsOnlyItsCanonicalCounterOnce',
 'opMis003StandardHasNoDetailedRegistrationOrIncrement',
 'opMis004NullUnknownAndAliasedBoundariesCannotBecomeSeriesOrDiagnosticValues',
 'opMis005PartialRegistrationFailureKeepsIdentityAndRegistryOwnership',
 'opMis006IncrementFailuresAreNeverRetriedOrCompensated',
 'opMis007ParallelObservationsHaveExactCountsWithoutCardinalityGrowth',
 'opMis008IndependentOwnersAndRepeatedObservationsDoNotShareCounts'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7376-api-operation-mismatch-host-v1'
    post.OUT=post.host.BASE/'PG7378-api-operation-mismatch-post-v1'
    post.PRIVATE=post.host.W/'pg7378-api-operation-mismatch-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+n for n in ('OperationMismatchMetricRecorder','OperationMismatchMetricRecorder$Operation')}
    post.EXPECTED_SUITES[host.SUITES[6]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=56;post.SOURCE_FILE_COUNT=15
    return post

if __name__=='__main__':
    configure().main()
