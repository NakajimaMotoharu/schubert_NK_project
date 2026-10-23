"""Actual108 cases/all26 executable classes, positive exact counters and same source/static scope."""
import pg7066_timed_filesystem_post as previous
import pg7086_registry_missing_post as missing
import pg7154_filesystem_health_post as health
import pg7168_observation_clock_post as clock
import pg7184_heap_input_post as heap
import pg7196_timed_heap_host as host

METHODS={'heapTime001WarningNeedsTenMinutesAndFiveNormalMinutesToClose',
 'heapTime002NinetyIsImmediateAndCriticalNeedsCauseAndTenMinutes',
 'heapTime003UnknownBreaksBothViolationAndRecoveryWithoutInventingNormal',
 'heapTime004ReportedOomIsIndependentOfMissingUsageAndNeverInventsZero',
 'heapTime005NullInvalidAndBackwardsInputsNeverMutateState',
 'heapTime006ExplicitGapRestartsViolationAndNormalRecovery',
 'heapTime007ConcurrentSameEpochKeepsOneEventAndImmutableSnapshot',
 'heapTime008CriticalIsStickyAcrossWarningAndReportedOomResetsRecovery'}


if __name__=='__main__':
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7196-timed-heap-host-v1'
    post.OUT=post.host.BASE/'PG7198-timed-heap-post-v1'
    post.PRIVATE=post.host.W/'pg7198-timed-heap-post-v1'
    post.METHODS|=missing.METHODS|health.METHODS|clock.METHODS|heap.METHODS|METHODS
    post.NAMES|={post.PREFIX+n for n in ('FilesystemHealthObservation','FilesystemHealthMonitor','MonitoringObservationClock',
                                       'HealthUsageRatio','JvmHeapHealthObservation','TimedJvmHeapMonitor','TimedJvmHeapMonitor$Evaluation')}
    post.EXPECTED_SUITES={name:dict(tests=count,failures=0,errors=0,skipped=0)
                         for name,count in zip(host.SUITES,(7,6,10,4,14,7,6,8,2,6,3,10,8,9,8),strict=True)}
    post.TOTAL_TESTS=108;post.SOURCE_FILE_COUNT=32
    post.main()
