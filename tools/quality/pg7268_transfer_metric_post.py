"""Independent161 actual cases/all40 executable classes, immutable supplied counts only."""
import pg7066_timed_filesystem_post as previous
import pg7086_registry_missing_post as missing
import pg7154_filesystem_health_post as health
import pg7168_observation_clock_post as clock
import pg7184_heap_input_post as heap
import pg7198_timed_heap_post as timed
import pg7212_heap_connection_post as connection
import pg7226_db_pool_post as pool
import pg7240_sync_p95_post as latency
import pg7254_batch_metric_post as batch
import pg7266_transfer_metric_host as host
import pg7106_micrometer_http_host as sdk

METHODS={
 'transferMet001ActualDebugHasFourClosedUnknownGaugesAndBorrowedRegistry',
 'transferMet002LiteralCountsAndExactTotalsPreservePreviousSnapshot',
 'transferMet003RealZeroAndMissingAreDifferentAndRecoveryUsesNewValues',
 'transferMet004StandardDoesNotRegisterOrRetainDetailedValues',
 'transferMet005NullNegativeAndOverflowInputsCannotMutateExistingSnapshot',
 'transferMet006MaximumLongRemainsExactInSnapshotAndDoubleUsesGoldenRounding',
 'transferMet007ConcurrentAtomicSnapshotNeverMixesCohortsOrChangesOldValues',
 'transferMet008PartialRegistrationFailureAndSeparateOwnersKeepCallerOwnership'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7266-transfer-metric-host-v1'
    post.OUT=post.host.BASE/'PG7268-transfer-metric-post-v1'
    post.PRIVATE=post.host.W/'pg7268-transfer-metric-post-v1'
    post.EXTRA_AUXILIARY_JARS=sdk.SDK
    post.METHODS|=missing.METHODS|health.METHODS|clock.METHODS|heap.METHODS|timed.METHODS|connection.METHODS|pool.METHODS|latency.METHODS|batch.METHODS|METHODS
    post.NAMES|={post.PREFIX+n for n in ('FilesystemHealthObservation','FilesystemHealthMonitor','MonitoringObservationClock',
        'HealthUsageRatio','JvmHeapHealthObservation','TimedJvmHeapMonitor','TimedJvmHeapMonitor$Evaluation',
        'MonitoringPoller','JvmHeapHealthMonitor','TimedDbPoolMonitor','TimedDbPoolMonitor$Evaluation',
        'TimedSyncLatencyMonitor','TimedSyncLatencyMonitor$Evaluation','BatchMetricContract','BatchMetricContract$Step',
        'BatchMetricContract$Status','BatchMetricRecorder','TransferMetricRecorder','TransferMetricRecorder$Counts',
        'TransferMetricRecorder$Usage','TransferMetricRecorder$Suffix')}
    post.EXPECTED_SUITES={name:dict(tests=count,failures=0,errors=0,skipped=0)
        for name,count in zip(host.SUITES,(7,6,10,4,14,7,6,8,2,6,3,10,8,9,8,8,8,8,8,5,8,8),strict=True)}
    post.TOTAL_TESTS=161;post.SOURCE_FILE_COUNT=46
    return post

if __name__=='__main__':configure().main()
