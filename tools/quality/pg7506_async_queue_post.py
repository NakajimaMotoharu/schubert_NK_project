"""Independent192/26 cases/current46 positive classes, exact source/CRC/session/four counters."""
import pg7492_web_log_backlog_post as previous
import pg7504_async_queue_host as host

METHODS={
 'asyncQueue001KnownNormalAndMissingRemainDifferentWithoutInventedEvents',
 'asyncQueue002ExactAbsoluteAndRatioBoundariesUseIndependentGoldenValues',
 'asyncQueue003UnknownAndPartialLowEvidenceBreakNormalRecoveryWithoutClosing',
 'asyncQueue004CriticalStaysStickyUntilTenNormalMinutesAndConfirmedCause',
 'asyncQueue005ExplicitGapCannotBridgeTheFiveMinuteNormalWindow',
 'asyncQueue006InvalidInputsAndReversedElapsedCannotMutatePriorEvent',
 'asyncQueue007ConcurrentSameOwnerAndIndependentOwnerHaveExactCounts',
 'asyncQueue008GeneratedEvaluationContractsHaveIndependentFieldAndPlatformOracles'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7504-async-queue-host-v1'
    post.OUT=post.host.BASE/'PG7506-async-queue-post-v1'
    post.PRIVATE=post.host.W/'pg7506-async-queue-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'AsyncQueueMonitor',post.PREFIX+'AsyncQueueMonitor$Evaluation'}
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=192;post.SOURCE_FILE_COUNT=53
    return post

if __name__=='__main__':configure().main()
