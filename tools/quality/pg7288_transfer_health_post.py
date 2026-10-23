"""Independent169 cases/all42 current executable classes, no real transfer or admission control."""
import pg7268_transfer_metric_post as previous
import pg7286_transfer_health_host as host

METHODS={
 'transferConn001DebugUsesExactCountsMetricsAndSameImmutableInput',
 'transferConn002WarningBytesAndFilesHaveIndependentExactBoundaries',
 'transferConn003CriticalPromotesSameEventAndRemainsStickyAtWarningValues',
 'transferConn004UnknownClearsGaugesWithoutNormalizingOrClosingEvent',
 'transferConn005ExplicitGapRestartsCriticalRecoveryWithoutIncrement',
 'transferConn006StandardStillMaintainsWarningCriticalAndCauseRecovery',
 'transferConn007InvalidInputsAndProviderFailuresPreserveOwnerAndCurrentValues',
 'transferConn008ConcurrentOneOwnerHasExactCountAndImmutableOldSnapshot'}

if __name__=='__main__':
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7286-transfer-health-host-v1'
    post.OUT=post.host.BASE/'PG7288-transfer-health-post-v1'
    post.PRIVATE=post.host.W/'pg7288-transfer-health-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'TransferHealthMonitor',post.PREFIX+'TransferHealthMonitor$Evaluation'}
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=169;post.SOURCE_FILE_COUNT=48
    post.main()
