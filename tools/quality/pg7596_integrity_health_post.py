"""Independent229/30 and positive56 classes/current source/one session/CRC/four counters."""
import pg7580_restart_health_post as previous
import pg7594_integrity_health_host as host

METHODS={
 'integrityMon001KnownZeroAndMissingDoNotInventOrConflateEvents',
 'integrityMon002OneOrMaximumFailureIsCriticalWithFixedIdentity',
 'integrityMon003NormalEvenConfirmedAndMaximumElapsedCannotAutoClose',
 'integrityMon004UnknownAndExplicitGapKeepOldEventAndNewViolationHistory',
 'integrityMon005NullNegativeAndReversedTimeRejectWithoutMutatingEvent',
 'integrityMon006EveryClosedServiceUsesItsOwnImmutableLogicalKey',
 'integrityMon007ConcurrentCallersKeepExactCountAndIndependentOwner',
 'integrityMon008GeneratedEvaluationUsesIndependentBooleanAndIdentityOracles'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7594-integrity-health-host-v1'
    post.OUT=post.host.BASE/'PG7596-integrity-health-post-v1'
    post.PRIVATE=post.host.W/'pg7596-integrity-health-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'IntegrityHealthMonitor',post.PREFIX+'IntegrityHealthMonitor$Evaluation'}
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=229;post.SOURCE_FILE_COUNT=61
    return post

if __name__=='__main__':configure().main()
