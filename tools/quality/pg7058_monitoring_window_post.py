"""Original62 cases/17 executable classes, independent same-run CRC and all counters."""
import pg7008_monitoring_mode_post as post
import pg7046_monitoring_status_post as status
import pg7056_monitoring_window_host as host

METHODS={
 'monWindow001FirstContinuousAndSameTimestampBoundaries','monWindow002NormalBreaksViolationHistory',
 'monWindow003UnknownIsAbsentAndBreaksHistory','monWindow004ExplicitGapNeverBridgesOldPeriod',
 'monWindow005RejectedSequenceLeavesStateUnchanged','monWindow006WholeNonnegativeDurationDomain',
 'monWindow007ConcurrentSamePointHasOneOrigin',
 'monWindow008SeparateThresholdPeriodsConnectWithoutActualObservations'}


if __name__=='__main__':
    post.SLOT=host.SLOT
    post.RUN='PG7056-monitoring-window-host-v1'
    post.OUT=post.host.BASE/'PG7058-monitoring-window-post-v1'
    post.PRIVATE=post.host.W/'pg7058-monitoring-window-post-v1'
    post.NAMES={post.PREFIX+n for n in (
      'MonitoringModePolicy','MonitoringModePolicy$DetailService','MetricContract','MetricContract$Kind',
      'AlertLifecycle','AlertLifecycle$Condition','AlertLifecycle$Service','AlertLifecycle$Severity',
      'AlertLifecycle$CauseClearance','AlertLifecycle$Event','AlertRegistry','AlertThresholds',
      'ObservationContext','MonitoringPolicyEngine','MonitoringStatusText',
      'ContinuousConditionWindow','ContinuousConditionWindow$State')}
    post.METHODS=post.METHODS|status.catalog.METHODS|status.state.METHODS|status.threshold.METHODS|status.pipeline.METHODS|status.METHODS|METHODS
    post.EXPECTED_SUITES={name:dict(tests=count,failures=0,errors=0,skipped=0)
                         for name,count in zip(host.SUITES,(7,6,10,4,14,7,6,8),strict=True)}
    post.TOTAL_TESTS=62
    post.SOURCE_FILE_COUNT=18
    post.main()
