"""Original54 cases,15 executable classes, single real session and independent counters."""
import pg7008_monitoring_mode_post as post
import pg7014_metric_catalog_post as catalog
import pg7020_alert_lifecycle_post as state
import pg7024_alert_thresholds_post as threshold
import pg7028_monitoring_pipeline_post as pipeline
import pg7044_monitoring_status_host as host

METHODS = {
 'monStatus001EmptyModesHaveOnlySuppliedScopeAndColumns',
 'monStatus002LiteralSingleFrameAndNoRetainedCallerState',
 'monStatus003CanonicalOrderCountSeverityAndLastSeen',
 'monStatus004NullDuplicateClosedRejectedWithoutOwnerMutation',
 'monStatus005FullInstantBoundaryGoldenVectors',
 'monStatus006ConcurrentStatelessFormatting'}


if __name__ == '__main__':
    post.SLOT = host.SLOT
    post.RUN = 'PG7044-monitoring-status-host-v1'
    post.OUT = post.host.BASE/'PG7046-monitoring-status-post-v1'
    post.PRIVATE = post.host.W/'pg7046-monitoring-status-post-v1'
    post.NAMES = {post.PREFIX+n for n in (
      'MonitoringModePolicy','MonitoringModePolicy$DetailService','MetricContract','MetricContract$Kind',
      'AlertLifecycle','AlertLifecycle$Condition','AlertLifecycle$Service','AlertLifecycle$Severity',
      'AlertLifecycle$CauseClearance','AlertLifecycle$Event','AlertRegistry','AlertThresholds',
      'ObservationContext','MonitoringPolicyEngine','MonitoringStatusText')}
    post.METHODS = post.METHODS | catalog.METHODS | state.METHODS | threshold.METHODS | pipeline.METHODS | METHODS
    post.EXPECTED_SUITES = {name:dict(tests=count,failures=0,errors=0,skipped=0)
                           for name,count in zip(host.SUITES,(7,6,10,4,14,7,6),strict=True)}
    post.TOTAL_TESTS = 54
    post.SOURCE_FILE_COUNT = 16
    post.main()
