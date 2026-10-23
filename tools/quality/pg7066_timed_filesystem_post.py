"""Original70 cases/19 executables, all real counters and single CRC/session proof."""
import pg7008_monitoring_mode_post as post
import pg7058_monitoring_window_post as window
import pg7064_timed_filesystem_host as host

METHODS={
 'alertContinuity001InvalidInterruptionHasNoStateChange',
 'alertContinuity002WarningAndCriticalRecoveryCannotBridgeGap',
 'timedFs001WarningBoundaryAndFiveMinuteRecovery','timedFs002CriticalBoundaryAndExplicitCause',
 'timedFs003MissingBreaksViolationWithoutClearingOpenEvent',
 'timedFs004MissingAndExplicitGapBreakNormalRecovery','timedFs005InvalidInputsCannotChangeOwnerState',
 'timedFs006ConcurrentOwnerAndLocalStatusLiteral'}


if __name__=='__main__':
    post.SLOT=host.SLOT
    post.RUN='PG7064-timed-filesystem-host-v1'
    post.OUT=post.host.BASE/'PG7066-timed-filesystem-post-v1'
    post.PRIVATE=post.host.W/'pg7066-timed-filesystem-post-v1'
    post.NAMES={post.PREFIX+n for n in (
      'MonitoringModePolicy','MonitoringModePolicy$DetailService','MetricContract','MetricContract$Kind',
      'AlertLifecycle','AlertLifecycle$Condition','AlertLifecycle$Service','AlertLifecycle$Severity',
      'AlertLifecycle$CauseClearance','AlertLifecycle$Event','AlertRegistry','AlertThresholds',
      'ObservationContext','MonitoringPolicyEngine','MonitoringStatusText',
      'ContinuousConditionWindow','ContinuousConditionWindow$State',
      'TimedFilesystemMonitor','TimedFilesystemMonitor$Evaluation')}
    status=window.status
    post.METHODS=post.METHODS|status.catalog.METHODS|status.state.METHODS|status.threshold.METHODS|status.pipeline.METHODS|status.METHODS|window.METHODS|METHODS
    post.EXPECTED_SUITES={name:dict(tests=count,failures=0,errors=0,skipped=0)
                         for name,count in zip(host.SUITES,(7,6,10,4,14,7,6,8,2,6),strict=True)}
    post.TOTAL_TESTS=70
    post.SOURCE_FILE_COUNT=21
    post.main()
