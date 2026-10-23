"""Exact original41 cases/12 executable classes, independent original CRC/session/counters."""
import pg7008_monitoring_mode_post as post
import pg7014_metric_catalog_post as catalog
import pg7020_alert_lifecycle_post as state
import pg7022_alert_thresholds_host as host

METHODS = {
 'threshold001FilesystemPercentAndDwellBoundaries','threshold002TransferBytesFilesAndOrBoundaries',
 'threshold003AsyncCountRatioAndNoOverflow','threshold004WebLogCountAndOldestAge',
 'threshold005DlqNonemptyInvestigationAndGrowth','threshold006ExpiryCountBoundaries',
 'threshold007PoolUtilizationPendingAndTimeout','threshold008HeapPercentDwellAndOutOfMemory',
 'threshold009StrictP95AndFiveMinuteDwell','threshold010BackupScheduleSuccessAndConsecutiveFailures',
 'threshold011RestartWindowBoundaries','threshold012IntegrityNeverWarnsOrAutomaticallyRepairs',
 'threshold013InvalidInputsNeverBecomeNormal','threshold014ConcurrentStatelessEvaluations'}


if __name__ == '__main__':
    post.SLOT = host.SLOT
    post.RUN = 'PG7022-alert-thresholds-host-v1'
    post.OUT = post.host.BASE/'PG7024-alert-thresholds-post-v1'
    post.PRIVATE = post.host.W/'pg7024-alert-thresholds-post-v1'
    post.NAMES = {post.PREFIX+n for n in (
      'MonitoringModePolicy','MonitoringModePolicy$DetailService','MetricContract','MetricContract$Kind',
      'AlertLifecycle','AlertLifecycle$Condition','AlertLifecycle$Service','AlertLifecycle$Severity',
      'AlertLifecycle$CauseClearance','AlertLifecycle$Event','AlertRegistry','AlertThresholds')}
    post.METHODS = post.METHODS | catalog.METHODS | state.METHODS | METHODS
    post.EXPECTED_SUITES = {name:dict(tests=count,failures=0,errors=0,skipped=0)
                           for name,count in zip(host.SUITES,(7,6,10,4,14),strict=True)}
    post.TOTAL_TESTS = 41
    post.SOURCE_FILE_COUNT = 11
    post.main()
