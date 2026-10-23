"""Independent237/31 and positive59 classes/current source/single session/CRC/four counters."""
import pg7596_integrity_health_post as previous
import pg7610_dlq_health_host as host

METHODS={
 'dlqMon001KnownEmptyAndUnknownRemainDistinctWithoutInventingEvents',
 'dlqMon002CoherentEntryMatrixUsesIndependentSeverityAndAllServiceKeys',
 'dlqMon003NormalEvenConfirmedCannotAutoCloseWarningOrCritical',
 'dlqMon004UnknownGapAndEscalationPreserveExactHistoricalEvents',
 'dlqMon005NullNegativeIncoherentAndReversedInputsCannotMutateEvent',
 'dlqMon006ConcurrentSameOwnerAndSeparateOwnerKeepExactCounts',
 'dlqMon007ObservationGeneratedContractsUseIndependentLongAndBooleanOracles',
 'dlqMon008EvaluationGeneratedContractsUseIndependentBooleanAndIdentityOracles'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7610-dlq-health-host-v1'
    post.OUT=post.host.BASE/'PG7612-dlq-health-post-v1'
    post.PRIVATE=post.host.W/'pg7612-dlq-health-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'DlqHealthMonitor',post.PREFIX+'DlqHealthMonitor$Observation',post.PREFIX+'DlqHealthMonitor$Evaluation'}
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=237;post.SOURCE_FILE_COUNT=63
    return post

if __name__=='__main__':configure().main()
