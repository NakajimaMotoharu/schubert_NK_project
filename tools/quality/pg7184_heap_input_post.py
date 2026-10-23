"""All current100 exact cases/24 executable classes, no mixed-source coverage."""
import pg7066_timed_filesystem_post as previous
import pg7086_registry_missing_post as missing
import pg7154_filesystem_health_post as health
import pg7168_observation_clock_post as clock
import pg7182_heap_input_host as host

METHODS={'heapInput001FixedHeapTableAndBindingPerformOnlyOneReadPerSample',
 'heapInput002UnknownMaximumNeverFallsBackToCommittedOrInventsZero',
 'heapInput003RatioBoundaryRejectsInvalidCountsRatherThanClamping',
 'heapInput004OneByteBoundaryHasIndependentIeeeExpectedValues',
 'heapInput005LargestAndSingleByteMaximaDoNotOverflow',
 'heapInput006NullBoundaryNeverBecomesValidZeroAndBindingIsBorrowed',
 'heapInput007AllProviderFailuresKeepIdentityWithoutFormattingOrRetry',
 'heapInput008ManyBindingsDoNotReadOrMutateAndConcurrentReadsAreExact',
 'heapInput009HeapSnapshotIsIndependentOfCommittedAndLaterProviderValues'}


if __name__=='__main__':
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7182-heap-input-host-v1'
    post.OUT=post.host.BASE/'PG7184-heap-input-post-v1'
    post.PRIVATE=post.host.W/'pg7184-heap-input-post-v1'
    post.METHODS|=missing.METHODS|health.METHODS|clock.METHODS|METHODS
    post.NAMES|={post.PREFIX+n for n in ('FilesystemHealthObservation','FilesystemHealthMonitor','MonitoringObservationClock',
                                       'HealthUsageRatio','JvmHeapHealthObservation')}
    post.EXPECTED_SUITES={name:dict(tests=count,failures=0,errors=0,skipped=0)
                         for name,count in zip(host.SUITES,(7,6,10,4,14,7,6,8,2,6,3,10,8,9),strict=True)}
    post.TOTAL_TESTS=100;post.SOURCE_FILE_COUNT=30
    post.main()
