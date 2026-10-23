"""Independent124-case/28-executable qualification for shared poll and heap connection."""
import pg7066_timed_filesystem_post as previous
import pg7086_registry_missing_post as missing
import pg7154_filesystem_health_post as health
import pg7168_observation_clock_post as clock
import pg7184_heap_input_post as heap
import pg7198_timed_heap_post as timed
import pg7210_heap_connection_host as host

METHODS={
 'poll001NormalFlagsContextAndResultHaveNoRetries',
 'poll002EveryUncheckedFailureRemainsIdenticalAndCutsNextContinuity',
 'poll003BackwardsContextIsRejectedBeforeActionAndDoesNotInventGap',
 'poll004ClockFailureHasNoActionAndCrossApiGapIsConsumed',
 'poll005NullBoundariesDoNotCallOrChangeContinuity',
 'poll006NullResultIsFailureAndDoesNotCommitLaterEpoch',
 'poll007ParallelNonAtomicActionsAreSerializedIntoOneToSixtyFour',
 'poll008ActionFailureThenClockPathRecoversAfterOneGapOnly',
 'heapConn001BeanClockAndKernelNeedExactlyTenWarningMinutes',
 'heapConn002UnknownMaximumBreaksCriticalNormalRecovery',
 'heapConn003GetterFailureIsNotRetriedOrConvertedAndBreaksRecovery',
 'heapConn004ClockFailureOrNullNeverReadsBeanAndCrossApiRecoveryHasGap',
 'heapConn005ExplicitOomReportWithUnknownUsageIsCriticalNotInventedZero',
 'heapConn006NullAndBackwardsBoundariesHaveNoProviderOrStateMutation',
 'heapConn007SeparateOwnersDoNotShareBeansOrAlertState',
 'heapConn008ConcurrentInputsHaveExactReadsAndImmutableCountSnapshots'}

if __name__=='__main__':
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7210-heap-connection-host-v1'
    post.OUT=post.host.BASE/'PG7212-heap-connection-post-v1'
    post.PRIVATE=post.host.W/'pg7212-heap-connection-post-v1'
    post.METHODS|=missing.METHODS|health.METHODS|clock.METHODS|heap.METHODS|timed.METHODS|METHODS
    post.NAMES|={post.PREFIX+n for n in ('FilesystemHealthObservation','FilesystemHealthMonitor','MonitoringObservationClock',
        'HealthUsageRatio','JvmHeapHealthObservation','TimedJvmHeapMonitor','TimedJvmHeapMonitor$Evaluation',
        'MonitoringPoller','JvmHeapHealthMonitor')}
    post.EXPECTED_SUITES={name:dict(tests=count,failures=0,errors=0,skipped=0)
        for name,count in zip(host.SUITES,(7,6,10,4,14,7,6,8,2,6,3,10,8,9,8,8,8),strict=True)}
    post.TOTAL_TESTS=124;post.SOURCE_FILE_COUNT=36
    post.main()
