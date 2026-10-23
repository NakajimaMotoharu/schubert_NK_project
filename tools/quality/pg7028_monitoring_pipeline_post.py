"""Exact original48 cases/14 executable classes and independent CRC/session/counters."""
import pg7008_monitoring_mode_post as post
import pg7014_metric_catalog_post as catalog
import pg7020_alert_lifecycle_post as state
import pg7024_alert_thresholds_post as threshold
import pg7026_monitoring_pipeline_host as host

METHODS = {
 'monPipe001ObservationContextInvariantsAndImmutableValues','monPipe002EveryNormalAndWarningEndpointIdentity',
 'monPipe003EveryCriticalEndpointAndCauseAwareRecovery','monPipe004RejectedInputsDoNotPartiallyUpdateState',
 'monPipe005ModeConsistencyDoesNotChangeAlerts','monPipe006ConcurrentSingleEntryKeepsOneOwner',
 'monPipe007AllSeventyTwoFixedKeysAndImmutableProjection'}


if __name__ == '__main__':
    post.SLOT = host.SLOT
    post.RUN = 'PG7026-monitoring-pipeline-host-v1'
    post.OUT = post.host.BASE/'PG7028-monitoring-pipeline-post-v1'
    post.PRIVATE = post.host.W/'pg7028-monitoring-pipeline-post-v1'
    post.NAMES = {post.PREFIX+n for n in (
      'MonitoringModePolicy','MonitoringModePolicy$DetailService','MetricContract','MetricContract$Kind',
      'AlertLifecycle','AlertLifecycle$Condition','AlertLifecycle$Service','AlertLifecycle$Severity',
      'AlertLifecycle$CauseClearance','AlertLifecycle$Event','AlertRegistry','AlertThresholds',
      'ObservationContext','MonitoringPolicyEngine')}
    post.METHODS = post.METHODS | catalog.METHODS | state.METHODS | threshold.METHODS | METHODS
    post.EXPECTED_SUITES = {name:dict(tests=count,failures=0,errors=0,skipped=0)
                           for name,count in zip(host.SUITES,(7,6,10,4,14,7),strict=True)}
    post.TOTAL_TESTS = 48
    post.SOURCE_FILE_COUNT = 14
    post.main()
