"""Independent140 actual methods/all32 executable classes, not real p95 measurement."""
import pg7066_timed_filesystem_post as previous
import pg7086_registry_missing_post as missing
import pg7154_filesystem_health_post as health
import pg7168_observation_clock_post as clock
import pg7184_heap_input_post as heap
import pg7198_timed_heap_post as timed
import pg7212_heap_connection_post as connection
import pg7226_db_pool_post as pool
import pg7238_sync_p95_host as host

METHODS={
 'syncTime001StrictTwoSecondWarningNeedsFiveMinutes',
 'syncTime002StrictTwoPointFiveNeedsFiveMinutesBeforeCriticalPromotion',
 'syncTime003UnknownCutsBothViolationWindowsRatherThanBecomingZero',
 'syncTime004UnknownCutsCriticalRecoveryAndCauseMustBeConfirmed',
 'syncTime005NullInvalidAndBackwardsInputsCannotMutateExistingState',
 'syncTime006ExplicitGapRestartsViolationAndRecoveryWithStickyCritical',
 'syncTime007ConcurrentSameEpochMaintainsExactImmutableEventCounts',
 'syncTime008FiniteMaximumAndWarningRecoveryDoNotMixSeparateOwners'}

if __name__=='__main__':
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7238-sync-p95-host-v1'
    post.OUT=post.host.BASE/'PG7240-sync-p95-post-v1'
    post.PRIVATE=post.host.W/'pg7240-sync-p95-post-v1'
    post.METHODS|=missing.METHODS|health.METHODS|clock.METHODS|heap.METHODS|timed.METHODS|connection.METHODS|pool.METHODS|METHODS
    post.NAMES|={post.PREFIX+n for n in ('FilesystemHealthObservation','FilesystemHealthMonitor','MonitoringObservationClock',
        'HealthUsageRatio','JvmHeapHealthObservation','TimedJvmHeapMonitor','TimedJvmHeapMonitor$Evaluation',
        'MonitoringPoller','JvmHeapHealthMonitor','TimedDbPoolMonitor','TimedDbPoolMonitor$Evaluation',
        'TimedSyncLatencyMonitor','TimedSyncLatencyMonitor$Evaluation')}
    post.EXPECTED_SUITES={name:dict(tests=count,failures=0,errors=0,skipped=0)
        for name,count in zip(host.SUITES,(7,6,10,4,14,7,6,8,2,6,3,10,8,9,8,8,8,8,8),strict=True)}
    post.TOTAL_TESTS=140;post.SOURCE_FILE_COUNT=40
    post.main()
